from typing import Optional
from urllib.parse import quote, unquote

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from loguru import logger

from src.task_manager.config.settings import settings
from src.task_manager.dto.chat_summary import Topic
from src.task_manager.handlers.task_states import TaskCreationStates
from src.task_manager.service.auth_service import AuthService
from src.task_manager.service.chat_summary_service import chat_summary_service
from src.task_manager.service.task_service import task_service
from src.task_manager.service.voice_transcription_service import (
    voice_transcription_service,
)

router = Router(name="task_handler")

MAX_CALLBACK_DATA_LENGTH = 64  # Ограничение Telegram API

# Заглушка для mock Jira — mock-сервис не проверяет Authorization
MOCK_JIRA_AUTH_TOKEN = "mock-local-demo"


async def _ensure_auth_token(
    *,
    state: FSMContext,
    bot,
    telegram_id: int,
) -> str | None:
    """
    Возвращает токен из FSM или получает новый.

    В режиме JIRA_USE_MOCK не обращается к IDM и не требует AUTH_LOGIN/AUTH_PASSWORD.
    """
    data = await state.get_data()
    token = data.get("auth_token")
    if token:
        return token

    if settings.jira_use_mock:
        await state.update_data(auth_token=MOCK_JIRA_AUTH_TOKEN)
        logger.info(
            f"Режим JIRA mock: токен-заглушка для пользователя {telegram_id} "
            "(AUTH_LOGIN/AUTH_PASSWORD не нужны)"
        )
        return MOCK_JIRA_AUTH_TOKEN

    if not settings.auth_login or not settings.auth_password:
        logger.error("Не заданы AUTH_LOGIN или AUTH_PASSWORD в переменных окружения")
        return None

    try:
        auth_service = AuthService(bot=bot)
        _, _, token = await auth_service.process_authorization(
            login=settings.auth_login,
            password=settings.auth_password,
            telegram_id=str(telegram_id),
        )
        if not token:
            logger.error(f"Не удалось получить токен для пользователя {telegram_id}")
            return None

        await state.update_data(auth_token=token)
        logger.info(f"Токен получен и сохранен в FSM для пользователя {telegram_id}")
        return token

    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}", exc_info=True)
        return None


async def _safe_edit_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> bool:
    """
    Безопасно редактирует сообщение с обработкой ошибок Telegram API.

    Args:
        message: Сообщение для редактирования
        text: Новый текст
        reply_markup: Опциональная клавиатура

    Returns:
        True если успешно, False если ошибка
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.debug(f"Сообщение не изменилось: {message.message_id}")
            return True
        logger.warning(f"Не удалось отредактировать сообщение {message.message_id}: {e}")
        try:
            await message.answer(text, reply_markup=reply_markup)
            return True
        except Exception as send_error:
            logger.error(f"Не удалось отправить новое сообщение: {send_error}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения {message.message_id}: {e}")
        return False


async def _create_task_and_notify(
    telegram_id: int,
    project_url: str,
    task_text: str,
    status_message: Message,
    state: FSMContext,
) -> None:
    """
    Создает задачу в Jira и отправляет уведомление пользователю.

    Args:
        telegram_id: ID пользователя Telegram
        project_url: URL проекта в Jira
        task_text: Текст задачи
        status_message: Сообщение для обновления статуса
        state: FSM контекст
    """
    try:
        # Получаем токен из состояния
        data = await state.get_data()
        token = data.get("auth_token")

        if not task_text or not task_text.strip():
            await _safe_edit_message(
                status_message,
                "Ошибка: текст задачи не может быть пустым.\n"
                "Попробуйте начать заново с команды /create_task",
            )
            await state.clear()
            return

        jira_task_url = await task_service.create_task(
            telegram_id=telegram_id, project_url=project_url, text=task_text, token=token
        )

        await _safe_edit_message(
            status_message,
            f"<b>Задача успешно создана!</b>\n\nСсылка: {jira_task_url}",
        )

        logger.info(f"Задача создана для пользователя {telegram_id}: {jira_task_url}")

    except Exception as e:
        logger.error(
            f"Ошибка при создании задачи для пользователя {telegram_id}: {e}",
            exc_info=True,
        )
        await _safe_edit_message(
            status_message,
            "Не удалось создать задачу.\n" "Попробуйте позже или обратитесь к администратору.",
        )
    finally:
        await state.clear()


def _extract_project_url(callback_data: str) -> Optional[str]:
    """
    Извлекает URL проекта из callback_data с обработкой ошибок.

    Args:
        callback_data: Данные callback

    Returns:
        URL проекта или None при ошибке
    """
    try:
        parts = callback_data.split("project:", 1)
        if len(parts) != 2:
            logger.error(f"Некорректный формат callback_data: {callback_data}")
            return None
        return unquote(parts[1])
    except Exception as e:
        logger.error(f"Ошибка при извлечении project_url из {callback_data}: {e}")
        return None


def _extract_topic_index(callback_data: str) -> Optional[int]:
    """
    Извлекает индекс темы из callback_data с обработкой ошибок.

    Args:
        callback_data: Данные callback

    Returns:
        Индекс темы или None при ошибке
    """
    try:
        parts = callback_data.split("topic:", 1)
        if len(parts) != 2:
            logger.error(f"Некорректный формат callback_data: {callback_data}")
            return None
        return int(parts[1])
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка при извлечении topic_index из {callback_data}: {e}")
        return None


@router.message(Command("create_task"))
async def cmd_create_task(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /create_task.
    """
    telegram_id = message.from_user.id
    logger.info(
        f"Пользователь {telegram_id} начал создание задачи в чате типа: {message.chat.type}"
    )

    is_private = message.chat.type == "private"
    project_selection_state = (
        TaskCreationStates.waiting_project_selection
        if is_private
        else TaskCreationStates.waiting_group_project_selection
    )

    token = await _ensure_auth_token(
        state=state,
        bot=message.bot,
        telegram_id=telegram_id,
    )
    if not token:
        if not settings.jira_use_mock and (
            not settings.auth_login or not settings.auth_password
        ):
            await message.answer(
                "Ошибка конфигурации: не заданы учетные данные для авторизации.\n"
                "Обратитесь к администратору."
            )
        else:
            await message.answer(
                "Не удалось авторизоваться. Попробуйте позже или обратитесь к администратору."
            )
        return

    try:
        projects = await task_service.get_available_projects(telegram_id, token)
        if not projects:
            await message.answer(
                "У вас нет доступных проектов в Jira.\n"
                "Обратитесь к администратору для получения доступа."
            )
            await state.clear()
            return

        # Создаем клавиатуру с проектами и кнопкой отмены внизу
        keyboard = _build_projects_keyboard(projects)

        if not keyboard.inline_keyboard:
            await message.answer(
                "Не удалось создать клавиатуру с проектами.\n"
                "Возможно, URL проектов слишком длинные.\n"
                "Обратитесь к администратору."
            )
            await state.clear()
            return

        cancel_keyboard = _build_cancel_keyboard()
        combined_buttons = keyboard.inline_keyboard + cancel_keyboard.inline_keyboard
        combined_keyboard = InlineKeyboardMarkup(inline_keyboard=combined_buttons)

        try:
            # В групповом чате отвечаем на сообщение пользователя (reply)
            # В приватном чате просто отправляем сообщение
            send_method = message.reply if not is_private else message.answer

            text = (
                "<b>Создание задачи в Jira</b>\n\n"
                "Выберите проект, в котором хотите создать задачу:"
            )

            await send_method(
                text=text,
                reply_markup=combined_keyboard,
            )
            await state.set_state(project_selection_state)
        except TelegramAPIError as e:
            logger.error(
                f"Ошибка Telegram API при отправке сообщения " f"пользователю {telegram_id}: {e}"
            )
            await message.answer(
                "Произошла ошибка при отправке сообщения.\n"
                "Попробуйте позже или обратитесь к администратору."
            )
            await state.clear()

    except Exception as e:
        logger.error(
            f"Ошибка при получении списка проектов для пользователя " f"{telegram_id}: {e}",
            exc_info=True,
        )
        try:
            await message.answer(
                "Произошла ошибка при получении списка проектов.\n"
                "Попробуйте позже или обратитесь к администратору."
            )
        except Exception as send_error:
            logger.error(
                f"Не удалось отправить сообщение об ошибке пользователю {telegram_id}: {send_error}"
            )
        finally:
            await state.clear()


@router.callback_query(
    TaskCreationStates.waiting_project_selection,
    F.data.startswith("project:"),
)
async def process_project_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора проекта для приватного чата.
    """
    telegram_id = callback.from_user.id
    project_url = _extract_project_url(callback.data)

    if not project_url:
        await callback.answer("Ошибка при выборе проекта. Попробуйте еще раз.", show_alert=True)
        return

    logger.info(f"Пользователь {telegram_id} выбрал проект: {project_url}")

    try:
        await state.update_data(project_url=project_url)
        cancel_keyboard = _build_cancel_keyboard()
        success = await _safe_edit_message(
            callback.message,
            "Проект выбран!\n\n"
            "Теперь отправьте текст задачи (можно голосовым сообщением).\n\n"
            "<i>Первая строка будет использована как заголовок задачи,\n"
            "весь текст - как описание.</i>",
            reply_markup=cancel_keyboard,
        )

        if success:
            await state.set_state(TaskCreationStates.waiting_task_text)
            await callback.answer()
        else:
            await callback.answer("Ошибка при обновлении сообщения.", show_alert=True)

    except Exception as e:
        logger.error(
            f"Ошибка при обработке выбора проекта для {telegram_id}: {e}",
            exc_info=True,
        )
        await callback.answer(
            "Произошла ошибка. Попробуйте позже.",
            show_alert=True,
        )
        await state.clear()


@router.callback_query(
    TaskCreationStates.waiting_group_project_selection,
    F.data.startswith("project:"),
)
async def process_group_project_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора проекта для группового чата.
    После выбора проекта предлагает выбрать тему обсуждения.
    """
    telegram_id = callback.from_user.id
    project_url = _extract_project_url(callback.data)

    if not project_url:
        await callback.answer("Ошибка при выборе проекта. Попробуйте еще раз.", show_alert=True)
        return

    logger.info(f"Пользователь {telegram_id} выбрал проект в групповом чате: " f"{project_url}")

    # Отвечаем на callback сразу, чтобы избежать таймаута
    await callback.answer("Обработка запроса...")

    try:
        await state.update_data(project_url=project_url)
        chat_id = callback.message.chat.id

        # Показываем сообщение о загрузке
        await _safe_edit_message(
            callback.message,
            "⏳ Анализ чата и извлечение тем...\n" "Это может занять некоторое время.",
        )

        topics = await chat_summary_service.get_topics(chat_id)

        if not topics:
            await _safe_edit_message(
                callback.message,
                "В этом чате пока нет обсуждаемых тем.\n"
                "Для создания задачи используйте приватный чат с ботом.",
            )
            await state.clear()
            return

        topics_dicts = [topic.model_dump() for topic in topics]
        await state.update_data(topics=topics_dicts)

        keyboard = _build_topics_keyboard(topics)
        cancel_keyboard = _build_cancel_keyboard()
        combined_buttons = keyboard.inline_keyboard + cancel_keyboard.inline_keyboard
        combined_keyboard = InlineKeyboardMarkup(inline_keyboard=combined_buttons)

        success = await _safe_edit_message(
            callback.message,
            "Проект выбран!\n\n" "Выберите тему обсуждения, по которой хотите создать задачу:",
            reply_markup=combined_keyboard,
        )

        if success:
            await state.set_state(TaskCreationStates.waiting_topic_selection)
        else:
            await _safe_edit_message(
                callback.message,
                "Ошибка при обновлении сообщения.\n" "Попробуйте еще раз.",
            )
            await state.clear()

    except Exception as e:
        logger.error(
            f"Ошибка при получении списка тем для пользователя " f"{telegram_id}: {e}",
            exc_info=True,
        )
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка при получении списка тем.\n"
            "Попробуйте позже или обратитесь к администратору.",
        )
        await state.clear()
        await callback.answer("Ошибка при получении тем")


@router.message(TaskCreationStates.waiting_task_text, F.text)
async def process_task_text(message: Message, state: FSMContext) -> None:
    """
    Обработчик текста задачи.
    """
    telegram_id = message.from_user.id

    if not message.text:
        logger.warning(f"Получено сообщение без текста от пользователя {telegram_id}")
        await message.answer("Пожалуйста, отправьте текстовое сообщение с описанием задачи.")
        return

    task_text = message.text.strip()

    logger.info(f"Пользователь {telegram_id} отправил текст задачи: " f"{task_text[:50]}...")

    data = await state.get_data()
    project_url = data.get("project_url")

    if not project_url:
        logger.error(f"Не найден project_url в FSM data для пользователя {telegram_id}")
        await message.answer("Произошла ошибка. Попробуйте начать заново с команды /create_task")
        await state.clear()
        return

    token = await _ensure_auth_token(
        state=state,
        bot=message.bot,
        telegram_id=telegram_id,
    )
    if not token:
        if not settings.jira_use_mock and (
            not settings.auth_login or not settings.auth_password
        ):
            await message.answer(
                "Ошибка конфигурации: не заданы учетные данные для авторизации.\n"
                "Обратитесь к администратору."
            )
        else:
            await message.answer(
                "Не удалось авторизоваться. Попробуйте позже или обратитесь к администратору."
            )
        await state.clear()
        return

    # Показываем превью задачи вместо немедленного создания
    success = await _show_task_preview(message, task_text, project_url, state)

    if not success:
        await message.answer(
            "Произошла ошибка при формировании превью задачи.\n"
            "Попробуйте начать заново с команды /create_task"
        )
        await state.clear()


@router.message(TaskCreationStates.waiting_task_text, F.voice)
async def process_voice_task(message: Message, state: FSMContext) -> None:
    """
    Обработчик голосового сообщения для описания задачи.
    """
    telegram_id = message.from_user.id

    logger.info(f"Пользователь {telegram_id} отправил голосовое сообщение для задачи")

    data = await state.get_data()
    project_url = data.get("project_url")

    if not project_url:
        logger.error(f"Не найден project_url в FSM data для пользователя {telegram_id}")
        await message.answer("Произошла ошибка. Попробуйте начать заново с команды /create_task")
        await state.clear()
        return

    # Отправляем сообщение о начале обработки
    status_msg = await message.answer("⏳ Обрабатываю голосовое сообщение...")

    try:
        bot = message.bot
        task_summary = await voice_transcription_service.create_task_summary(
            bot=bot, voice=message.voice
        )

        if not task_summary:
            await status_msg.edit_text(
                "❌ Не удалось распознать речь. "
                "Попробуйте записать сообщение четче или отправьте текстом."
            )
            return

        token = await _ensure_auth_token(
            state=state,
            bot=bot,
            telegram_id=telegram_id,
        )
        if not token:
            if not settings.jira_use_mock and (
                not settings.auth_login or not settings.auth_password
            ):
                await status_msg.edit_text(
                    "Ошибка конфигурации: не заданы учетные данные для авторизации.\n"
                    "Обратитесь к администратору."
                )
            else:
                await status_msg.edit_text(
                    "Не удалось авторизоваться. Попробуйте позже "
                    "или обратитесь к администратору."
                )
            await state.clear()
            return

        # Показываем превью задачи с транскрибированным текстом
        combined_text = (
            f"{task_summary.header}\n{task_summary.content}"
            if task_summary.content
            else task_summary.header
        )

        success = await _show_task_preview(message, combined_text, project_url, state)

        if success:
            await status_msg.edit_text(
                "✅ Голосовое сообщение распознано\n" "Проверьте превью задачи ниже."
            )
        else:
            await status_msg.edit_text(
                "Произошла ошибка при формировании превью задачи.\n"
                "Попробуйте начать заново с команды /create_task"
            )
            await state.clear()

    except Exception as e:
        logger.error(
            f"Ошибка при обработке голосового сообщения для пользователя {telegram_id}: {e}",
            exc_info=True,
        )
        await status_msg.edit_text(
            f"❌ Произошла ошибка при обработке голосового сообщения: {str(e)}\n\n"
            "Попробуйте отправить текстовое сообщение или попробуйте позже."
        )


@router.callback_query(
    TaskCreationStates.waiting_topic_selection,
    F.data.startswith("topic:"),
)
async def process_topic_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора темы для создания задачи из группового чата.
    """
    telegram_id = callback.from_user.id

    topic_index = _extract_topic_index(callback.data)

    if topic_index is None:
        await callback.answer(
            "Ошибка при выборе темы. Попробуйте еще раз.",
            show_alert=True,
        )
        await state.clear()
        return

    logger.info(f"Пользователь {telegram_id} выбрал тему с индексом: {topic_index}")

    data = await state.get_data()
    project_url = data.get("project_url")
    topics = data.get("topics", [])

    if not project_url:
        logger.error(f"Не найден project_url в FSM data для пользователя {telegram_id}")
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка. Попробуйте начать заново с команды /create_task",
        )
        await state.clear()
        await callback.answer("Ошибка")
        return

    if not topics or not isinstance(topics, list):
        logger.error(
            f"Темы не найдены или имеют неверный формат для " f"пользователя {telegram_id}"
        )
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка при получении тем. "
            "Попробуйте начать заново с команды "
            "/create_task",
        )
        await state.clear()
        await callback.answer("Ошибка")
        return

    if topic_index < 0 or topic_index >= len(topics):
        logger.error(
            f"Неверный индекс темы {topic_index} (всего тем: {len(topics)}) "
            f"для пользователя {telegram_id}"
        )
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка при выборе темы. " "Попробуйте начать заново с команды /create_task",
        )
        await state.clear()
        await callback.answer("Ошибка")
        return

    selected_topic = topics[topic_index]

    if not isinstance(selected_topic, dict):
        logger.error(
            f"Тема имеет неверный формат (ожидался dict, "
            f"получен {type(selected_topic)}) для пользователя {telegram_id}"
        )
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка при обработке темы. "
            "Попробуйте начать заново с команды /create_task",
        )
        await state.clear()
        await callback.answer("Ошибка")
        return

    topic_name = selected_topic.get("topic", "")

    text_for_task = selected_topic.get("text_for_task")

    if not topic_name:
        logger.error(f"Поле topic пустое для пользователя {telegram_id}")
        await _safe_edit_message(
            callback.message,
            "Выбранная тема содержит недостаточно информации. Попробуйте другую тему.",
        )
        await callback.answer("Ошибка")
        return

    if not text_for_task:
        logger.warning(
            f"Поле text_for_task не заполнено для темы '{topic_name}', "
            f"используется fallback для пользователя {telegram_id}"
        )
        summary = selected_topic.get("summary", "")
        resolution = selected_topic.get("resolution")

        if not summary:
            logger.error(f"Поле summary пустое для пользователя {telegram_id}")
            await _safe_edit_message(
                callback.message,
                "Выбранная тема содержит недостаточно информации. Попробуйте другую тему.",
            )
            await callback.answer("Ошибка")
            return

        text_for_task = summary
        if resolution:
            text_for_task += f"\n\nРешение: {resolution}"

    task_text = f"{topic_name}\n\n{text_for_task}"

    await callback.answer("Формирую превью задачи...")

    success = await _show_task_preview(callback.message, task_text, project_url, state)

    if success:
        await _safe_edit_message(callback.message, "Тема выбрана! Проверьте превью задачи ниже.")
    else:
        await _safe_edit_message(
            callback.message,
            "Произошла ошибка при формировании превью задачи.\n"
            "Попробуйте начать заново с команды /create_task",
        )
        await state.clear()


@router.callback_query(
    TaskCreationStates.waiting_task_confirmation,
    F.data == "confirm_task_creation",
)
async def confirm_task_creation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик подтверждения создания задачи.
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} подтвердил создание задачи")

    data = await state.get_data()
    project_url = data.get("project_url")
    task_text = data.get("task_text")

    if not project_url or not task_text:
        logger.error(f"Не найдены данные для создания задачи у пользователя {telegram_id}")
        await callback.answer("Ошибка: данные задачи потеряны", show_alert=True)
        await _safe_edit_message(
            callback.message, "Произошла ошибка. Попробуйте начать заново с команды /create_task"
        )
        await state.clear()
        return

    await _safe_edit_message(callback.message, "Создаю задачу в Jira...")
    await callback.answer()

    await _create_task_and_notify(
        telegram_id=telegram_id,
        project_url=project_url,
        task_text=task_text,
        status_message=callback.message,
        state=state,
    )


@router.callback_query(
    TaskCreationStates.waiting_project_selection,
    F.data == "cancel_task_creation",
)
@router.callback_query(
    TaskCreationStates.waiting_group_project_selection,
    F.data == "cancel_task_creation",
)
@router.callback_query(
    TaskCreationStates.waiting_topic_selection,
    F.data == "cancel_task_creation",
)
@router.callback_query(
    TaskCreationStates.waiting_task_text,
    F.data == "cancel_task_creation",
)
@router.callback_query(
    TaskCreationStates.waiting_task_confirmation,
    F.data == "cancel_task_creation",
)
async def cancel_task_creation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик отмены создания задачи на любом этапе.
    Работает как для личных сообщений, так и для групп/каналов.
    """
    telegram_id = callback.from_user.id
    logger.info(f"Пользователь {telegram_id} отменил создание задачи")
    await state.clear()
    await _safe_edit_message(
        callback.message,
        "Создание задачи отменено.\n\n"
        "Для создания новой задачи используйте команду /create_task",
    )
    await callback.answer("Создание задачи отменено")


def _build_projects_keyboard(projects: dict[str, str]) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру с проектами.

    Args:
        projects: Словарь проектов (название -> URL)

    Returns:
        InlineKeyboardMarkup с кнопками проектов
    """
    buttons = []

    for project_name, project_url in projects.items():
        encoded_url = quote(project_url, safe="")
        callback_data = f"project:{encoded_url}"

        # Проверяем длину callback_data (ограничение Telegram API - 64 байта)
        if len(callback_data.encode("utf-8")) > MAX_CALLBACK_DATA_LENGTH:
            logger.warning(
                f"Callback_data для проекта '{project_name}' слишком длинный "
                f"({len(callback_data)} байт), проект пропущен. "
                f"URL: {project_url}"
            )
            continue

        button = InlineKeyboardButton(
            text=project_name,
            callback_data=callback_data,
        )
        buttons.append([button])

    if not buttons:
        logger.error("Не удалось создать ни одной кнопки проекта " "из-за ограничений длины")
        # Возвращаем пустую клавиатуру - обработчик должен проверить это
        return InlineKeyboardMarkup(inline_keyboard=[])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _build_topics_keyboard(topics: list[Topic]) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру с темами обсуждений.

    Args:
        topics: Список тем (Topic objects)

    Returns:
        InlineKeyboardMarkup с кнопками тем
    """
    buttons = []

    for idx, topic in enumerate(topics):
        # Формируем текст кнопки: категория + название темы
        # (ограничиваем длину)
        category = getattr(topic, "category", "Без категории")
        topic_name = getattr(topic, "topic", "Без названия")
        button_text = f"[{category}] {topic_name}"
        if len(button_text) > 60:
            button_text = button_text[:57] + "..."

        callback_data = f"topic:{idx}"

        # Проверяем длину callback_data (хотя для индекса
        # это не должно быть проблемой)
        if len(callback_data.encode("utf-8")) > MAX_CALLBACK_DATA_LENGTH:
            logger.warning(
                f"Callback_data для темы {idx} слишком длинный, "
                f"тема пропущена. Тема: {topic_name}"
            )
            continue

        button = InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data,
        )
        buttons.append([button])

    if not buttons:
        logger.error("Не удалось создать ни одной кнопки темы")
        return InlineKeyboardMarkup(inline_keyboard=[])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _build_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру с кнопкой отмены.

    Returns:
        InlineKeyboardMarkup с кнопкой отмены
    """
    cancel_button = InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_task_creation",
    )
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])


def _build_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру с кнопками подтверждения/отмены.

    Returns:
        InlineKeyboardMarkup с кнопками подтверждения и отмены
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Создать задачу", callback_data="confirm_task_creation")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_task_creation")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _show_task_preview(
    message: Message,
    task_text: str,
    project_url: str,
    state: FSMContext,
) -> bool:
    """
    Показывает превью задачи перед созданием.

    Args:
        message: Сообщение для ответа
        task_text: Текст задачи
        project_url: URL проекта в Jira
        state: FSM контекст

    Returns:
        True если успешно, False при ошибке
    """
    # Извлекаем заголовок (первая строка) и описание
    lines = task_text.split("\n", 1)
    title = lines[0][:200] if lines else "Без заголовка"
    description = lines[1] if len(lines) > 1 else ""

    # Ограничиваем длину для превью
    if len(description) > 500:
        description = description[:497] + "..."

    preview_text = (
        "<b>📋 Подтвердите создание задачи или отмените</b>\n\n"
        f"<b>Проект:</b>\n{project_url}\n\n"
        f"<b>Заголовок:</b>\n{title}\n\n"
        f"<b>Описание:</b>\n{description or 'Отсутствует'}\n\n"
    )

    # Сохраняем текст задачи в состояние
    await state.update_data(task_text=task_text)

    keyboard = _build_confirmation_keyboard()

    try:
        await message.answer(preview_text, reply_markup=keyboard)
        await state.set_state(TaskCreationStates.waiting_task_confirmation)
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке превью задачи: {e}")
        return False

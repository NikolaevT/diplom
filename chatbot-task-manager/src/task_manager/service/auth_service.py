from urllib.parse import parse_qs, quote, urlparse

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from src.task_manager.dto.user_dto import UserDto
from src.task_manager.service.idm_service import receive
from src.task_manager.service.lion_client import LionClient
from src.task_manager.service.raccoon_client import RaccoonClient
from src.task_manager.service.task_service import task_service


class AuthService:
    """
    Сервис для обработки авторизации пользователей.
    """

    def __init__(self, bot: Bot | None = None, fsm_context: FSMContext | None = None):
        self.raccoon_client = RaccoonClient()
        self.lion_client = LionClient()
        self.bot = bot
        self.fsm_context = fsm_context

    def extract_telegram_id_from_redirect_uri(self, redirect_uri: str) -> str | None:
        """
        Извлекает telegram_id из redirect_uri.

        Args:
            redirect_uri: URL редиректа с параметром telegram_id

        Returns:
            telegram_id или None, если не найден
        """
        if not redirect_uri:
            return None

        try:
            parsed = urlparse(redirect_uri)
            query_params = parse_qs(parsed.query)
            telegram_id = query_params.get("telegram_id", [None])[0]
            return telegram_id
        except Exception as e:
            logger.warning(f"Не удалось извлечь telegram_id из redirect_uri: {e}")
            return None

    async def process_authorization(
        self, login: str, password: str, telegram_id: str
    ) -> tuple[str | None, UserDto | None, str | None]:
        """
        Обрабатывает процесс авторизации пользователя по логину и паролю.

        Args:
            login: Логин пользователя
            password: Пароль пользователя
            telegram_id: Telegram ID пользователя

        Returns:
            Кортеж (telegram_id, UserDto, token) или (None, None, None) в случае ошибки
        """
        if not telegram_id:
            logger.error("telegram_id не передан")
            return None, None, None

        if not login or not password:
            logger.error("Логин или пароль не переданы")
            return None, None, None

        try:
            token = await self.raccoon_client.login(login=login, password=password)
            logger.info(f"Получен токен от svc-raccoon для пользователя {telegram_id}")

            identity_data = await self.lion_client.get_identity(token=token)
            logger.info(f"Получены данные identity для пользователя {telegram_id}")

            bmk_id = identity_data.get("id")
            class_id = identity_data.get("classId")

            if not bmk_id:
                logger.warning(
                    f"В ответе svc-lion не найден id для пользователя {telegram_id}. "
                    f"Полный ответ: {identity_data}"
                )

            user = UserDto(
                telegram_id=str(telegram_id),
                bmk_id=str(bmk_id) if bmk_id else "unknown",
                class_id=str(class_id) if class_id else "unknown",
            )
            receive(user)

            logger.info(
                f"Пользователь {telegram_id} успешно авторизован: "
                f"bmk_id={user.bmk_id}, class_id={user.class_id}"
            )

            return telegram_id, user, token

        except Exception as e:
            logger.error(
                f"Ошибка при обработке авторизации для пользователя {telegram_id}: {e}",
                exc_info=True,
            )
            return None, None, None

    async def send_succ_auth_text(self, telegram_id: str) -> None:
        """
        Уведомляем об успешной авторизации.
        Args:
            telegram_id: Telegram ID пользователя
        """
        if not self.bot:
            logger.error(
                f"Бот не передан в AuthService,"
                f"невозможно отправить сообщение пользователю {telegram_id}"
            )
            return

        try:
            success_auth_text = "<b>Авторизация прошла успешно</b>"

            await self.bot.send_message(
                chat_id=int(telegram_id),
                text=success_auth_text,
            )

            logger.info(f"Сообщение отправлено пользователю {telegram_id} после авторизации")

        except Exception as e:
            logger.error(
                f"Не удалось отправить сообщение пользователю {telegram_id} после авторизации: {e}",
                exc_info=True,
            )

    async def handle_post_authorization(
        self, telegram_id: str, token: str, fsm_context: FSMContext
    ) -> None:
        """
        Обрабатывает логику после успешной авторизации:
        - Сохраняет токен в FSM
        - Проверяет состояние FSM
        - Если пользователь был в процессе создания задачи - продолжает процесс
        - Иначе отправляет сообщение об успешной авторизации

        Args:
            telegram_id: Telegram ID пользователя
            token: Токен авторизации
            fsm_context: Контекст FSM для работы с состоянием
        """
        await fsm_context.update_data(auth_token=token)
        logger.info(f"Токен сохранен в FSM для пользователя {telegram_id}")

        current_state = await fsm_context.get_state()
        state_str = str(current_state) if current_state else ""

        if "waiting_authorization" in state_str or "waiting_project_selection" in state_str:
            logger.info(f"Пользователь {telegram_id} был в процессе создания задачи, продолжаем...")
            await self._continue_task_creation(telegram_id, token, fsm_context)
        else:
            await self.send_succ_auth_text(telegram_id=telegram_id)

    async def _continue_task_creation(
        self, telegram_id: str, token: str, fsm_context: FSMContext
    ) -> None:
        """
        Продолжает процесс создания задачи после авторизации:
        - Получает список проектов
        - Отправляет клавиатуру с проектами пользователю

        Args:
            telegram_id: Telegram ID пользователя
            token: Токен авторизации
            fsm_context: Контекст FSM для работы с состоянием
        """
        if not self.bot:
            logger.error(
                f"Бот не передан в AuthService, "
                f"невозможно продолжить создание задачи для пользователя {telegram_id}"
            )
            return

        try:
            projects = await task_service.get_available_projects(int(telegram_id), token)

            if not projects:
                await self.bot.send_message(
                    chat_id=int(telegram_id),
                    text="У вас нет доступных проектов в Jira.\n"
                    "Обратитесь к администратору для получения доступа.",
                )
                await fsm_context.clear()
            else:
                # Формируем клавиатуру с проектами
                keyboard = self._create_projects_keyboard(projects)

                await self.bot.send_message(
                    chat_id=int(telegram_id),
                    text="<b>Авторизация успешна!</b>\n\n<b>"
                    "Создание задачи в Jira</b>\n\n"
                    "Выберите проект, в котором хотите создать задачу:",
                    reply_markup=keyboard,
                )

                await fsm_context.set_state("TaskCreationStates:waiting_project_selection")

        except Exception as e:
            logger.error(f"Ошибка при получении проектов после авторизации: {e}")
            await self.bot.send_message(
                chat_id=int(telegram_id),
                text="Произошла ошибка при получении списка проектов.\n"
                "Попробуйте позже или обратитесь к администратору.",
            )
            await fsm_context.clear()

    def _create_projects_keyboard(self, projects: dict[str, str]) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру с кнопками проектов.

        Args:
            projects: Словарь проектов (название -> URL)

        Returns:
            InlineKeyboardMarkup с кнопками проектов и кнопкой отмены
        """
        buttons = []
        for project_name, project_url in projects.items():
            encoded_url = quote(project_url, safe="")
            callback_data = f"project:{encoded_url}"
            button = InlineKeyboardButton(text=project_name, callback_data=callback_data)
            buttons.append([button])

        cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel_task_creation")
        buttons.append([cancel_button])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

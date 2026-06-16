from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from src.task_manager.bot_instance import get_bot
from src.task_manager.dto.summary_dto import SummaryDto


async def send_summary(dto: SummaryDto) -> None:
    """
    Отправляет уведомление с summary задачи каждому пользователю из списка recipients.

    Args:
        dto: SummaryDto с данными уведомления (task_link, summary, recipients)
    """
    bot = get_bot()

    # Формируем текст сообщения
    message_text = f"📋 <b>Новое уведомление</b>\n\n" f"{dto.summary}"

    # Создаем инлайн-кнопку со ссылкой на задачу
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔗 Открыть задачу", url=dto.task_link)]]
    )

    # Отправляем сообщение каждому получателю
    for telegram_id in dto.recipients:
        try:
            await bot.send_message(chat_id=telegram_id, text=message_text, reply_markup=keyboard)

        except TelegramForbiddenError:
            logger.warning(
                f"Не удалось отправить уведомление пользователю {telegram_id}: "
                f"пользователь заблокировал бота"
            )

        except TelegramBadRequest as e:
            logger.warning(
                f"Не удалось отправить уведомление пользователю {telegram_id}: "
                f"неверный chat_id или другая ошибка запроса. Детали: {e}"
            )

        except Exception as e:
            logger.error(
                f"Неожиданная ошибка при отправке уведомления пользователю {telegram_id}: {e}"
            )

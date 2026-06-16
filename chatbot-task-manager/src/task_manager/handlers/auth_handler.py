from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="auth_handler")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Старт-скрин бота.
    """
    welcome_text = (
        "<b>Привет!</b> 👋\n\n"
        "Пока это просто заглушка авторизации.\n\n"
        "Потом я стану нормально честное слово"
        "Доступные команды:\n"
        "• /create_task - создать задачу в Jira\n"
        "• /help - помощь по командам\n\n"
        "Для создания задачи используйте команду /create_task"
    )

    await message.answer(welcome_text)

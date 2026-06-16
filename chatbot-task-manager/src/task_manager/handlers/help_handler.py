from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help_handler")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help.
    Показывает список доступных команд и инструкцию по использованию.
    """
    help_text = (
        "<b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/create_task - Создать задачу в Jira\n\n"
    )

    await message.answer(help_text)

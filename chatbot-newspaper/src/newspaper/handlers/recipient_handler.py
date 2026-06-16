from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.chat_member_updated import (
    ADMINISTRATOR,
    IS_NOT_MEMBER,
    MEMBER,
    ChatMemberUpdatedFilter,
)
from aiogram.types import ChatMemberUpdated, Message
from loguru import logger

from src.newspaper.service.recipient_client import RecipientClient

router = Router(name="recipient_handler")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Обработка команды /start.
    Отправляет POST-запрос на внешний сервис для регистрации получателя.
    """
    user = message.from_user
    if not user:
        return

    telegram_id = user.id
    name = (user.full_name or user.username or str(telegram_id)).strip()
    chat_type = message.chat.type if message.chat else "private"

    logger.info(f"Команда /start: id={telegram_id}, name='{name}', type={chat_type}")

    await RecipientClient.register(
        telegram_id=telegram_id,
        name=name,
        recipient_type=chat_type,
        is_admin=False,
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> (MEMBER | ADMINISTRATOR))
)
async def bot_added_to_chat(event: ChatMemberUpdated) -> None:
    """
    Обработка добавления бота в групповой чат или канал.
    Отправляет POST-запрос на внешний сервис для регистрации получателя.
    """
    chat = event.chat

    telegram_id = chat.id
    name = chat.title or "Без названия"
    chat_type = chat.type  # group, supergroup, channel
    is_admin = event.new_chat_member.status == "administrator"

    logger.info(
        f"Бот добавлен в чат: id={telegram_id}, "
        f"title='{name}', type={chat_type}, is_admin={is_admin}"
    )

    await RecipientClient.register(
        telegram_id=telegram_id,
        name=name,
        recipient_type=chat_type,
        is_admin=is_admin,
    )

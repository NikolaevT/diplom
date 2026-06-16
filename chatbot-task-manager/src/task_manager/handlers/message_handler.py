from typing import Any, Dict, Optional

from aiogram import Router
from aiogram.types import Message
from loguru import logger

from src.task_manager.mapper import message_to_entity
from src.task_manager.repository.message_repository import save

router = Router(name="message_handler")


def extract_text_from_message(message: Message) -> Optional[str]:
    """
    Извлекает текст из сообщения, включая подпись к медиа.
    Args:
        message: Объект сообщения от aiogram
    Returns:
        Текст сообщения или None если текста нет
    """
    if message.text:
        return message.text

    if message.caption:
        return message.caption

    return None


def prepare_message_data(message: Message) -> Dict[str, Any]:
    """
    Подготавливает данные сообщения для сохранения в MongoDB.
    Args:
        message: Объект сообщения от aiogram
    Returns:
        Словарь с данными для сохранения
    """
    try:
        content = extract_text_from_message(message)

        message_data = {
            "message_id": str(message.message_id),
            "chat_id": message.chat.id,
            "user_id": str(message.from_user.id),
            "content": content,
            "created_at": message.date,
        }

        return message_data

    except Exception as e:
        logger.error(f"Ошибка при подготовке данных сообщения: {e}")
        raise


async def save_message_to_db(message_data: Dict[str, Any]):
    """
    Сохраняет сообщение в базу данных.
    Args:
        message_data: Подготовленные данные сообщения
    """
    try:
        message_entity = message_to_entity(message_data)
        save(message_entity)

    except Exception as e:
        logger.error(f"Ошибка при сохранении сообщения в БД: {e}")


@router.message()
async def handle_all_messages(message: Message) -> None:
    """
    Обработчик ВСЕХ сообщений.
    Обрабатывает любые типы сообщений, но сохраняет только те,
    которые содержат текст (основной текст или подпись к медиа).
    """
    try:
        message_data = prepare_message_data(message)

        if not message_data["content"]:
            logger.debug(f"Сообщение {message.message_id} пропущено: отсутствует текст")
            return

        logger.info(
            f"Обработка сообщения {message.message_id} от пользователя {message_data['user_id']}, "
            f"в чате {message_data['chat_id']}, "
            f"содержимое: {message_data['content']}"
        )

        await save_message_to_db(message_data)

    except ValueError as e:
        logger.debug(f"Сообщение {message.message_id} пропущено: {e}")

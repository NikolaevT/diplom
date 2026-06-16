from typing import Any, Dict

from src.task_manager.model import MessageEntity


def to_entity(message_data: Dict[str, Any]) -> MessageEntity:
    """
    Преобразует словарь с данными сообщения в MessageEntity.

    Args:
        message_data: Словарь с данными сообщения из prepare_message_data

    Returns:
        MessageEntity: Объект сущности для сохранения в БД

    Raises:
        ValueError: Если обязательные поля отсутствуют или content равен None
    """
    # Проверяем, что content не None (должен быть валидирован до маппера)
    if message_data.get("content") is None:
        raise ValueError("content не может быть None для создания MessageEntity")

    return MessageEntity(
        chat_id=message_data["chat_id"],
        user_id=message_data["user_id"],
        content=message_data["content"],
        created_at=message_data["created_at"],
    )


def to_dto(entity: MessageEntity) -> Dict[str, Any]:
    """
    Преобразует MessageEntity в словарь с данными сообщения.

    Args:
        entity: Объект сущности из БД

    Returns:
        Dict[str, Any]: Словарь с данными сообщения
    """
    return {
        "message_id": str(entity.id) if entity.id else None,
        "chat_id": entity.chat_id,
        "user_id": entity.user_id,
        "content": entity.content,
        "created_at": entity.created_at,
    }

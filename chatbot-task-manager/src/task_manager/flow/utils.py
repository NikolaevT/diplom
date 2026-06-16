from typing import List

from src.task_manager.dto.message_dto import Message
from src.task_manager.dto.participant import Participant, Participants
from src.task_manager.model.message_entity import MessageEntity


def message_entity_to_dto(entity: MessageEntity) -> Message:
    """
    Конвертирует MessageEntity в Message DTO.

    Args:
        entity: Сущность сообщения из MongoDB

    Returns:
        Message DTO для использования в flow
    """
    return Message(
        user_id=int(entity.user_id),
        chat_id=int(entity.chat_id),
        text=entity.content,
        time=entity.created_at.isoformat() if entity.created_at else "",
    )


def extract_participants(messages: List[Message]) -> Participants:
    """
    Извлекает уникальных участников из списка сообщений.

    Args:
        messages: Список сообщений

    Returns:
        Объект Participants со списком уникальных участников
    """
    # Создаем словарь для хранения уникальных участников по user_id
    unique_participants = {}

    for message in messages:
        if message.user_id not in unique_participants:
            # Создаем участника с user_id, имя будет пустым
            # (можно расширить логику для получения имен)
            # но для этого нужно постучаться в енота или в медведя...
            unique_participants[message.user_id] = Participant(
                user_id=message.user_id, name=f"User_{message.user_id}"
            )

    return Participants(participants=list(unique_participants.values()))

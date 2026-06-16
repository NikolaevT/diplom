from src.task_manager.model import MessageEntity


def save(model: MessageEntity) -> MessageEntity:
    model.save()

    return model


def find_by_filter(**filters) -> list[MessageEntity]:
    """
    Поиск сообщений по фильтрам.

    Args:
        **filters: Параметры фильтрации
            (например, chat_id=123, created_at__gte=datetime)

    Returns:
        Список найденных сообщений
    """
    return list(MessageEntity.objects(**filters))

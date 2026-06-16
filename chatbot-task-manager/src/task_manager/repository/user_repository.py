from src.task_manager.model import UserEntity


def save(model):
    model.save()
    return model


def find_by_telegram_id(telegram_id: int | str) -> UserEntity | None:
    """
    Возвращает пользователя по telegram_id или None, если не найден.
    Args:
        telegram_id: Telegram ID пользователя (int или str)
    Returns:
        UserEntity если найден, иначе None
    """
    return UserEntity.objects(telegram_id=str(telegram_id))

from src.task_manager.dto.user_dto import UserDto
from src.task_manager.model import UserEntity


def to_entity(idm: UserDto) -> UserEntity:
    """
    Преобразует User DTO в IDMEntity.
    Args:
        idm: User DTO
    Returns:
        UserEntity: Объект сущности для сохранения в БД
    """

    return UserEntity(
        telegram_id=idm.telegram_id,
        bmk_id=idm.bmk_id,
        class_id=idm.class_id,
    )

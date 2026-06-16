from src.task_manager.dto.user_dto import UserDto
from src.task_manager.mapper import user_to_entity
from src.task_manager.repository.user_repository import save


def receive(user: UserDto):
    """
    Получает DTO пользователя, конвертирует в Entity и кладет в БД
    Args: idm: DTO с данными пользователя
    """

    entity = user_to_entity(user)
    save(entity)

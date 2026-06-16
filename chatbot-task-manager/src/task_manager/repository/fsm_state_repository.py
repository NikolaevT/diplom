from typing import Any, Optional

from loguru import logger

from src.task_manager.model.fsm_state_entity import FSMStateEntity


def save_state(user_id: int, chat_id: int, state: Optional[str]) -> None:
    """
    Сохраняет состояние FSM для пользователя.

    Args:
        user_id: Telegram ID пользователя
        chat_id: ID чата
        state: Состояние FSM
    """
    try:
        FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).update_one(
            set__state=state,
            upsert=True,
        )
        logger.debug(
            f"Состояние сохранено: user_id={user_id}, " f"chat_id={chat_id}, state={state}"
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении состояния: {e}")
        raise


def get_state(user_id: int, chat_id: int) -> Optional[str]:
    """
    Получает состояние FSM для пользователя.

    Args:
        user_id: Telegram ID пользователя
        chat_id: ID чата

    Returns:
        Состояние FSM или None
    """
    try:
        entity = FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).first()

        if entity:
            return entity.state

        return None
    except Exception as e:
        logger.error(f"Ошибка при получении состояния: {e}")
        return None


def save_data(user_id: int, chat_id: int, data: dict[str, Any]) -> None:
    """
    Сохраняет данные FSM для пользователя.

    Args:
        user_id: Telegram ID пользователя
        chat_id: ID чата
        data: Данные FSM
    """
    try:
        FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).update_one(
            set__data=data,
            upsert=True,
        )
        logger.debug(f"Данные сохранены: user_id={user_id}, " f"chat_id={chat_id}, data={data}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")
        raise


def get_data(user_id: int, chat_id: int) -> dict[str, Any]:
    """
    Получает данные FSM для пользователя.

    Args:
        user_id: Telegram ID пользователя
        chat_id: ID чата

    Returns:
        Данные FSM или пустой словарь
    """
    try:
        entity = FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).first()

        if entity and entity.data:
            return entity.data

        return {}
    except Exception as e:
        logger.error(f"Ошибка при получении данных: {e}")
        return {}

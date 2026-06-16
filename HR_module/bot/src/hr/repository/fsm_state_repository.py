from typing import Any, Optional

from loguru import logger

from src.hr.model.fsm_state_entity import FSMStateEntity


def save_state(user_id: int, chat_id: int, state: Optional[str]) -> None:
    """Сохраняет состояние FSM для пользователя."""
    try:
        FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).update_one(
            set__state=state,
            upsert=True,
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении состояния FSM: {e}")
        raise


def get_state(user_id: int, chat_id: int) -> Optional[str]:
    """Получает состояние FSM для пользователя."""
    try:
        entity = FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).first()
        return entity.state if entity else None
    except Exception as e:
        logger.error(f"Ошибка при получении состояния FSM: {e}")
        return None


def save_data(user_id: int, chat_id: int, data: dict[str, Any]) -> None:
    """Сохраняет данные FSM для пользователя."""
    try:
        FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).update_one(
            set__data=data,
            upsert=True,
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных FSM: {e}")
        raise


def get_data(user_id: int, chat_id: int) -> dict[str, Any]:
    """Получает данные FSM для пользователя."""
    try:
        entity = FSMStateEntity.objects(user_id=user_id, chat_id=chat_id).first()
        return entity.data if entity and entity.data else {}
    except Exception as e:
        logger.error(f"Ошибка при получении данных FSM: {e}")
        return {}

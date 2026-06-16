from typing import Any, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from src.hr.repository import fsm_state_repository


class MongoDBStorage(BaseStorage):
    """
    Адаптер MongoDB Storage для FSM состояний aiogram.
    """

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        state_str = state.state if isinstance(state, State) else state
        fsm_state_repository.save_state(key.user_id, key.chat_id, state_str)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return fsm_state_repository.get_state(key.user_id, key.chat_id)

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        fsm_state_repository.save_data(key.user_id, key.chat_id, data)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return fsm_state_repository.get_data(key.user_id, key.chat_id)

    async def close(self) -> None:
        pass

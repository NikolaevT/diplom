"""
Модуль репозиториев для работы с базой данных.
"""

from . import (
    fsm_state_repository,
    message_repository,
    task_repository,
    user_repository,
)

__all__ = [
    "fsm_state_repository",
    "message_repository",
    "task_repository",
    "user_repository",
]

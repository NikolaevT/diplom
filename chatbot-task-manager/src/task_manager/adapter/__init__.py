"""
Модуль адаптеров для интеграции с внешними библиотеками.
"""

from .fsm_storage import MongoDBStorage

__all__ = ["MongoDBStorage"]

from loguru import logger
from mongoengine import connect as mongoengine_connect
from mongoengine import disconnect as mongoengine_disconnect

from src.task_manager.config.settings import settings


class MongoDBConnection:
    """Класс для управления подключением к MongoDB через MongoEngine."""

    @classmethod
    def connect(cls) -> None:
        """Установить подключение к MongoDB через MongoEngine."""
        connect_params = {
            "db": settings.mongodb_name,
            "host": settings.mongodb_url,
            "serverSelectionTimeoutMS": 5000,
            "maxPoolSize": settings.mongodb_max_pool_size,
            "minPoolSize": settings.mongodb_min_pool_size,
            "waitQueueTimeoutMS": settings.mongodb_wait_queue_timeout_ms,
        }

        # На продакшене/стенде креды обязательны
        if settings.environment.lower() in ("production", "staging"):
            if not settings.mongodb_username or not settings.mongodb_password:
                raise ValueError(
                    "MONGODB_USERNAME и MONGODB_PASSWORD обязательны "
                    f"для окружения {settings.environment}"
                )
            connect_params["username"] = settings.mongodb_username
            connect_params["password"] = settings.mongodb_password
            connect_params["authentication_source"] = settings.mongodb_auth_source or "admin"
        # В development можно без аутентификации
        elif settings.mongodb_username and settings.mongodb_password:
            connect_params["username"] = settings.mongodb_username
            connect_params["password"] = settings.mongodb_password
            connect_params["authentication_source"] = settings.mongodb_auth_source or "admin"
        logger.info(f"Данные подключения{connect_params}")
        mongoengine_connect(**connect_params)

    @classmethod
    def disconnect(cls) -> None:
        """Закрыть подключение к MongoDB."""
        mongoengine_disconnect()


# Экспортируемые функции для использования в других модулях
def connect() -> None:
    """Функция-обертка для подключения к MongoDB."""
    MongoDBConnection.connect()


def disconnect() -> None:
    """Функция-обертка для отключения от MongoDB."""
    MongoDBConnection.disconnect()

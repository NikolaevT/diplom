from loguru import logger
from mongoengine import connect as mongoengine_connect
from mongoengine import disconnect as mongoengine_disconnect

from src.hr.config.settings import settings


class MongoDBConnection:
    """Класс для управления подключением к MongoDB через MongoEngine."""

    @classmethod
    def connect(cls) -> None:
        """Установить подключение к MongoDB."""
        from mongoengine import connection

        mongoengine_connect(
            db=settings.mongodb_name,
            host=settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
        )
        connection.get_db().client.admin.command("ping")
        logger.info(f"MongoDB подключен: {settings.mongodb_url}/{settings.mongodb_name}")

    @classmethod
    def disconnect(cls) -> None:
        """Закрыть подключение к MongoDB."""
        mongoengine_disconnect()


def connect() -> None:
    MongoDBConnection.connect()


def disconnect() -> None:
    MongoDBConnection.disconnect()

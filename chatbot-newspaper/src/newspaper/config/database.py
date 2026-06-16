from mongoengine import connect
from mongoengine import disconnect as mongoengine_disconnect

from src.newspaper.config.settings import settings


class MongoDBConnection:
    """Класс для управления подключением к MongoDB через MongoEngine."""

    @classmethod
    def connect(cls) -> None:
        """Установить подключение к MongoDB через MongoEngine."""
        connect(
            db=settings.mongodb_database,
            host=settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
            authentication_source=None,
            username=None,
            password=None,
        )

    @classmethod
    def disconnect(cls) -> None:
        """Закрыть подключение к MongoDB."""
        mongoengine_disconnect()

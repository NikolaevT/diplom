from typing import Optional

import chromadb
from chromadb.api import ClientAPI
from loguru import logger

from src.task_manager.config.settings import settings


class ChromaDBConnection:
    """Класс для управления подключением к Chroma DB."""

    _client: Optional[ClientAPI] = None
    _collection = None

    @classmethod
    def connect(cls) -> None:
        """Установить подключение к Chroma DB."""
        try:
            chroma_url = f"http://{settings.chroma_host}:{settings.chroma_port}"

            cls._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )

            # Проверка подключения
            cls._client.heartbeat()

            # Получаем или создаем коллекцию
            cls._collection = cls.get_or_create_collection()

            logger.info(
                f"Chroma DB подключен: {chroma_url}, "
                f"коллекция: {settings.chroma_collection_name}"
            )
        except Exception as e:
            logger.error(f"Ошибка при подключении к Chroma DB: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        """Закрыть подключение к Chroma DB."""
        if cls._client:
            try:
                cls._client.clear_system_cache()
            except Exception as e:
                logger.warning(f"Ошибка при закрытии соединения с Chroma DB: {e}")
            finally:
                cls._client = None
                cls._collection = None

    @classmethod
    def get_client(cls) -> ClientAPI:
        """Получить клиент Chroma DB."""
        if cls._client is None:
            raise RuntimeError("Chroma DB не подключен. Вызовите connect() сначала.")
        return cls._client

    @classmethod
    def get_or_create_collection(cls):
        """Получить или создать коллекцию для векторных представлений."""
        if cls._client is None:
            raise RuntimeError("Chroma DB не подключен. Вызовите connect() сначала.")

        try:
            # Пытаемся получить существующую коллекцию
            collection = cls._client.get_collection(name=settings.chroma_collection_name)
            logger.info(f"Коллекция '{settings.chroma_collection_name}' найдена")
            return collection
        except Exception:
            # Если коллекция не существует, создаем новую
            logger.info(f"Создание коллекции '{settings.chroma_collection_name}'")
            collection = cls._client.create_collection(name=settings.chroma_collection_name)
            return collection

    @classmethod
    def get_collection(cls):
        """Получить текущую коллекцию."""
        if cls._collection is None:
            raise RuntimeError("Коллекция не инициализирована. Вызовите connect() сначала.")
        return cls._collection

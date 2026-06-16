import logging
import os

from sentence_transformers import SentenceTransformer

from src.task_manager.config.chroma_db import ChromaDBConnection
from src.task_manager.config.settings import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Сервис для RAG"""

    def __init__(self):
        """Инициализация RAG сервиса с моделью векторизации."""
        model_name = os.getenv("EMBEDDING_MODEL", settings.embedding_model)
        self.model = SentenceTransformer(model_name)

    async def replenish_vector_db(self, text: str, mongodb_message_id: str):
        """
        Принимает сообщение, векторизует его и кладет в векторную БД

        Args:
            text: текст сообщения
            mongodb_message_id: идентификатор сообщения в MongoDB
        """
        try:
            # Векторизация текста
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()

            # Получение коллекции Chroma DB
            collection = ChromaDBConnection.get_collection()

            # Сохранение в Chroma DB
            collection.add(
                ids=[mongodb_message_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{"mongodb_message_id": mongodb_message_id}],
            )

        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Ошибка при добавлении сообщения в векторную БД: {e}")
            raise

    async def search_by_text(self, query: str, top_n: int = 5) -> list[str]:
        """
        Поиск похожих документов по тексту запроса

        Args:
            query: текст запроса для поиска
            top_n: количество результатов (по умолчанию 5)

        Returns:
            list[str]: список найденных текстов документов
        """
        try:
            # Векторизация запроса
            query_embedding = self.model.encode(query, convert_to_numpy=True).tolist()

            # Получение коллекции Chroma DB
            collection = ChromaDBConnection.get_collection()

            # Поиск похожих документов
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_n,
            )

            # Возвращаем только тексты документов
            documents = results.get("documents", [[]])[0]
            return documents

        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Ошибка при поиске в векторной БД: {e}")
            raise

import asyncio
from datetime import datetime, timedelta
from typing import List

from crewai.flow import Flow, listen, start
from loguru import logger

from src.task_manager.dto.chat_summary import Topic
from src.task_manager.dto.state import ChatAnalysisState
from src.task_manager.flow.crews.topic_analyze_crew import TopicAnalyzeCrew
from src.task_manager.flow.utils import (
    extract_participants,
    message_entity_to_dto,
)
from src.task_manager.repository import message_repository


def _parse_time(value: str) -> str:
    """Извлекает время из ISO-строки."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.time().isoformat()
    except ValueError:
        return value


class ChatAnalysisFlow(Flow[ChatAnalysisState]):
    """Flow для анализа чата и извлечения тем обсуждений"""

    def __init__(self, chat_id: int):
        """
        Инициализация flow.

        Args:
            chat_id: ID чата для анализа
        """
        super().__init__()
        self.chat_id = chat_id

    @start()
    def load_messages_from_db(self):
        """Загрузка сообщений из MongoDB по chat_id за последние 2 часа"""
        logger.info(f"Загрузка сообщений для chat_id={self.chat_id}")

        # Здесь вычитаем 6 часов: 3 часа — это сдвиг до UTC, и ещё 3 часа — диапазон анализа
        three_hours_ago = datetime.now() - timedelta(hours=6)

        # Загружаем сообщения из БД за последние 3 часа
        message_entities = message_repository.find_by_filter(
            chat_id=self.chat_id, created_at__gte=three_hours_ago
        )

        logger.info(f"Найдено {len(message_entities)} сообщений за последние 3 часа")

        messages = [message_entity_to_dto(entity) for entity in message_entities]

        logger.info(f"Загружено {len(messages)} сообщений за последние 3 часа")

        # Сохраняем в состояние
        self.state.input_messages = messages

    @listen(load_messages_from_db)
    def extract_participants_step(self):
        """Извлечение участников из сообщений"""
        logger.info("Извлечение участников чата")

        # Извлекаем участников
        participants = extract_participants(self.state.input_messages)

        logger.info(f"Найдено {len(participants.participants)} участников")

        # Сохраняем в состояние
        self.state.participants = participants

    @listen(extract_participants_step)
    def analyze_topics(self):
        """Анализ тем через TopicAnalyzeCrew"""
        logger.info("Запуск анализа тем через LLM")

        # Подготавливаем данные для crew
        messages_data = [msg.model_dump() for msg in self.state.input_messages]
        participants_data = self.state.participants.model_dump()

        # Запускаем crew
        crew_result = (
            TopicAnalyzeCrew()
            .crew()
            .kickoff(
                inputs={
                    "messages": messages_data,
                    "participants": participants_data,
                }
            )
        )

        logger.info(f"Анализ завершен. Результат: {crew_result.pydantic}")

        # Сохраняем результат в состояние
        self.state.topics = crew_result.pydantic

        return crew_result.pydantic


def _run_flow_sync(chat_id: int):
    """
    Синхронный запуск flow в отдельном потоке.

    Args:
        chat_id: ID чата для анализа

    Returns:
        Результат flow
    """
    flow = ChatAnalysisFlow(chat_id=chat_id)
    result = flow.kickoff()
    return result


async def analyze_chat(chat_id: int) -> List[Topic]:
    """
    Точка входа для запуска анализа чата.

    Args:
        chat_id: ID чата в Telegram

    Returns:
        Список тем обсуждений
    """
    logger.info(f"Запуск анализа чата chat_id={chat_id}")

    # Используем asyncio.to_thread для запуска синхронного кода
    # в отдельном потоке. Это стандартный подход Python 3.7+
    # для выполнения блокирующего кода в async контексте
    result = await asyncio.to_thread(_run_flow_sync, chat_id)

    # Возвращаем список тем
    if hasattr(result, "topics"):
        return result.topics
    return []

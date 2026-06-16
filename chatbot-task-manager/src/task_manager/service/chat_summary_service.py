from typing import List

from loguru import logger

from src.task_manager.dto.chat_summary import Topic
from src.task_manager.flow.chat_analysis_flow import analyze_chat


class ChatSummaryService:
    """
    Сервис для работы с саммари групповых чатов и извлечения тем.
    """

    async def get_topics(self, chat_id: int) -> List[Topic]:
        """
        Получает список тем обсуждений из группового чата.

        Args:
            chat_id: ID группового чата в Telegram

        Returns:
            Список тем обсуждений
        """
        logger.info(f"Получение тем для чата chat_id={chat_id}")

        try:
            # Запускаем анализ через CrewAI Flow
            topics = await analyze_chat(chat_id)

            logger.info(f"Найдено {len(topics)} тем для chat_id={chat_id}")
            return topics

        except Exception as e:
            logger.error(f"Ошибка при получении тем для чата {chat_id}: {e}")
            raise


chat_summary_service = ChatSummaryService()

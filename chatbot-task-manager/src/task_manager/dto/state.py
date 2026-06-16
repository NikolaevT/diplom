from pydantic import BaseModel, Field

from src.task_manager.dto.chat_summary import Topics
from src.task_manager.dto.message_dto import Message
from src.task_manager.dto.participant import Participants


class ChatAnalysisState(BaseModel):
    """Стейт для анализа чата"""

    # Входные данные
    input_messages: list[Message] = Field(default_factory=list)
    # Результаты анализа
    participants: Participants = Field(default_factory=Participants)
    topics: Topics = Field(default_factory=Topics)

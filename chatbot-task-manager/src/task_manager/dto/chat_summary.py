from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Topic(BaseModel):
    """Тема обсуждения (ветка)"""

    topic: str = ""  # Название темы
    category: str  # Категория (frontend, backend, инфраструктура и т.д.)
    summary: str  # Краткая суть обсуждения (1-2 предложения)
    participants_with_comments: Dict[str, List[str]] = Field(
        default_factory=dict
    )  # Кто что говорил по этой теме
    resolution: Optional[str] = None  # Как решили проблему (если было решение)
    text_for_task: Optional[str] = None  # Поле для текста задачи в jira


class Topics(BaseModel):
    topics: List[Topic] = Field(default_factory=list)


class TaskSummary(BaseModel):
    header: str = ""
    content: str = ""

from pydantic import BaseModel, Field


class SummaryDto(BaseModel):
    """
    Dto для отправки уведомления пользователей с summary
    """

    task_link: str = Field(..., description="Ссылка на задачу")
    summary: str = Field(..., description="Краткое summary (или тема)")
    recipients: list[str] = Field(..., description="Список идентификаторов пользователей телеграм")

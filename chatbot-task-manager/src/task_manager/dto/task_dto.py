from pydantic import BaseModel, Field


class CreateIssueTelegramRequest(BaseModel):
    """
    Dto для создания задачи через Telegram.
    """

    project: str = Field(..., description="URL проекта")
    summary: str = Field(..., description="Заголовок задачи")
    description: str = Field(..., description="Описание задачи")
    reporter_telegram_id: int = Field(
        ...,
        alias="reporterTelegramId",
        description="Telegram ID создателя задачи",
    )
    assignee_telegram_id: int | None = Field(
        default=None,
        alias="assigneeTelegramId",
        description="Telegram ID исполнителя (опционально)",
    )

    class Config:
        populate_by_name = True


class CreatedIssueResponseDto(BaseModel):
    """
    Dto для ответа после создания задачи.
    """

    issue: str = Field(..., description="URL созданной задачи в Jira")

from pydantic import BaseModel, Field


class AvailableJiraProjectsResponseDto(BaseModel):
    """
    Dto для ответа со списком доступных проектов Jira.
    """

    available_projects: dict[str, str] = Field(
        ...,
        alias="availableProjects",
        description="Словарь проектов: название -> URL",
    )

    class Config:
        populate_by_name = True

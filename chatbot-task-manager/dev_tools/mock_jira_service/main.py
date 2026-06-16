"""
Mock Jira Service для разработки.

Этот сервис имитирует работу реального Jira API для тестирования бота
в режиме разработки без необходимости подключения к реальному Jira.

Запуск:
    make mock-jira
    # или: uvicorn main:app --reload --port 8091

API документация:
    http://127.0.0.1:8091/docs
"""

import inspect
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from test_data import generate_task_url, get_projects_for_user

MOCK_SERVICE_PORT = 8091


@asynccontextmanager
async def lifespan(app: FastAPI):
    cat = inspect.cleandoc(r"""
          |\      _,,,---,,_
    ZZZzz /,`.-'`'    -.  ;-;;,_
         |,4-  ) )-,_. ,\ (  `'-'
        '---''(_/--'  `-'\_)
      """)
    print("\n" + cat + "\n")
    print("Mock Jira Integration Service is purring...")
    print(f"API docs: http://127.0.0.1:{MOCK_SERVICE_PORT}/docs")
    yield


app = FastAPI(
    title="Mock Jira Integration Service",
    description="Mock-сервис для имитации Jira Integration API в разработке",
    version="1.0.0",
    lifespan=lifespan,
)


class AvailableJiraProjectsResponseDto(BaseModel):
    """DTO для ответа со списком проектов."""

    model_config = ConfigDict(populate_by_name=True)

    available_projects: dict[str, str] = Field(
        ...,
        alias="availableProjects",
        description="Словарь проектов: название -> URL",
    )


class CreateIssueTelegramRequest(BaseModel):
    """DTO для создания задачи через Telegram."""

    model_config = ConfigDict(populate_by_name=True)

    project: str = Field(..., description="URL проекта")
    summary: str = Field(..., description="Заголовок задачи")
    description: str = Field(..., description="Описание задачи")
    reporter_telegram_id: int = Field(
        ...,
        alias="reporterTelegramId",
        description="Telegram ID создателя",
    )
    assignee_telegram_id: int | None = Field(
        default=None,
        alias="assigneeTelegramId",
        description="Telegram ID исполнителя",
    )


class CreatedIssueResponseDto(BaseModel):
    """DTO для ответа после создания задачи."""

    model_config = ConfigDict(populate_by_name=True)

    issue: str = Field(..., description="URL созданной задачи")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Mock Jira Integration Service is running",
        "docs": f"http://127.0.0.1:{MOCK_SERVICE_PORT}/docs",
    }


@app.get("/api/linkedservice/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get(
    "/v1/project/by-telegramId/{telegram_id}",
    response_model=AvailableJiraProjectsResponseDto,
    response_model_by_alias=True,
)
async def get_projects_by_telegram_id(
    telegram_id: int,
) -> AvailableJiraProjectsResponseDto:
    projects = get_projects_for_user(telegram_id)
    return AvailableJiraProjectsResponseDto(available_projects=projects)


@app.post(
    "/v1/issue/by-telegramId",
    response_model=CreatedIssueResponseDto,
    response_model_by_alias=True,
    status_code=201,
)
async def create_issue(task: CreateIssueTelegramRequest) -> CreatedIssueResponseDto:
    if not task.summary or not task.summary.strip():
        raise HTTPException(
            status_code=400,
            detail="Summary cannot be empty",
        )

    if not task.description or not task.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Description cannot be empty",
        )

    task_url = generate_task_url(task.project)

    print(f"[MOCK] Created task: {task_url}")
    print(f"  Project: {task.project}")
    print(f"  Summary: {task.summary}")
    print(f"  Reporter ID: {task.reporter_telegram_id}")

    return CreatedIssueResponseDto(issue=task_url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=MOCK_SERVICE_PORT)

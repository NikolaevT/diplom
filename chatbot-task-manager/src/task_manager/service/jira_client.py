import httpx
from loguru import logger

from src.task_manager.config.settings import settings
from src.task_manager.dto.project_dto import AvailableJiraProjectsResponseDto
from src.task_manager.dto.task_dto import (
    CreatedIssueResponseDto,
    CreateIssueTelegramRequest,
)


class JiraClient:
    """
    Клиент для взаимодействия с внешним сервисом интеграции с Jira.

    Два метода:
    1. get_available_projects - получает список доступных проектов
    2. create_task - создаёт задачу и возвращает ссылку
    """

    def __init__(self) -> None:
        """
        Инициализация клиента.
        """
        if settings.jira_use_mock:
            raw = settings.jira_mock_host.strip() if settings.jira_mock_host else ""
            self.base_url = raw or None
            if self.base_url:
                logger.info(f"Jira-клиент в режиме MOCK: base_url={self.base_url}")
            else:
                logger.warning("jira_use_mock=true, но jira_mock_host пустой")
        else:
            self.base_url = settings.jira_host.strip() if settings.jira_host else None
            if not self.base_url:
                logger.info(
                    "jira_host не задан; для локальной демо включите JIRA_USE_MOCK=true "
                    "и запустите make mock-jira"
                )

    async def get_available_projects(self, telegram_id: int, token: str) -> dict[str, str]:
        """
        Получает список доступных проектов Jira для пользователя.
        Args:
            telegram_id: Telegram ID пользователя
            token: Bearer токен для авторизации
        Returns:
            Словарь проектов: название -> URL
        """
        telegram_id = str(telegram_id)
        logger.info(f"Запрос списка проектов для telegram_id={telegram_id}")

        headers = {"Authorization": f"BAP_Bearer {token}"}

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
        ) as client:
            try:
                resp = await client.get(f"/v1/project/by-telegramId/{telegram_id}")
                resp.raise_for_status()
                data = resp.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "HTTP ошибка при запросе проектов: "
                    f"status={e.response.status_code}, "
                    f"url={e.request.url!s}, "
                    f"body={e.response.text!r}"
                )
                raise

            except httpx.RequestError as e:
                logger.error(
                    "Ошибка соединения с сервисом Jira: "
                    f"type={type(e)}, repr={e!r}, url={getattr(e.request, 'url', None)}"
                )
                raise

        response_dto = AvailableJiraProjectsResponseDto(**data)
        return response_dto.available_projects

    async def create_task(self, task: CreateIssueTelegramRequest, token: str) -> str:
        """
        Создаёт задачу в Jira через внешний сервис.
        Args:
            task: DTO задачи с данными для создания
            token: Bearer токен для авторизации
        Returns:
            URL созданной задачи
        """
        logger.debug(f"Создание задачи: {task.model_dump_json()}")

        # Формируем тело запроса с camelCase именами полей
        body = task.model_dump(by_alias=True, mode="json")

        headers = {"Authorization": f"BAP_Bearer {token}"}

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
        ) as client:
            try:
                resp = await client.post("/v1/issue/by-telegramId", json=body)
                resp.raise_for_status()
                data = resp.json()

            except httpx.RequestError as e:
                logger.error(f"Ошибка соединения с сервисом: {e}")
                raise

        response_dto = CreatedIssueResponseDto(**data)
        return response_dto.issue

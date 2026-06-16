from loguru import logger

from src.task_manager.dto.task_dto import CreateIssueTelegramRequest
from src.task_manager.model.task_entity import TaskEntity
from src.task_manager.repository import task_repository
from src.task_manager.service.jira_client import JiraClient


class TaskService:
    """
    Сервис для управления задачами в Jira.
    """

    def __init__(self):
        self.jira_client = JiraClient()

    async def get_available_projects(self, telegram_id: int, token: str) -> dict[str, str]:
        """
        Получает список доступных проектов для пользователя.

        Args:
            telegram_id: Telegram ID пользователя
            token: Bearer токен для авторизации

        Returns:
            Словарь проектов: название -> URL
        """
        logger.info(f"Получение списка проектов для telegram_id={telegram_id}")
        try:
            projects = await self.jira_client.get_available_projects(telegram_id, token)
            logger.info(f"Найдено {len(projects)} проектов для telegram_id={telegram_id}")
            return projects
        except Exception as e:
            logger.error(f"Ошибка при получении списка проектов: {e}")
            raise

    async def create_task(self, telegram_id: int, project_url: str, text: str, token: str) -> str:
        """
        Создает задачу в Jira.

        Args:
            telegram_id: Telegram ID пользователя
            project_url: URL проекта в Jira
            text: Текст задачи
            token: Bearer токен для авторизации

        Returns:
            URL созданной задачи в Jira
        """
        logger.info(f"Создание задачи для telegram_id={telegram_id}, " f"project_url={project_url}")

        summary, description = self._parse_task_text(text)

        # Формируем DTO для создания задачи
        task_dto = CreateIssueTelegramRequest(
            project=project_url,
            summary=summary,
            description=description,
            reporter_telegram_id=telegram_id,
            assignee_telegram_id=None,
        )

        try:
            # Создаем задачу в Jira
            jira_task_url = await self.jira_client.create_task(task_dto, token)
            logger.info(f"Задача создана в Jira: {jira_task_url}")

            # Сохраняем информацию о задаче в БД
            task_entity = TaskEntity(
                telegram_id=telegram_id,
                project_url=project_url,
                summary=summary,
                description=description,
                reporter=str(telegram_id),
                jira_task_url=jira_task_url,
            )
            task_repository.save(task_entity)

            return jira_task_url

        except Exception as e:
            logger.error(f"Ошибка при создании задачи: {e}")
            raise

    def _parse_task_text(self, text: str) -> tuple[str, str]:
        """
        Парсит текст задачи.
        Первая строка становится заголовком (summary),
        остальное - описанием (description).

        Args:
            text: Текст задачи

        Returns:
            Кортеж (summary, description)
        """
        lines = text.split("\n", 1)

        if len(lines) == 1:
            # Только одна строка - используем её и как заголовок, и как описание
            summary = lines[0].strip()
            description = lines[0].strip()
        else:
            # Первая строка - заголовок, остальное - описание
            summary = lines[0].strip()
            description = text.strip()

        logger.debug(
            f"Парсинг текста: summary='{summary[:50]}...', description длина={len(description)}"
        )

        return summary, description


# Создаем синглтон сервиса
task_service = TaskService()

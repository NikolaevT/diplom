from loguru import logger

from src.task_manager.model.task_entity import TaskEntity


def save(task: TaskEntity) -> None:
    """
    Сохраняет задачу в MongoDB.

    Args:
        task: Entity задачи для сохранения
    """
    try:
        task.save()
        logger.info(
            f"Задача сохранена в БД: telegram_id={task.telegram_id}, "
            f"project_url={task.project_url}, jira_task_url={task.jira_task_url}"
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении задачи в БД: {e}")
        raise

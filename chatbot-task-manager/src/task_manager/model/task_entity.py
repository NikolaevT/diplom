from datetime import datetime

from mongoengine import DateTimeField, Document, IntField, StringField


class TaskEntity(Document):
    """
    Entity модель для задачи в Jira.

    telegram_id: Telegram ID пользователя, создавшего задачу
    project_url: URL проекта в Jira
    summary: Заголовок задачи
    description: Описание задачи
    reporter: Создатель задачи (telegram_id)
    jira_task_url: URL созданной задачи в Jira
    created_at: Дата и время создания задачи
    """

    telegram_id = IntField(required=True)
    project_url = StringField(required=True)
    summary = StringField(required=True)
    description = StringField(required=True)
    reporter = StringField(required=True)
    jira_task_url = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow, required=True)

    meta = {
        "collection": "tasks",
        "indexes": [
            "telegram_id",
            "created_at",
            "-created_at",  # Индекс для сортировки по дате (по убыванию)
        ],
    }

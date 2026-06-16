"""
Тестовые данные для Mock Jira сервиса.

Используется для имитации работы реального Jira API в режиме разработки.
"""

from urllib.parse import urlparse

# Демо-проекты для любого пользователя, которого нет в MOCK_USERS.
# Короткие URL — чтобы callback_data кнопок Telegram укладывалась в 64 байта.
DEFAULT_DEMO_PROJECTS: dict[str, str] = {
    "Демо: Backend": "http://127.0.0.1:8091/p/b",
    "Демо: Frontend": "http://127.0.0.1:8091/p/f",
    "Демо: QA": "http://127.0.0.1:8091/p/q",
}

# Тестовые проекты, доступные разным пользователям
# Формат: telegram_id -> {название_проекта: url_проекта}
MOCK_USERS = {
    # Пользователь с несколькими проектами
    123456789: {
        "Project Alpha": "https://jira.example.com/projects/ALPHA",
        "Development Board": "https://jira.example.com/projects/DEV",
        "Testing Environment": "https://jira.example.com/projects/TEST",
    },
    # Пользователь с одним проектом
    111111111: {
        "Single Project": "https://jira.example.com/projects/SINGLE",
    },
    # Пользователь без проектов (для тестирования ошибки)
    987654321: {},
    # Реальный telegram_id для тестирования
    434200409: {
        "My Dev Project": "https://jira.example.com/projects/MYDEV",
        "Test Project": "https://jira.example.com/projects/TEST",
        "Project Alpha": "https://jira.example.com/projects/ALPHA",
        "Development Board": "https://jira.example.com/projects/DEV",
        "Testing Environment": "https://jira.example.com/projects/TEST2",
    },
}

# Счетчик для генерации уникальных ID задач
task_counter = 1


def get_projects_for_user(telegram_id: int) -> dict[str, str]:
    """
    Возвращает словарь проектов для указанного telegram_id.

    Явные записи в MOCK_USERS имеют приоритет (в т.ч. пустой словарь для негативных тестов).
    Иначе — DEFAULT_DEMO_PROJECTS (удобно для записи демо с любым Telegram-аккаунтом).

    Args:
        telegram_id: Telegram ID пользователя

    Returns:
        Словарь проектов {название: url}
    """
    if telegram_id in MOCK_USERS:
        return MOCK_USERS[telegram_id]
    return DEFAULT_DEMO_PROJECTS


def generate_task_url(project_url: str) -> str:
    """
    Генерирует URL для созданной задачи.

    Args:
        project_url: URL проекта

    Returns:
        URL созданной задачи
    """
    global task_counter
    task_id = f"TASK-{task_counter}"
    task_counter += 1

    parsed = urlparse(project_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}/browse/{task_id}"

    if "jira.example.com" in project_url:
        return f"https://jira.example.com/browse/{task_id}"

    base_url = (
        project_url.split("/projects/")[0] if "/projects/" in project_url else project_url
    )
    return f"{base_url}/browse/{task_id}"

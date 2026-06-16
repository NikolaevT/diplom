from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB настройки
    mongodb_url: str = Field(default=None, description="MongoDB connection string")
    mongodb_name: str = Field(default="task_manager", description="Имя базы данных MongoDB")

    mongodb_collection: str = Field(default="tasks", description="Имя коллекции MongoDB")

    mongodb_username: str | None = Field(default=None, description="MongoDB username (опционально)")
    mongodb_password: str | None = Field(default=None, description="MongoDB password (опционально)")
    mongodb_auth_source: str | None = Field(
        default=None, description="MongoDB auth database (обычно 'admin')"
    )
    mongodb_max_pool_size: int = Field(default=20, description="Максимальное количество соединений")
    mongodb_min_pool_size: int = Field(default=10, description="Минимальное количество соединений")
    mongodb_wait_queue_timeout_ms: int = Field(
        default=1000, description="Время ожидания соединения (мс)"
    )

    # Настройки приложения
    app_name: str = Field(default="Task manager", description="Название приложения")

    debug: bool = Field(default=False, description="Режим отладки")

    environment: str = Field(default="development", description="Окружение приложения")

    # Токен бота
    bot_token: str = Field(default="", description="Токен бота")

    # Разрешенные обновления
    polling_allowed_updates: str = Field(
        default="message,callback_query", description="Разрешенные обновления"
    )

    polling_timeout: int = Field(default=30, description="Таймаут ожидания обновлений")

    polling_request_timeout: int = Field(default=30, description="Таймаут запроса обновлений")

    polling_close_timeout: int = Field(default=10, description="Таймаут закрытия соединения")

    # Интеграция с внешним сервисом
    jira_host: str = Field(default="", description="Base URL сервиса с jira")

    # Локальный mock (dev_tools/mock_jira_service) — демо без доступа к реальному Jira
    jira_use_mock: bool = Field(
        default=True,
        description="Если true, HTTP-клиент Jira ходит на jira_mock_host, а не на jira_host",
    )
    jira_mock_host: str = Field(
        default="http://127.0.0.1:8091",
        description="Base URL mock Jira Integration (make mock-jira)",
    )

    # Chroma DB настройки
    chroma_host: str = Field(default="localhost", description="Хост сервера Chroma DB")
    chroma_port: int = Field(default=8000, description="Порт сервера Chroma DB")
    chroma_collection_name: str = Field(
        default="embeddings", description="Имя коллекции для векторов"
    )

    # Настройки модели векторизации
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="Название модели для векторизации текста",
    )

    # IDM / OIDC настройки
    idm_sso_url: str = Field(
        default="https://auth.bmc-soft.ru/realms/bmc-soft/auth",
        description="URL страницы SSO авторизации",
    )
    idm_redirect_uri: str = Field(
        default="",
        description=(
            "Redirect URI для callback после авторизации. "
            "Должен содержать плейсхолдер {telegram_id}, например: "
            "https://our-backend/api/v1/auth/oidc/callback?telegram_id={telegram_id}"
        ),
    )

    # Сервисы БМКИТ
    svc_raccoon_url: str = Field(
        default="https://it.dev.bmc-soft.ru/svc-raccoon",
        description="Base URL сервиса svc-raccoon для обмена code на токен",
    )
    svc_lion_url: str = Field(
        default="https://it.dev.bmc-soft.ru/svc-lion",
        description="Base URL сервиса svc-lion для получения данных пользователя (identity)",
    )

    # Учетные данные для авторизации (используются для всех задач)
    auth_login: str = Field(
        default="",
        description="Логин (email) для авторизации в системе",
    )
    auth_password: str = Field(
        default="",
        description="Пароль для авторизации в системе",
    )

    # FastAPI настройки
    host: str = Field(default="0.0.0.0", description="Хост для FastAPI сервера")
    port: int = Field(default=8080, description="Порт для FastAPI сервера")

    # LLM (vLLM, OpenAI-compatible API)
    vllm_base_url: str = Field(
        default="",
        description="Base URL vLLM, например http://10.45.0.75:8000/v1",
    )
    vllm_api_key: str = Field(
        default="not-needed",
        description="API key для vLLM (если не требуется — not-needed)",
    )
    llm_model_name: str = Field(
        default="Qwen/Qwen3.5-9B",
        description="Имя модели на vLLM, например Qwen/Qwen3.6-35B-A3B-FP8",
    )
    llm_temperature: float = Field(
        default=0.7,
        description="Температура генерации для LLM (0.0-1.0)",
    )
    llm_reasoning: bool = Field(
        default=False,
        description="Включить reasoning/thinking у модели (False — быстрее для CrewAI JSON)",
    )
    llm_max_tokens: int = Field(
        default=5000,
        description="Максимум токенов в ответе LLM",
    )
    agent_request_limit: int = Field(
        default=30,
        description="max_iter агента CrewAI (лимит итераций LLM на задачу)",
    )
    agent_tool_calls_limit: int = Field(
        default=10,
        description="Лимит tool calls агента CrewAI",
    )

    # Настройка логов OpenSearch
    opensearch_hosts: list[str] = Field(
        default_factory=lambda: ["https://opensearch.dev.bmc-soft.ru"],
        description="Список хостов OpenSearch в формате ['https://hostname']",
    )
    opensearch_username: str = Field(default="admin", description="Логин")
    opensearch_password: str = Field(default="admin", description="Пароль")
    opensearch_index_prefix: str = Field(
        default="chatbot-task-manager",
        description="Префикс для индексов логов в OpenSearch",
    )

    # ВАЖНО: Эта настройка включает чтение .env файла
    model_config = SettingsConfigDict(
        env_file=".env",  # Читает .env файл из корня проекта
        env_file_encoding="utf-8",
        case_sensitive=False,  # MONGODB_URL == mongodb_url
        extra="ignore",
    )

    # Настройки для распознавания голосовых
    tmp_voice_dir: Path = Path("/tmp/voice_bot")


settings = Settings()

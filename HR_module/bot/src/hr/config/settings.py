from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Токен Telegram бота
    bot_token: str = Field(..., description="Токен Telegram бота")

    # Настройки приложения
    app_name: str = Field(default="HR Module", description="Название приложения")
    debug: bool = Field(default=False, description="Режим отладки")
    host: str = Field(default="0.0.0.0", description="Хост FastAPI")
    port: int = Field(default=8091, description="Порт FastAPI")

    # MongoDB настройки
    mongodb_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB connection string"
    )
    mongodb_name: str = Field(default="hr_module", description="Имя базы данных MongoDB")

    # Параметры polling
    polling_allowed_updates: str = Field(
        default="message,callback_query", description="Разрешенные типы Telegram updates"
    )
    polling_timeout: int = Field(default=30, description="Таймаут long polling")
    polling_request_timeout: int = Field(default=30, description="Таймаут HTTP-запроса polling")
    polling_close_timeout: int = Field(default=10, description="Таймаут остановки polling")

    # Mock БМК-ИТ
    bmk_it_host: str = Field(default="http://127.0.0.1:8088", description="Base URL mock БМК-ИТ")

    # Реквизиты для сдачи документов (уровень 4)
    documents_email: str = Field(
        default="hr-docs@example.com",
        description="Email для отправки документов по почте",
    )
    office_address: str = Field(
        default="ул. Бассейна 1, офис 1",
        description="Адрес офиса для передачи документов лично",
    )
    office_hours: str = Field(
        default="Пн–Пт 9:00–18:00",
        description="Часы работы бухгалтерии",
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "bot/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

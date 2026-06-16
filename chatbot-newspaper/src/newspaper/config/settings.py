from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB connection string"
    )
    mongodb_database: str = Field(default="newspaper", description="Имя базы данных MongoDB")

    bot_token: str = Field(default="", description="Токен бота")

    app_name: str = Field(default="Chatbot Newspaper", description="Название приложения")

    debug: bool = Field(default=False, description="Режим отладки")

    host: str = Field(default="0.0.0.0", description="Хост для FastAPI сервера")
    port: int = Field(default=8080, description="Порт для FastAPI сервера")

    chat_id: str = Field(default="", description="ID чата для отправки новостей")

    recipient_api_url: str = Field(
        default="http://localhost:9090/api/v1/recipients",
        description="Эндпоинт для регистрации получателей",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()

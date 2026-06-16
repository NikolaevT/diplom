from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(default="", description="Токен Telegram-бота")
    admin_ids: str = Field(default="", description="ID администраторов через запятую")
    database_path: str = Field(default="birthdays.db", description="Путь к SQLite БД")
    timezone: str = Field(default="Europe/Moscow", description="Часовой пояс планировщика")
    app_name: str = Field(default="Chatbot Begemot", description="Название приложения")
    environment: str = Field(default="development", description="Окружение")
    debug: bool = Field(default=False, description="Режим отладки")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def admin_id_list(self) -> list[int]:
        if not self.admin_ids.strip():
            return []
        return [int(item.strip()) for item in self.admin_ids.split(",") if item.strip()]


settings = Settings()

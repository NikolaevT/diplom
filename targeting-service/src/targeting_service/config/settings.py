from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="Targeting Service", description="Название приложения")

    debug: bool = False
    port: int = 8080
    log_level: str = Field(default="INFO", description="Уровень логирования")

    db_host: str = Field(default="127.0.0.1", description="Хост PostgreSQL")
    db_port: int = Field(default=55432, description="Порт PostgreSQL")
    db_name: str = Field(default="targeting_service", description="Имя базы данных")
    db_user: str = Field(default="targeting_user", description="Пользователь БД")
    db_password: str = Field(default="change_me", description="Пароль пользователя БД")

    bot_base_url: str = Field(default="http://127.0.0.1:8080", description="URL сервиса бота")
    identity_url: str = Field(
        default="https://it.dev.bmc-soft.ru/svc-lion/v1/identity",
        description="URL сервиса проверки токена (BAP_Bearer)",
    )


settings = Settings()

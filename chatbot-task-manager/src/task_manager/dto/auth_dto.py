from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """DTO для запроса авторизации по логину и паролю."""

    login: str = Field(..., description="Логин (email) пользователя")
    password: str = Field(..., description="Пароль пользователя")
    telegram_id: str = Field(..., description="Telegram ID пользователя")

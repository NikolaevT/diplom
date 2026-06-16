from pydantic import BaseModel, Field


class UserDto(BaseModel):
    """
    DTO для User.
    """

    telegram_id: str = Field(..., description="Идентификатор пользователя в Telegram")
    bmk_id: str = Field(..., description="Идентификатор пользователя в БМК-ИТ")
    class_id: str = Field(..., description="Идентификатор класса пользователя")

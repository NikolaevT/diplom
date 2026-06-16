from pydantic import BaseModel, Field
from pydantic import ConfigDict


class RecipientDto(BaseModel):
    """
    dto для Telegram-бота (получателей новостей).
    """

    model_config = ConfigDict(populate_by_name=True)

    telegram_id: str = Field(
        ..., description="Telegram ID пользователя, чата или канала", alias="telegramId"
    )
    name: str | None = Field(default=None, description="Имя пользователя/чата")
    type: str = Field(..., description="Тип: user / group / channel и т.п.")
    is_admin: bool = Field(
        default=False, description="Является ли пользователь администратором", alias="isAdmin"
    )

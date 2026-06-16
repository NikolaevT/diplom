from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CandidateDto(BaseModel):
    """Данные кандидата, которые отправляются в БМК-ИТ."""

    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(..., alias="fullName")
    birth_date: str = Field(..., alias="birthDate")
    email: str
    telegram_id: str = Field(..., alias="telegramId")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: str) -> str:
        value = value.strip()
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError as e:
            msg = "Дата рождения должна быть в формате ДД.ММ.ГГГГ"
            raise ValueError(msg) from e
        return value

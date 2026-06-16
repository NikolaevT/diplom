from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CandidateRequest(BaseModel):
    """Регистрация кандидата из Telegram-бота."""

    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(..., alias="fullName")
    birth_date: str = Field(
        ...,
        alias="birthDate",
        description="Дата рождения в формате ДД.ММ.ГГГГ"
    )
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


class CandidateResponse(CandidateRequest):
    """Профиль кандидата, сохраненный в mock БМК-ИТ."""

    pass


class AppointmentActionRequest(BaseModel):
    """Подтверждение или отмена собеседования (вызов от HR middleware)."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_id: str = Field(
        ...,
        alias="appointmentId",
        description="Уникальный ID собеседования в БМК-ИТ (задаёт HR при создании, например apt-1)",
    )
    telegram_id: str = Field(..., alias="telegramId")


class AppointmentRescheduleRequest(BaseModel):
    """Перенос собеседования."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_id: str = Field(
        ...,
        alias="appointmentId",
        description="Уникальный ID собеседования в БМК-ИТ (задаёт HR при создании, например apt-1)",
    )
    telegram_id: str = Field(..., alias="telegramId")
    reason: str
    new_date: str = Field(..., alias="newDate")


class OfferActionRequest(BaseModel):
    """Принятие или отклонение оффера."""

    model_config = ConfigDict(populate_by_name=True)

    offer_id: str = Field(..., alias="offerId")
    telegram_id: str = Field(..., alias="telegramId")


class ScheduleAppointmentRequest(BaseModel):
    """Назначение собеседования HR-специалистом."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_id: str = Field(
        ...,
        alias="appointmentId",
        description="Уникальный ID собеседования в БМК-ИТ (задаёт HR при создании, например apt-1)",
    )
    telegram_id: str = Field(..., alias="telegramId")
    date: str
    time: str
    location: str


class ScheduleAppointmentResponse(ScheduleAppointmentRequest):
    """Сохранённое назначение собеседования."""

    pass


class OfferNotifyRequest(BaseModel):
    """Данные для отправки оффера кандидату через middleware."""

    model_config = ConfigDict(populate_by_name=True)

    offer_id: str = Field(..., alias="offerId")
    telegram_id: str = Field(..., alias="telegramId")
    file_url: str = Field(..., alias="fileUrl")
    file_name: str = Field(default="Offer.pdf", alias="fileName")


class OfferResponse(OfferNotifyRequest):
    """Сохранённый оффер."""

    pass


class InstructionNotifyRequest(BaseModel):
    """Данные для отправки инструкции кандидату через middleware."""

    model_config = ConfigDict(populate_by_name=True)

    instruction_id: str = Field(..., alias="instructionId")
    telegram_id: str = Field(..., alias="telegramId")
    file_url: str = Field(..., alias="fileUrl")
    file_name: str = Field(default="Instruction.pdf", alias="fileName")


class InstructionResponse(InstructionNotifyRequest):
    """Сохранённая инструкция."""

    pass


class ActionResponse(BaseModel):
    """Унифицированный ответ mock API."""

    success: bool = True
    message: str

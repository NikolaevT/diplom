from pydantic import BaseModel, ConfigDict, Field


class AppointmentDto(BaseModel):
    """Данные назначенного собеседования от БМК-ИТ."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_id: str = Field(..., alias="appointmentId")
    telegram_id: str = Field(..., alias="telegramId")
    date: str
    time: str
    location: str


class AppointmentActionDto(BaseModel):
    """Подтверждение или отмена собеседования."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_id: str = Field(..., alias="appointmentId")
    telegram_id: str = Field(..., alias="telegramId")


class AppointmentRescheduleDto(AppointmentActionDto):
    """Запрос на перенос собеседования."""

    reason: str
    new_date: str = Field(..., alias="newDate")

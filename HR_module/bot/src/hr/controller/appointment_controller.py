from fastapi import APIRouter

from src.hr.dto import AppointmentDto
from src.hr.service.appointment_service import notify_appointment

router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["appointments"],
)


@router.post("")
async def receive_appointment(appointment: AppointmentDto):
    """Принимает назначение собеседования от БМК-ИТ и отправляет его в Telegram."""
    return await notify_appointment(appointment)

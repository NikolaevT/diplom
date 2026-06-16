from aiogram.exceptions import TelegramBadRequest
from fastapi import HTTPException
from loguru import logger

from src.hr.dto import AppointmentDto
from src.hr.service.telegram_client import telegram_client


async def notify_appointment(appointment: AppointmentDto) -> dict:
    """
    Принимает данные о собеседовании от БМК-ИТ и отправляет сообщение кандидату.
    """
    try:
        message_id = await telegram_client.send_appointment(appointment)
    except TelegramBadRequest as e:
        err_text = str(e).lower()
        if "chat not found" in err_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Chat not found (telegramId={appointment.telegram_id}). "
                    "Кандидат должен начать диалог с ботом через /start."
                ),
            ) from e
        logger.error(f"Telegram API error: {e}")
        raise HTTPException(status_code=400, detail=str(e) or "Telegram API error") from e

    return {
        "success": True,
        "message": "Собеседование отправлено кандидату",
        "messageId": message_id,
        "appointmentId": appointment.appointment_id,
        "telegramId": appointment.telegram_id,
    }

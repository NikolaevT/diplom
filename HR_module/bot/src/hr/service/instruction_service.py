from aiogram.exceptions import TelegramBadRequest
from fastapi import HTTPException
from loguru import logger

from src.hr.dto import InstructionDto
from src.hr.service.offer_service import _download_file
from src.hr.service.telegram_client import telegram_client


async def notify_instruction(instruction: InstructionDto) -> dict:
    """Скачивает файл инструкции и отправляет его кандидату в Telegram."""
    try:
        file_bytes = await _download_file(instruction.file_url)
    except Exception as e:
        logger.error(f"Не удалось скачать инструкцию с {instruction.file_url}: {e!r}")
        raise HTTPException(status_code=400, detail="Cannot download instruction file") from e

    try:
        message_id = await telegram_client.send_instruction(instruction, file_bytes)
    except TelegramBadRequest as e:
        err_text = str(e).lower()
        if "chat not found" in err_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Chat not found (telegramId={instruction.telegram_id}). "
                    "Кандидат должен начать диалог с ботом через /start."
                ),
            ) from e
        raise HTTPException(status_code=400, detail=str(e) or "Telegram API error") from e

    return {
        "success": True,
        "message": "Инструкция отправлена кандидату",
        "messageId": message_id,
        "instructionId": instruction.instruction_id,
        "telegramId": instruction.telegram_id,
    }

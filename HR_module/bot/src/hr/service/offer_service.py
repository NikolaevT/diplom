import httpx
from aiogram.exceptions import TelegramBadRequest
from fastapi import HTTPException
from loguru import logger

from src.hr.dto import OfferDto
from src.hr.service.telegram_client import telegram_client


async def _download_file(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


async def notify_offer(offer: OfferDto) -> dict:
    """Скачивает файл оффера и отправляет его кандидату в Telegram."""
    try:
        file_bytes = await _download_file(offer.file_url)
    except httpx.HTTPError as e:
        logger.error(f"Не удалось скачать оффер с {offer.file_url}: {e!r}")
        raise HTTPException(status_code=400, detail="Cannot download offer file") from e

    try:
        message_id = await telegram_client.send_offer(offer, file_bytes)
    except TelegramBadRequest as e:
        err_text = str(e).lower()
        if "chat not found" in err_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Chat not found (telegramId={offer.telegram_id}). "
                    "Кандидат должен начать диалог с ботом через /start."
                ),
            ) from e
        raise HTTPException(status_code=400, detail=str(e) or "Telegram API error") from e

    return {
        "success": True,
        "message": "Оффер отправлен кандидату",
        "messageId": message_id,
        "offerId": offer.offer_id,
        "telegramId": offer.telegram_id,
    }

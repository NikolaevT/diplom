import aiohttp
from aiogram.exceptions import TelegramBadRequest
from fastapi import HTTPException
from loguru import logger

from src.newspaper.config import settings
from src.newspaper.dto import NewsArticleDto
from src.newspaper.mapper.newspaper_mapper import NewsArticleMapper
from src.newspaper.repository.news_article_repository import save
from src.newspaper.service import telegram_client


async def _download_image_bytes(url: str) -> bytes | None:
    """
    Скачивает изображение по URL и возвращает его байтовое представление.
    Возвращает None, если скачать картинку не удалось.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"Не удалось скачать изображение с {url}: HTTP {resp.status}")
                    return None

                data = await resp.read()
        return data
    except Exception as e:
        logger.warning(f"Не удалось скачать изображение с {url}: {e}")
    return None


async def receive(news_article: NewsArticleDto):
    """
    Получает DTO новости, конвертирует в entity, отправляет в Telegram и сохраняет в БД.
    Args:
        news_article: DTO с данными новости
    Returns:
        NewsArticleDto: DTO сохраненной новости с message_id из Telegram
    """
    entity = NewsArticleMapper.to_entity(news_article)
    raw_chat = (
        news_article.telegram_id if news_article.telegram_id is not None else settings.chat_id
    )
    chat_id = str(raw_chat).strip() if raw_chat else ""
    if not chat_id:
        raise HTTPException(
            status_code=400,
            detail="chat_id is required: provide telegramId in request body or set CHAT_ID in .env",
        )
    entity.chat_id = chat_id

    if news_article.image_url:
        entity.image_bytes = await _download_image_bytes(news_article.image_url)

    # Отправляем в Telegram и получаем message_id
    try:
        message_id = await telegram_client.send_message(news=entity, chat_id=chat_id)
    except TelegramBadRequest as e:
        err_text = str(e).lower()
        if "chat not found" in err_text:
            raise HTTPException(
                status_code=400,
                detail=f"Chat not found (telegram_id={chat_id}). "
                f"Add the bot to the group/channel or check that the chat id is correct.",
            ) from e
        raise HTTPException(status_code=400, detail=str(e) or "Telegram API error") from e

    # Обновляем entity с полученным message_id
    entity.message_id = message_id

    saved = save(entity)

    return NewsArticleMapper.to_dto(saved)



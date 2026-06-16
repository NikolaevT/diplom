"""Клиент для отправки постов в бот."""

from loguru import logger
from httpx import Client

from src.targeting_service.config import settings
from src.targeting_service.dto.distribution_dto import BotNewsRequest, PostDto


def post_news(post: PostDto, telegram_id: str) -> dict:
    """POST в /api/v1/news бота. Одна новость — один получатель (chat_id)."""
    body = BotNewsRequest(
        image_url=post.image_url,
        content=post.content,
        source_url=post.source_url,
        telegram_id=telegram_id,
    )
    base = settings.bot_base_url.rstrip("/")
    url = f"{base}/api/v1/news"
    logger.debug("POST /api/v1/news: url={}, telegram_id={}", url, telegram_id)
    with Client(timeout=25.0) as client:
        response = client.post(url, json=body.model_dump(by_alias=True, exclude_none=True))
        if not response.is_success:
            logger.error(
                "Bot news API error: status={}, body={}",
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        return response.json() if response.content else {}

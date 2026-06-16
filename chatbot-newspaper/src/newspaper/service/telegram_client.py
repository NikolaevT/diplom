from aiogram import Bot
from aiogram.types import BufferedInputFile, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from src.newspaper.config import settings
from src.newspaper.model import NewsArticleEntity


class TelegramClient:
    """
    Клиент для работы с Telegram API.
    Отвечает за размещение сообщений с новостями.
    """

    MAX_CAPTION_LENGTH = 1024

    def __init__(self) -> None:
        self.bot = Bot(token=settings.bot_token)

    async def close(self) -> None:
        await self.bot.close()

    def _create_keyboard(self, source_url: str | None):
        """
        Создает клавиатуру с кнопкой для перехода по ссылке.
        Returns None, если source_url пустой.
        """
        if not source_url or not source_url.strip():
            return None
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔗 Читать полностью", url=source_url))
        return keyboard.as_markup()

    async def send_message(self, news: NewsArticleEntity, chat_id: str) -> int:
        """
        Отправляет новость в Telegram чат.
        Контент передаётся как есть (заказчик сам форматирует через \\n и т.п.).
        С фото — если есть image_bytes. Без фото — обычное текстовое сообщение.
        """
        content = news.content
        reply_markup = self._create_keyboard(news.source_url)

        if news.image_bytes:
            photo = BufferedInputFile(file=news.image_bytes, filename="photo.jpg")
            caption = (
                content[: self.MAX_CAPTION_LENGTH]
                if len(content) > self.MAX_CAPTION_LENGTH
                else content
            )
            message: Message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup,
            )
        else:
            message: Message = await self.bot.send_message(
                chat_id=chat_id,
                text=content,
                reply_markup=reply_markup,
            )

        logger.debug(
            f"Новость отправлена. Chat ID: {chat_id}, Message ID: {message.message_id}"
        )
        return message.message_id

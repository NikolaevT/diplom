import asyncio
from contextlib import asynccontextmanager
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from loguru import logger

from src.newspaper.config import settings
from src.newspaper.config.database import MongoDBConnection
from src.newspaper.controller.newspaper_article_controller import router as newspaper_router
from src.newspaper.handlers.recipient_handler import router as recipient_handler_router

BOT_TOKEN = settings.bot_token.strip() if settings.bot_token else None
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменных окружения. "
        "Установите переменную BOT_TOKEN перед запуском бота."
    )

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Подключаем aiogram хендлеры
dp.include_router(recipient_handler_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    MongoDBConnection.connect()
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(
        dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            handle_signals=False,
        )
    )
    logger.info("Telegram polling запущен")

    yield

    # Shutdown
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()
    MongoDBConnection.disconnect()
    logger.info("Приложение остановлено")


app = FastAPI(lifespan=lifespan)
app.include_router(newspaper_router)

def main() -> None:
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

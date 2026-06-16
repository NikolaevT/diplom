import asyncio
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from loguru import logger

from src.hr.adapter.fsm_storage import MongoDBStorage
from src.hr.bot_instance import init_bot
from src.hr.config import settings
from src.hr.config.database import connect, disconnect
from src.hr.controller.appointment_controller import router as appointment_router
from src.hr.controller.instruction_controller import router as instruction_router
from src.hr.controller.offer_controller import router as offer_router
from src.hr.handlers import (
    appointment_handler_router,
    document_handler_router,
    offer_handler_router,
    registration_router,
)

BOT_TOKEN = settings.bot_token.strip() if settings.bot_token else None
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменных окружения. "
        "Установите переменную BOT_TOKEN перед запуском бота."
    )

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MongoDBStorage()
dp = Dispatcher(storage=storage)

_polling_task: asyncio.Task | None = None


def register_routers() -> None:
    """Регистрирует aiogram роутеры."""
    dp.include_router(appointment_handler_router)
    dp.include_router(offer_handler_router)
    dp.include_router(document_handler_router)
    dp.include_router(registration_router)


def get_polling_config() -> dict:
    """Загружает параметры polling из настроек."""
    allowed_updates = None
    if settings.polling_allowed_updates:
        allowed_updates = [
            update.strip()
            for update in settings.polling_allowed_updates.split(",")
            if update.strip()
        ]

    return {
        "timeout": settings.polling_timeout,
        "request_timeout": settings.polling_request_timeout,
        "close_timeout": settings.polling_close_timeout,
        "allowed_updates": allowed_updates,
    }


init_bot(bot)


async def start_bot() -> None:
    """Запускает Telegram polling."""
    logger.info("Запуск Telegram бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    register_routers()

    polling_config = get_polling_config()
    global _polling_task
    _polling_task = asyncio.create_task(
        dp.start_polling(
            bot,
            timeout=polling_config["timeout"],
            request_timeout=polling_config["request_timeout"],
            close_timeout=polling_config["close_timeout"],
            allowed_updates=polling_config["allowed_updates"],
            handle_signals=False,
        )
    )
    logger.info("Telegram polling запущен")


async def stop_bot() -> None:
    """Останавливает Telegram polling."""
    global _polling_task
    if _polling_task and not _polling_task.done():
        logger.info("Остановка Telegram polling...")
        await dp.stop_polling()
        try:
            await asyncio.wait_for(_polling_task, timeout=10.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            _polling_task.cancel()
            try:
                await _polling_task
            except asyncio.CancelledError:
                pass
    await bot.session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect()
    await start_bot()
    logger.info("HR Module запущен")

    yield

    await stop_bot()
    disconnect()
    logger.info("HR Module остановлен")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(appointment_router)
app.include_router(offer_router)
app.include_router(instruction_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


def main() -> None:
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()

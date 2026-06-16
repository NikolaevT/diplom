import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from loguru import logger

from src.task_manager.adapter.fsm_storage import MongoDBStorage
from src.task_manager.bot_instance import init_bot
from src.task_manager.config.database import connect, disconnect
from src.task_manager.config.settings import settings
from src.task_manager.controller.auth_controller import router as auth_api_router
from src.task_manager.handlers import auth_router, help_router, message_router, task_handler
from src.task_manager.opensearch.logging_service import setup_logging
from src.task_manager.whisper_model_instance import init_whisper_model

setup_logging()
BOT_TOKEN = settings.bot_token.strip() if settings.bot_token else None
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменных окружения. "
        "Установите переменную BOT_TOKEN перед запуском бота."
    )

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MongoDBStorage()
dp = Dispatcher(storage=storage)

# Флаг для отслеживания состояния polling
_polling_task: asyncio.Task | None = None


def get_bot() -> Bot:
    return bot


def register_routers() -> None:
    """Регистрирует все роутеры в диспетчере."""
    dp.include_router(task_handler.router)
    dp.include_router(auth_router)
    dp.include_router(help_router)
    dp.include_router(message_router)


def get_polling_config() -> dict:
    """Загружает параметры polling из переменных окружения."""
    allowed_updates = None
    if settings.polling_allowed_updates:
        allowed_updates = [
            update.strip()
            for update in settings.polling_allowed_updates.split(",")
            if update.strip()
        ]

    return {
        "timeout": int(settings.polling_timeout),
        "request_timeout": int(settings.polling_request_timeout),
        "close_timeout": int(settings.polling_close_timeout),
        "allowed_updates": allowed_updates,
    }


# Инициализация глобального экземпляра бота
init_bot(bot)

# Создание MongoDB storage для FSM
storage = MongoDBStorage()


async def main() -> None:
    """Основная функция для запуска бота."""
    logger.info("Запуск Telegram бота...")

    # Подключение к MongoDB
    logger.info("Подключение к MongoDB...")
    connect()
    logger.info(f"MongoDB подключен: {settings.mongodb_url}/{settings.mongodb_name}")

    # Подключение к Chroma DB
    logger.info("Подключение к Chroma DB...")
    # ChromaDBConnection.connect()
    logger.info(
        f"Chroma DB подключен: {settings.chroma_host}:{settings.chroma_port}/"
        f"{settings.chroma_collection_name}"
    )

    # Инициализация модели Whisper
    logger.info("Инициализация модели Whisper...")
    await asyncio.to_thread(init_whisper_model)
    logger.info("Модель Whisper инициализирована")

    # Проверка подключения к боту
    bot_info = await bot.get_me()
    logger.info(f"Бот подключен: @{bot_info.username} (ID: {bot_info.id})")

    # Регистрация роутеров
    register_routers()
    logger.info("Роутеры зарегистрированы")

    polling_config = get_polling_config()
    logger.info(
        f"Запуск polling с параметрами: "
        f"timeout={polling_config['timeout']}s, "
        f"request_timeout={polling_config['request_timeout']}s"
    )

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
    logger.info("Polling бота запущен")


async def stop_bot():
    """остановка бота."""
    global _polling_task
    if _polling_task and not _polling_task.done():
        logger.info("Остановка polling бота...")
        await dp.stop_polling()
        try:
            await asyncio.wait_for(_polling_task, timeout=10.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            _polling_task.cancel()
            try:
                await _polling_task
            except asyncio.CancelledError:
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan - менеджер жизненного цикла FastAPI.
    Выполняется при запуске и остановке приложения.
    """
    connect()
    # ChromaDBConnection.connect()
    await main()
    logger.info("Все запущено")

    yield

    await stop_bot()
    disconnect()
    # ChromaDBConnection.disconnect()

    logger.info("Все остановлено")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth_api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)

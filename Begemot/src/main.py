import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from src.begemot.bot_instance import init_bot
from src.begemot.config.database import init_db
from src.begemot.config.settings import settings
from src.begemot.handlers import get_all_routers
from src.begemot.service.reminder_service import ReminderService

BOT_TOKEN = settings.bot_token.strip() if settings.bot_token else None
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не найден в переменных окружения. "
        "Установите переменную BOT_TOKEN перед запуском бота."
    )

bot = Bot(token=BOT_TOKEN)
init_bot(bot)

dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()
reminder_service = ReminderService(bot)


def register_routers() -> None:
    for router in get_all_routers():
        dp.include_router(router)
    logger.info("Роутеры зарегистрированы")


async def on_startup() -> None:
    if not settings.admin_id_list:
        logger.warning("ADMIN_IDS не указаны в .env — планировщик напоминаний не запущен")
        return

    scheduler.add_job(
        reminder_service.send_birthday_reminder,
        "cron",
        hour=1,
        minute=30,
        timezone=settings.timezone,
    )
    scheduler.add_job(
        reminder_service.send_monthly_birthdays,
        "cron",
        day=1,
        hour=10,
        minute=0,
        timezone=settings.timezone,
    )
    scheduler.start()
    logger.info("Планировщик напоминаний запущен")
    await reminder_service.send_birthday_reminder()


async def on_shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown()


async def main() -> None:
    init_db()
    register_routers()

    bot_info = await bot.get_me()
    logger.info(f"Бот подключен: @{bot_info.username} (ID: {bot_info.id})")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

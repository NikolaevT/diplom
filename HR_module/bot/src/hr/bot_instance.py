from aiogram import Bot

_bot: Bot | None = None


def init_bot(bot: Bot) -> None:
    """Инициализирует глобальный экземпляр Telegram-бота."""
    global _bot
    _bot = bot


def get_bot() -> Bot:
    """Возвращает глобальный экземпляр Telegram-бота."""
    if _bot is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() перед get_bot()")
    return _bot

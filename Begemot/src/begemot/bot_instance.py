from aiogram import Bot

_bot: Bot | None = None


def init_bot(bot: Bot) -> None:
    global _bot
    _bot = bot


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot не инициализирован. Вызовите init_bot() перед использованием.")
    return _bot

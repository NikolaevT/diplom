"""
Модуль для централизованного доступа к экземпляру Telegram бота.
Позволяет избежать циклических импортов и предоставляет единую точку доступа к боту.
"""

from aiogram import Bot

# Глобальная переменная для хранения экземпляра бота
_bot: Bot | None = None


def init_bot(bot: Bot) -> None:
    """
    Инициализирует глобальный экземпляр бота.

    Args:
        bot: Экземпляр aiogram.Bot
    """
    global _bot
    _bot = bot


def get_bot() -> Bot:
    """
    Возвращает глобальный экземпляр бота.

    Returns:
        Bot: Экземпляр aiogram.Bot

    Raises:
        RuntimeError: Если бот не был инициализирован через init_bot()
    """
    if _bot is None:
        raise RuntimeError(
            "Бот не инициализирован. Вызовите init_bot() перед использованием get_bot()"
        )
    return _bot

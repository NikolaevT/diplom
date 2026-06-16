"""Настройка логирования через loguru."""

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Перехватчик стандартных логов Python для перенаправления в loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Перехватывает лог-запись и отправляет её в loguru."""
        # Получаем соответствующий уровень loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим фрейм вызова
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(log_level: str = "INFO") -> None:
    """
    Настраивает логирование через loguru с перехватом стандартных логов.

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Удаляем стандартный обработчик loguru
    logger.remove()

    # Добавляем свой обработчик с форматированием
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Перехватываем стандартные логи Python (для uvicorn, FastAPI и т.д.)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Перехватываем логи конкретных библиотек
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(f"Логирование настроено с уровнем {log_level}")

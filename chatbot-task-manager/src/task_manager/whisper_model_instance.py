"""
Модуль для централизованного доступа к экземпляру модели Whisper.
Позволяет избежать циклических импортов и предоставляет единую точку доступа к модели.
"""

from faster_whisper import WhisperModel
from loguru import logger

# Глобальная переменная для хранения экземпляра модели
_whisper_model: WhisperModel | None = None


def init_whisper_model() -> None:
    """
    Инициализирует глобальный экземпляр модели Whisper.
    Модель создается с оптимизацией для CPU.
    """
    global _whisper_model
    if _whisper_model is None:
        logger.info("Загрузка модели Faster-Whisper...")
        _whisper_model = WhisperModel(
            model_size_or_path="small",
            device="cpu",
            compute_type="int8",  # Квантизация для экономии памяти
            cpu_threads=4,  # Оптимизация для CPU
            num_workers=1,
        )
        logger.info("Модель Faster-Whisper успешно загружена")


def get_whisper_model() -> WhisperModel:
    """
    Возвращает глобальный экземпляр модели Whisper.

    Returns:
        WhisperModel: Экземпляр модели Faster-Whisper

    Raises:
        RuntimeError: Если модель не была инициализирована через init_whisper_model()
    """
    if _whisper_model is None:
        raise RuntimeError(
            "Модель Whisper не инициализирована. "
            "Вызовите init_whisper_model() перед использованием get_whisper_model()"
        )
    return _whisper_model

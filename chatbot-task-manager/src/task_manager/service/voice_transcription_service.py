from typing import Optional

from aiogram import Bot
from aiogram.types import Voice
from loguru import logger

from src.task_manager.config import settings
from src.task_manager.dto.chat_summary import TaskSummary
from src.task_manager.flow.crews.task_summary_crew import TaskSummaryCrew
from src.task_manager.whisper_model_instance import get_whisper_model


class VoiceTranscriptionService:
    """
    Сервис для транскрипции голосовых сообщений с использованием Faster-Whisper.
    Использует глобальный экземпляр модели Whisper.
    """

    _instance: Optional["VoiceTranscriptionService"] = None

    def __new__(cls) -> "VoiceTranscriptionService":
        """Singleton pattern для сервиса."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_task_summary(self, bot: Bot, voice: Voice) -> TaskSummary:
        task_text = await self._transcribe_voice_file(bot=bot, voice=voice)

        crew_result = (
            TaskSummaryCrew()
            .crew()
            .kickoff(
                inputs={
                    "text": task_text,
                }
            )
        )

        return crew_result.pydantic

    async def _transcribe_voice_file(self, bot: Bot, voice: Voice) -> str:
        """
        Транскрибирует голосовое сообщение в текст.

        Args:
            bot: Экземпляр бота для скачивания файла
            voice: Объект Voice из сообщения Telegram

        Returns:
            str: Транскрибированный текст

        Raises:
            Exception: При ошибках скачивания, транскрипции или других проблемах
        """
        # Получаем глобальный экземпляр модели
        whisper_model = get_whisper_model()

        # Создаем временную директорию если её нет
        tmp_dir = settings.tmp_voice_dir
        tmp_dir.mkdir(exist_ok=True)

        # Генерируем уникальное имя файла
        file_id = voice.file_id
        ogg_path = tmp_dir / f"{file_id}.ogg"

        try:
            logger.info(f"Скачивание голосового сообщения: {file_id}")

            # Скачиваем файл
            await bot.download(voice, destination=ogg_path)

            # Транскрибируем напрямую из OGG
            logger.info(f"Транскрибирование аудио: {ogg_path}")
            segments, _ = whisper_model.transcribe(
                str(ogg_path),
                language="ru",
                beam_size=1,  # Ускоряет обработку
                vad_filter=True,  # Фильтрация тишины
            )

            # Собираем текст из сегментов
            transcription = " ".join([segment.text.strip() for segment in segments])

            if not transcription:
                raise ValueError("Не удалось распознать речь. Попробуйте записать сообщение четче.")

            logger.info(f"Транскрипция завершена: {len(transcription)} символов")
            return transcription

        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}", exc_info=True)
            raise

        finally:
            # Удаляем временный файл
            try:
                if ogg_path.exists():
                    ogg_path.unlink()
                    logger.debug(f"Удален временный файл: {ogg_path}")
            except Exception as exc:
                logger.warning(f"Не удалось удалить временные файлы: {exc}")


# Singleton экземпляр сервиса
voice_transcription_service = VoiceTranscriptionService()

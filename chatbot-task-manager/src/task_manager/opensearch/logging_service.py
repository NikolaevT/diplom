import logging
from typing import Any

from loguru import logger as loguru_logger

from src.task_manager.opensearch.open_search_handler import create_opensearch_handler


def attach_handler_to_loggers(handler: logging.Handler) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    for name in [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "crewai",
        "crewai.agents",
        "crewai.tasks",
    ]:
        logging.getLogger(name).addHandler(handler)

    return root_logger


def forward_log_record_to_standard_logging(message: Any) -> None:
    """
    Пересылает логи в стандартный logging для отправки в OpenSearch.
    
    В loguru sink функция получает Message объект, который содержит:
    - message: отформатированная строка сообщения
    - record: словарь с полной информацией о логе (message, level, time, file, function, line, exception, extra)
    """
    try:
        if not hasattr(message, "record"):
            if hasattr(message, "level"):
                record_dict = message
            else:
                return
        else:
            record_dict = message.record

        level_obj = record_dict.get("level")
        if not level_obj:
            return
        
        level_name = level_obj.name if hasattr(level_obj, "name") else str(level_obj)
        level_num = getattr(logging, level_name.upper(), logging.INFO)

        if hasattr(message, "record"):
            formatted_message = str(message)

            if not formatted_message or len(formatted_message.strip()) < 10:
                raw_message = record_dict.get("message", "")
                if raw_message:

                    try:
                        formatted_message = str(raw_message)
                    except Exception:
                        formatted_message = repr(raw_message)
        else:
            formatted_message = str(record_dict.get("message", ""))

        if not formatted_message:
            return

        file_info = record_dict.get("file", {})
        if isinstance(file_info, dict):
            file_path = file_info.get("path", "")
        elif hasattr(file_info, "path"):
            file_path = file_info.path
        else:
            file_path = ""

        func_name = record_dict.get("function", "")
        line_no = record_dict.get("line", 0)

        exc_info = None
        exception = record_dict.get("exception")
        if exception:
            exc_info = (type(exception), exception, getattr(exception, "__traceback__", None))

        # Создаем LogRecord для стандартного logging
        log_record = logging.LogRecord(
            name="loguru",
            level=level_num,
            pathname=file_path,
            lineno=line_no,
            msg=formatted_message,
            args=(),
            exc_info=exc_info,
            func=func_name,
        )

        logging.getLogger().handle(log_record)
    except Exception:
        pass


def setup_logging() -> None:
    """Единая точка входа: настраивает OpenSearch + loguru + стандартный logging."""
    handler = create_opensearch_handler()
    attach_handler_to_loggers(handler)


    logging.getLogger("opensearch").setLevel(logging.WARNING)
    logging.getLogger("opensearchpy").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)

    loguru_logger.add(forward_log_record_to_standard_logging, level="DEBUG")
    loguru_logger.info("Логирование настроено")

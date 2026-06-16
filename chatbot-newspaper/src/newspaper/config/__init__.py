from src.newspaper.config.database import MongoDBConnection
from src.newspaper.config.settings import Settings, settings

# setup_logging будет добавлен когда создадим logging.py
# from src.newspaper.config.logging import setup_logging

__all__ = [
    "settings",
    "Settings",
    "MongoDBConnection",
]

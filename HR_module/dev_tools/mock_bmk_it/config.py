import os
from pathlib import Path

FILES_DIR = Path(__file__).resolve().parent / "files"
MOCK_PUBLIC_URL = os.getenv("MOCK_PUBLIC_URL", "http://127.0.0.1:8088").rstrip("/")
MIDDLEWARE_HOST = os.getenv("MIDDLEWARE_HOST", "http://127.0.0.1:8091").rstrip("/")

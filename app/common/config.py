import os

from .logger import get_logger

logger = get_logger(__name__)

PROJECT_NAME = "Uniquest"
ALLOWED_HOSTS = "*"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", 8000)
DEBUG = bool(os.getenv("ENV", "local") == True)


if os.getenv("DB_STRING", None):
    MONGODB_URL = os.getenv("DB_STRING")
else:
    DB_HOST, DB_PASSWORD, DB_USER, DB_PORT = (
        os.getenv("DB_HOST", "localhost"),
        os.getenv("DB_PASSWORD", "pass"),
        os.getenv("DB_USER", "user"),
        os.getenv("DB_PORT", 27107),
    )
    MONGODB_URL = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?authMechanism=DEFAULT&authSource=admin"

MONGODB = os.getenv("DB_NAME") if os.getenv("DB_NAME") else "Uniquest"

DATA_FOLDER = "./data"
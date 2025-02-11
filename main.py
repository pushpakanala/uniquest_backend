from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.common.logger import get_logger
from app.common.config import PROJECT_NAME, ALLOWED_HOSTS, DEBUG
from app.common.db import db
from app.users.routers.index import router as user_router
from app.universities.routers.index import router as university_router
from app.common.services.exception_handler import EXCEPTION_HANDLERS

logger = get_logger(__name__)

app = FastAPI(
    title=PROJECT_NAME, exception_handlers=EXCEPTION_HANDLERS, debug=DEBUG
)


if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_event_handler("startup", db.connect_to_mongo)
app.add_event_handler("shutdown", db.close_mongo_connection)
app.include_router(user_router)
app.include_router(university_router)



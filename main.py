from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware
from app.common.logger import get_logger
from app.common.config import PROJECT_NAME, ALLOWED_HOSTS, DEBUG
from app.common.db import db
from app.users.routers.index import router as user_router
from app.universities.routers.index import router as university_router
from app.llm.routers.index import router as llm_router
from app.common.services.exception_handler import EXCEPTION_HANDLERS
from app.common.auth import create_access_token, verify_token  # Import auth functions
import os

logger = get_logger(__name__)

app = FastAPI(
    title=PROJECT_NAME, exception_handlers=EXCEPTION_HANDLERS, debug=DEBUG
)

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token Generation Route (Login)
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Dummy authentication - Replace with real authentication (DB lookup)
    if form_data.username != os.getenv("TOKEN_USERNAME") or form_data.password != os.getenv("TOKEN_PWD"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_data = {"sub": form_data.username}  # Payload for JWT
    access_token = create_access_token(user_data)
    return {"access_token": access_token, "token_type": "bearer"}

# Database connection handlers
app.add_event_handler("startup", db.connect_to_mongo)
app.add_event_handler("shutdown", db.close_mongo_connection)

# Include Routers with Authentication
app.include_router(user_router)
app.include_router(university_router, dependencies=[Depends(verify_token)])
app.include_router(llm_router, dependencies=[Depends(verify_token)])

from fastapi import APIRouter
from app.users.routers.user import router as user_router

router = APIRouter(
    prefix="/user-management",
)
router.include_router(user_router)

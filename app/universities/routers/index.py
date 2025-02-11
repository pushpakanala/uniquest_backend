from fastapi import APIRouter
from app.universities.routers.university import router as university_router

router = APIRouter(
    prefix="/user-management",
)
router.include_router(university_router)

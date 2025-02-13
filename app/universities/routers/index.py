from fastapi import APIRouter
from app.universities.routers.university import router as university_router

router = APIRouter(
    prefix="/university-management",
)
router.include_router(university_router)

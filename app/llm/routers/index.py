from fastapi import APIRouter
from app.llm.routers.llm import router as llm_router

router = APIRouter(
    prefix="/llm",
)
router.include_router(llm_router)

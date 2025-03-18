from fastapi import APIRouter
from app.metrics.routers.metrics import router as metrics_router

router = APIRouter(
    prefix="/metrics-logging",
)
router.include_router(metrics_router)

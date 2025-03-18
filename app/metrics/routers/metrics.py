import traceback
from fastapi import APIRouter, Depends, HTTPException, Query,status
from typing import Annotated, Union
from app.common.logger import get_logger
from app.common.helpers import format_response
from app.metrics.services.metrics import Metrics
from app.metrics.models.metrics import MetricSchema
from app.common.constants import Resources
from app.common.auth import verify_token,create_access_token
logger = get_logger(__name__)
router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={404: {"description": "Not Found"}},
    redirect_slashes=True,
)

    
@router.get(path="/")
async def get_all_metrics(
    s: Annotated[Metrics, Depends(Metrics)],
):
    try:
        res = await s.get_log_event()
        return format_response(200, res)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.post(path="/track-event")
async def post_metrics(
    request: MetricSchema,
    s:Annotated[Metrics,Depends(Metrics)],
):
    try:
        req_body = request.dict()
        res=await s.log_event(req_body)
        if res.acknowledged:
            return format_response(
                status.HTTP_201_CREATED, message=Resources.CREATED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Unable to insert the request"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
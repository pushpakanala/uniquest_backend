import traceback
from fastapi import APIRouter, Depends, HTTPException, Query,status
from typing import Annotated, Union
from app.common.logger import get_logger
from app.common.helpers import format_response
from app.llm.services.llm import LLM
from app.llm.models.llm import LLMSchema
from app.common.constants import Resources
logger = get_logger(__name__)
router = APIRouter(
    prefix="/llm",
    tags=["llm"],
    responses={404: {"description": "Not Found"}},
    redirect_slashes=True,
)

    
@router.get(path="/")
async def chat_with_ai(
    request: str,
    s: Annotated[LLM, Depends(LLM)],
):
    try:
        res = await s.chat_with_ai(request)
        return format_response(200, res)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.get(path="/top-universities")
async def get_top_universities(
    state_name:str,
    s:Annotated[LLM,Depends(LLM)],
):
    try:
        res=await s.get_top_universities(state_name)
        if res:
            return format_response(
                status.HTTP_200_OK,data=res, message=Resources.FETCHED
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
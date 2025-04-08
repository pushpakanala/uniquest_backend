import traceback
from fastapi import APIRouter, Depends, HTTPException, Query,status
from typing import Annotated, Union
from app.common.logger import get_logger
from app.common.helpers import format_response
from app.llm.services.llm import LLM
from app.llm.models.llm import LLMSchema, RequestBOT
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

@router.get(path="/top-universities-gpt")
async def   get_gpt_top_universities(
    state_name:str,
    s:Annotated[LLM,Depends(LLM)],
):
    try:
        res=await s.get_gpt_top_universities(state_name)
        if res:
            return format_response(
                status.HTTP_200_OK,data=res, message=Resources.FETCHED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Unable to handle the request"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.get(path="/gpt-universities-data")
async def get_gpt_universities_data(
    university_name:str,
    s:Annotated[LLM,Depends(LLM)],
):
    try:
        res=await s.get_gpt_universities_data(university_name)
        if res:
            return format_response(
                status.HTTP_200_OK,data=res, message=Resources.FETCHED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Unable to handle the request"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.get(path="/compare-universities-llm")
async def get_compare_universities(
    university_names:str,
    s:Annotated[LLM,Depends(LLM)],
):
    try:
        res=await s.get_compare_universities(university_names)
        if res:
            return format_response(
                status.HTTP_200_OK,data=res, message=Resources.FETCHED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Unable to handle the request"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
@router.post(path="/")
async def post_chatbot(
    request: RequestBOT,
    s:Annotated[LLM,Depends(LLM)],
):
    try:
        req_body = request.dict()
        res=await s.post_chatbot(req_body)
        if len(res):
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
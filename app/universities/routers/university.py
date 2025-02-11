import traceback
from fastapi import APIRouter, Depends, HTTPException, Query,status
from typing import Annotated, Union
from app.common.logger import get_logger
from app.common.helpers import format_response
from app.universities.services.university import University
from app.universities.models.university import StateUniversitySchema
from app.common.constants import Resources
logger = get_logger(__name__)
router = APIRouter(
    prefix="/state_university",
    tags=["state_university"],
    responses={404: {"description": "Not Found"}},
    redirect_slashes=True,
)

@router.get(path="/{id}")
async def get_user_by_email(
    state_name:str,
    s: Annotated[University, Depends(University)],
):
    try:
        res = await s.get_universities_by_state(state_name)
        if len(res):
            return format_response(status.HTTP_200_OK, data=res)
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "State Not Found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

    
@router.get(path="/")
async def get_all_users(
    s: Annotated[University, Depends(University)],
):
    try:
        res = await s.get_all_universities()
        return format_response(200, res)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
@router.post(path="/")
async def post_user(
    request: StateUniversitySchema,
    s:Annotated[University,Depends(University)],
):
    try:
        req_body = request.dict()
        res=await s.post_state_university(req_body)
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
    
# @router.put(path="/")
# async def update_user(
#     request:PutUserSchema,
#     s:Annotated[User,Depends(User)],
# ):
#     try:
#         req_body = request.dict()
#         res=await s.update_user(req_body)
#         if res.acknowledged and res.modified_count:
#             return format_response(
#                 status.HTTP_200_OK, message=Resources.UPDATED
#             )
#         else:
#             raise HTTPException(
#                 status.HTTP_400_BAD_REQUEST, Resources.UPDATE_FAILED
#             )
#     except Exception as e:
#         if isinstance(e, HTTPException):
#             raise e
#         logger.error("DATA ERROR : ")
#         logger.error(f"{e}")
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
# @router.delete(path="/")
# async def delete_user(
#     id:int,
#     s:Annotated[User,Depends(User)],
# ):
#     try:
#         res=await s.delete_user(id)
#         if res.acknowledged and res.deleted_count:
#                 return format_response(
#                     status.HTTP_200_OK, message=Resources.DELETED
#                 )
#         else:
#             raise HTTPException(
#                 status.HTTP_400_BAD_REQUEST, Resources.DELETE_FAILED
#             )
#     except Exception as e:
#         if isinstance(e, HTTPException):
#             raise e
#         logger.error("DATA ERROR : ")
#         logger.error(f"{e}")
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         raise HTTPException(500, f"Unknown Error Occurred: {e}")
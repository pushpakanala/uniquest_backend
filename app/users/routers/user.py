import traceback
from fastapi import APIRouter, Depends, HTTPException, Query,status
from typing import Annotated, Union
from app.common.logger import get_logger
from app.common.helpers import format_response
from app.users.services.user import User
from app.users.models.user import RequestUserSchema, PutUserSchema, LoginUserSchema, UpdatePwdSchema
from app.common.constants import Resources
from app.common.auth import verify_token,create_access_token
logger = get_logger(__name__)
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"}},
    redirect_slashes=True,
)

@router.post("/login")
async def login(
    email: str,
    password: str,
    s: Annotated[User, Depends(User)],
):
    """User Login - Returns JWT token if credentials are valid"""
    try:
        res = await s.login(email, password)
        if res:
            # Generate a JWT token
            access_token = create_access_token({"sub": res["email"], "role": res["role"]})
            res['access_token']=access_token
            res['token_type']='bearer'
            return format_response(
                status.HTTP_200_OK,
                data=res,
                message=Resources.LOGIN_SUCCESS,
            )
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Login Failed")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.get(path="/{id}",dependencies=[Depends(verify_token)])
async def get_user_by_email(
    email:str,
    s: Annotated[User, Depends(User)],
):
    try:
        res = await s.get_user_by_email(email)
        if len(res):
            return format_response(status.HTTP_200_OK, data=res)
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ID Not Found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

    
@router.get(path="/",dependencies=[Depends(verify_token)])
async def get_all_users(
    s: Annotated[User, Depends(User)],
):
    try:
        res = await s.get_all_users()
        return format_response(200, res)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.post(path="/email-verify")
async def get_user_verify_by_email(
    email:str,
    s: Annotated[User, Depends(User)],
):
    try:
        res = await s.get_user_verify_by_email(email)
        if len(res):
            return format_response(status.HTTP_200_OK, data=res)
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ID Not Found")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
@router.post(path="/")
async def post_user(
    request: RequestUserSchema,
    s:Annotated[User,Depends(User)],
):
    try:
        req_body = request.dict()
        res=await s.post_user(req_body)
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
    
@router.put(path="/",dependencies=[Depends(verify_token)])
async def update_user(
    request:PutUserSchema,
    s:Annotated[User,Depends(User)],
):
    try:
        req_body = request.dict()
        res=await s.update_user(req_body)
        if res.acknowledged and res.modified_count:
            return format_response(
                status.HTTP_200_OK, message=Resources.UPDATED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, Resources.UPDATE_FAILED
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")

@router.put(path="/update-pwd")
async def update_user_pwd(
    request:UpdatePwdSchema,
    s:Annotated[User,Depends(User)],
):
    try:
        req_body = request.dict()
        res=await s.update_user_pwd(req_body)
        if res.acknowledged and res.modified_count:
            return format_response(
                status.HTTP_200_OK, message=Resources.UPDATED
            )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, Resources.UPDATE_FAILED
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
    
@router.delete(path="/",dependencies=[Depends(verify_token)])
async def delete_user(
    id:int,
    s:Annotated[User,Depends(User)],
):
    try:
        res=await s.delete_user(id)
        if res.acknowledged and res.deleted_count:
                return format_response(
                    status.HTTP_200_OK, message=Resources.DELETED
                )
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, Resources.DELETE_FAILED
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("DATA ERROR : ")
        logger.error(f"{e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(500, f"Unknown Error Occurred: {e}")
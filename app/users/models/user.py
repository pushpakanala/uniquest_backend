from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union

class UserSchema(BaseModel):
    name: str
    email:str
    password:str
    role:str
    favourites:list =[]

class RequestUserSchema(BaseModel):
    name:str
    email:str
    role:str
    favourites:list =[]

class PutUserSchema(BaseModel):
    name:str
    email:str
    role:Optional[str]=Field(None)
    favourites:list =[]

class LoginUserSchema(BaseModel):
    email:str
    password:str
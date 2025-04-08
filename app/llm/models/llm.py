from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union

class LLMSchema(BaseModel):
    session_id:str
    messages:list

class RequestBOT(BaseModel):
    session_id:str
    user_message:str
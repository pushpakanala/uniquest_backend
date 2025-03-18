from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union

class MetricSchema(BaseModel):
    user_id:str
    event:str
    details:dict
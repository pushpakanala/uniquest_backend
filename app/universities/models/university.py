from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union

class StateUniversitySchema(BaseModel):
    state_name: str
    university_name: str
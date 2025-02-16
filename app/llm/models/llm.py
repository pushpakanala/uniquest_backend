from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union

class LLMSchema(BaseModel):
    state_name: str
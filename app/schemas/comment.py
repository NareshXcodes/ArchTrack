from pydantic import BaseModel , ConfigDict
from typing import List , Literal,Optional
from datetime import datetime

class CommentCreate(BaseModel):
    body : str

class CommentResponse(BaseModel):
    id : int
    body : str
    author_id : int
    decision_id : int
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)
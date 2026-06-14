from pydantic import BaseModel , ConfigDict
from typing import List , Literal,Optional
from datetime import datetime

class VoteCreate(BaseModel):
    option_id : int


class VoteResponse(BaseModel):
    user_id : int
    option_id : int
    decision_id: int
    model_config = ConfigDict(from_attributes=True)

class VoteResult(BaseModel):
    option_id : int
    vote_count : int
    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel , ConfigDict
from typing import Optional
from datetime import datetime

class OptionBase(BaseModel):
    title: str
    description: Optional[str] = None
    pros : Optional[str] = None
    cons : Optional[str] = None

class OptionCreate(OptionBase):
    pass

class OptionResponse(OptionBase):
    id : int
    decision_id : int
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

class OptionWithVotes(OptionResponse):
    vote_count:int
    

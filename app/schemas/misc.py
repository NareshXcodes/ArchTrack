from pydantic import BaseModel , ConfigDict
from typing import List , Literal,Dict

class StatusUpdate(BaseModel):
    status : Literal["proposed","under_review","accepted","deprecated","superseded"]

class ProjectSummary(BaseModel):
    total_decisions : int
    decisions_per_status : Dict[str,int]
    top_tags : List[str]
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message:str
    model_config = ConfigDict(from_attributes=True)
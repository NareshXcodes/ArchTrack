from pydantic import BaseModel , ConfigDict
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name : str
    description : str
    team_id : Optional[int]

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name : Optional[str]
    description : Optional[str]

class ProjectResponse(ProjectBase):
    id : int
    owner_id : int
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)
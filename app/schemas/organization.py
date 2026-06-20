from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Annotated, Field
from app.schemas.team import TeamResponse

class OrgCreate(BaseModel):
    name : str
    slug : str

class OrgUpdate(BaseModel):
    name: str
    slug: str

class OrgResponse(OrgCreate):
    id : int
    created_by : int | None
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

class OrgDetailResponse(OrgResponse):
    teams : List[TeamResponse]
    total_members : int


from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserResponse


class TeamCreate(BaseModel):
    name : str

class TeamResponse(TeamCreate):
    id : int
    org_id : int
    admin_id : int | None
    member_count : int
    transferred_at : datetime | None
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

class TeamDetailResponse(TeamResponse):
    members:List[UserResponse]

class TransferAdminRequest(BaseModel):
    new_admin_id : int
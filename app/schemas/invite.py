from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

InviteRole = Literal[
    "architect",
    "reviewer",
    "developer"
]

class InviteCreate(BaseModel):
    email : EmailStr
    role : InviteRole

class InviteResponse(InviteCreate):
    id : int
    org_id : int
    team_id : int
    invited_by : int
    token : str
    expires_at : datetime
    is_used : bool

class InviteRegister(BaseModel):
    token : Annotated[str, Field(max_length=64,min_length=64,pattern=r"^[0-9a-f]{64}$")]
    password : Annotated[str, Field(min_length=8)]

class InvitePreview(BaseModel):
    org_name : str
    team_name : str
    role : InviteRole
    invited_by_email : str
    expires_at :  datetime
    model_config = ConfigDict(from_attributes=True)


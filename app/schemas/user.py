from pydantic import BaseModel , ConfigDict
from datetime import datetime
from pydantic import EmailStr
from typing import Optional , Literal

Role = Literal[
    "org_admin"
    "team_admin",
    "architect",
    "reviewer",
    "developer"
]


class UserCreate(BaseModel):
    email : EmailStr
    password : str
    role : Optional[Role] = "developer"

class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    role : Role
    model_config = ConfigDict(from_attributes = True)
	
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes = True)

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
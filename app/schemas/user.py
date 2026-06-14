from pydantic import BaseModel , ConfigDict
from datetime import datetime
from pydantic import EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    model_config = ConfigDict(from_attributes = True)
	
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes = True)

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field

class BootstrapRequest(BaseModel):
    email : EmailStr
    password : Annotated[str, Field(min_length=8)]
    org_name : str
    org_slug : Annotated[str, Field(min_length=1,pattern=r"^[a-z0-9-]+$")]
    default_team_name : str = "General"

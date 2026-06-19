from typing import Literal
from pydantic import BaseModel

UpdatableRole = Literal[
    "team_admin",
    "architect",
    "reviewer",
    "developer"
]

class UpdateRole(BaseModel):
    role : UpdatableRole
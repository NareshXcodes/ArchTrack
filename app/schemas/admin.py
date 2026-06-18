from typing import Literal
from pydantic import BaseModel

UpdatableRole = Literal[
    "architect",
    "reviewer",
    "developer"
]

class UpdateRole(BaseModel):
    role : UpdatableRole
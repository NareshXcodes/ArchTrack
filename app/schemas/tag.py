from pydantic import BaseModel , ConfigDict


class TagResponse(BaseModel):
    id : int
    name : str
    model_config = ConfigDict(from_attributes=True)

class TagUsageResponse(BaseModel):
    id: int
    name: str
    usage_count: int
    model_config = ConfigDict(from_attributes=True)
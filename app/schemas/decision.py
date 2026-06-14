from pydantic import BaseModel , ConfigDict
from typing import List ,Optional
from datetime import datetime
from .option import OptionWithVotes
from .tag import TagResponse
from .comment import CommentResponse

class DecisionBase(BaseModel):
    title : str
    context : str
    decision_made : str
    consequences: str | None = None

class DecisionCreate(DecisionBase):
    tags : List[str] = []

class DecisionUpdate(BaseModel):
    title: Optional[str]
    context : Optional[str]
    decision_made : Optional[str]
    consequences: Optional[str]
    tags : Optional[List[str]]


class OptionVoteCount(BaseModel):
    option_id: int
    vote_count: int


class DecisionResponse(DecisionBase):
    id : int
    status : str
    author_id : int
    project_id : int
    tags : List[TagResponse]
    created_at : datetime
    updated_at : datetime
    model_config = ConfigDict(from_attributes=True)


class DecisionDetailResponse(DecisionResponse):
    options : List[OptionWithVotes]
    comments : List[CommentResponse]
    user_voted_option_id : Optional[int]
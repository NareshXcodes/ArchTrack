from pydantic import BaseModel , ConfigDict
from typing import Literal
from datetime import datetime
from app.models.reviewcomments import VerdictEnum


class AssignReviewer(BaseModel):
    reviewer_id : int
    assigned_by : int

class AssignReviewerResponse(AssignReviewer):
    decision_id : int
    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    verdict: VerdictEnum
    body: str

class ReviewResponse(ReviewCreate):
    id : int
    decision_id : int
    reviewer_id : int
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

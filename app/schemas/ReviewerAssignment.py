from pydantic import BaseModel , ConfigDict

class AssignReviewer(BaseModel):
    reviewer_id : int
    assigned_by : int

class AssignReviewerResponse(AssignReviewer):
    decision_id : int
    model_config = ConfigDict(from_attributes=True)
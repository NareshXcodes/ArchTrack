from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import SessionDB
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import DecisionReviewer , Decision
from app.models.reviewcomments import ReviewComment
from app.utils.permissions import ARCHITECTS
from app.schemas.ReviewerAssignment import AssignReviewer,AssignReviewerResponse

router = APIRouter(tags=['Reviewer Assignment'])

@router.post("/decisions/{id}/assign-reviewer",response_model=AssignReviewerResponse)
def assign_review_to_decision(id:int, db:SessionDB,new_assign_reviewer:AssignReviewer,current_user:User = Depends(ARCHITECTS)):
    fetch_decision = db.query(Decision).filter(Decision.id == id).first()
    fetch_reviewer = db.query(User).filter(User.id == new_assign_reviewer.reviewer_id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    if not fetch_reviewer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )

    if fetch_reviewer.role != "reviewer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a reviewer"
        )

    existing_assignment = db.query(DecisionReviewer).filter(DecisionReviewer.decision_id == id,DecisionReviewer.reviewer_id == new_assign_reviewer.reviewer_id).first()

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reviewer already assigned"
        )
    assignment=DecisionReviewer(decision_id = id,reviewer_id=new_assign_reviewer.reviewer_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment
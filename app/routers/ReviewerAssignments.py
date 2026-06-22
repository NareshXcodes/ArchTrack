from fastapi import APIRouter, Depends, HTTPException, status,Response
from app.models.users import User
from app.models.decisions import DecisionReviewer , Decision, StatusEnum
from app.models.reviewcomments import ReviewComment
from app.utils.org_query import OrgScopedQuery
from app.utils.org_query import get_scoped_query
from app.schemas.ReviewerAssignment import AssignReviewer,AssignReviewerResponse, ReviewCreate, ReviewResponse
from typing import List

router = APIRouter(tags=['Reviewer Assignment'])

@router.post("/decisions/{id}/assign-reviewer",response_model=AssignReviewerResponse)
def assign_review_to_decision(id:int,new_assign_reviewer:AssignReviewer,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )
    # Only decision author can assign reviewers
    if fetch_decision.author_id != sq.user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the decision author can assign reviewers"
        )

    # Reviewer assignment only during proposed stage
    if fetch_decision.status != StatusEnum.proposed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewers can only be assigned while decision is proposed"
        )

    fetch_reviewer = sq.users().filter(User.id == new_assign_reviewer.reviewer_id).first()

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

    # prevent author reviewing own decision
    if fetch_reviewer.id == fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision author cannot be assigned as reviewer"
        )

    existing_assignment = sq.db.query(DecisionReviewer).filter(DecisionReviewer.decision_id == id,DecisionReviewer.reviewer_id == new_assign_reviewer.reviewer_id).first()

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reviewer already assigned"
        )
    assignment=DecisionReviewer(decision_id = id,reviewer_id=new_assign_reviewer.reviewer_id,assigned_by=sq.user.id)
    sq.db.add(assignment)
    sq.db.commit()
    sq.db.refresh(assignment)
    return assignment


@router.delete("/decisions/{id}/assign-reviewer/{reviewer_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_reviewer(id:int,reviewer_id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == id).first()
    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    # Only decision author can remove reviewers
    if fetch_decision.author_id != sq.user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the decision author can remove reviewers"
        )

    # Reviewer removal only during proposed and under_review stage
    if fetch_decision.status not in (
        StatusEnum.proposed,
        StatusEnum.under_review
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer assignments are locked"
        )

    fetch_assignment = sq.db.query(DecisionReviewer).filter(DecisionReviewer.reviewer_id == reviewer_id,DecisionReviewer.decision_id == id).first()
    if not fetch_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewer assignment not found"
        )

    if fetch_assignment.assigned_by != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    review = sq.db.query(ReviewComment).filter(ReviewComment.decision_id == fetch_decision.id,ReviewComment.reviewer_id == reviewer_id).first()

    if review and review.verdict.value :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer has already submitted a verdict"
        )

    sq.db.delete(fetch_assignment)
    sq.db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@router.post("/decisions/{id}/review",response_model=ReviewResponse,status_code=status.HTTP_201_CREATED)
def submit_verdict(id:int,new_review:ReviewCreate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == id).first()
    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    if fetch_decision.status.value != "under_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision is not under review"
        )
    
    assignment = sq.db.query(DecisionReviewer).filter(DecisionReviewer.decision_id == id , DecisionReviewer.reviewer_id == sq.user.id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer is not assigned to this decision"
        )

    existing_review = sq.db.query(ReviewComment).filter(ReviewComment.decision_id == id , ReviewComment.reviewer_id == sq.user.id).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already submitted"
        )

    review = ReviewComment(
        body = new_review.body,
        verdict = new_review.verdict,
        decision_id = id,
        reviewer_id = sq.user.id
    )

    sq.db.add(review)
    sq.db.commit()
    sq.db.refresh(review)
    return review

@router.get("/decisions/{id}/reviews",response_model=List[ReviewResponse])
def fetch_all_reviews_verdicts(id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == id).first()
    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    fetch_review = sq.db.query(ReviewComment).filter(ReviewComment.decision_id == id).all()

    return fetch_review
from app.db.database import SessionDB
from app.schemas.vote import VoteCreate , VoteResult
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision, StatusEnum
from app.models.votes import Vote
from app.models.options import Option
from sqlalchemy import func
from app.utils.org_query import OrgScopedQuery, get_scoped_query

router = APIRouter(tags=['Votes'])

@router.post("/decisions/{decision_id}/vote",response_model=VoteResult)
def modify_vote(decision_id:int,new_vote:VoteCreate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == decision_id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )

    if fetch_decision.status != StatusEnum.proposed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is only allowed while decision is proposed"
        )

    fetch_options = sq.db.query(Option).join(Decision).filter(Option.id == new_vote.option_id,Decision.id == decision_id).first()

    if not fetch_options:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option Not Found"
        )

    existing_vote = sq.db.query(Vote).filter(Vote.user_id == sq.user.id,Vote.decision_id == decision_id).first()

    if existing_vote:
        existing_vote.option_id = new_vote.option_id
        sq.db.commit()
        sq.db.refresh(existing_vote)
    else:
        vote = Vote(**new_vote.model_dump() , decision_id = decision_id,user_id=sq.user.id)
        sq.db.add(vote)
        sq.db.commit()
        sq.db.refresh(vote)

    vote_count =  sq.db.query(func.count(Vote.id)).filter(Vote.option_id == new_vote.option_id).scalar()

    return VoteResult(
        option_id = new_vote.option_id,
        vote_count = vote_count
    )


@router.delete("/decisions/{decision_id}/vote",status_code=status.HTTP_204_NO_CONTENT)
def remove_vote(decision_id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == decision_id).first()
    
    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )
    
    if fetch_decision.status != StatusEnum.proposed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voting is closed for this decision"
        )

    fetch_vote = sq.db.query(Vote).filter(Vote.user_id == sq.user.id , Vote.decision_id == decision_id).first()

    if not fetch_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )

    sq.db.delete(fetch_vote)
    sq.db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
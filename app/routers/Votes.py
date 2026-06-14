from app.db.database import SessionDB
from app.schemas.vote import VoteCreate , VoteResult
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision
from app.models.votes import Vote
from app.models.options import Option
from sqlalchemy import func

router = APIRouter(tags=['Votes'])

@router.post("/decisions/{decision_id}/vote",response_model=VoteResult)
def modify_vote(decision_id:int,new_vote:VoteCreate,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )

    fetch_options = db.query(Option).filter(Option.id == new_vote.option_id).first()

    if not fetch_options:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option Not Found"
        )

    #check decision hold the option or not
    if fetch_decision.id != fetch_options.decision_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Option not belong to required decision"
        )

    existing_vote = db.query(Vote).filter(Vote.user_id == current_user.id,Vote.decision_id == decision_id).first()

    if existing_vote:
        existing_vote.option_id = new_vote.option_id
        db.commit()
        db.refresh(existing_vote)
    else:
        vote = Vote(**new_vote.model_dump() , decision_id = decision_id,user_id=current_user.id)
        db.add(vote)
        db.commit()
        db.refresh(vote)

    vote_count =  db.query(func.count(Vote.id)).filter(Vote.option_id == new_vote.option_id).scalar()

    return VoteResult(
        option_id = new_vote.option_id,
        vote_count = vote_count
    )


@router.delete("/decisions/{decision_id}/vote",status_code=status.HTTP_204_NO_CONTENT)
def remove_vote(decision_id:int,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_vote = db.query(Vote).filter(Vote.user_id == current_user.id , Vote.decision_id == decision_id).first()

    if not fetch_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )

    db.delete(fetch_vote)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
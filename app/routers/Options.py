from app.db.database import SessionDB
from app.schemas.option import OptionResponse ,OptionCreate
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision
from app.models.options import Option


router = APIRouter(tags=['Options'])

@router.post("/decisions/{decisions_id}/options",response_model=OptionResponse,status_code=status.HTTP_201_CREATED)
def adding_option(decision_id:int,new_option:OptionCreate,db:SessionDB,current_user: User = Depends(get_current_user)):
    query = db.query(Decision).filter(Decision.id == decision_id)
    fetch_decision = query.first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )
    
    if current_user.id != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized, Only owner can add options"
        )

    if fetch_decision.status.value == "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accepted decisions are locked"
        )

    options = Option(**new_option.model_dump(),decision_id = decision_id)
    db.add(options)
    db.commit()
    db.refresh(options)
    return options


@router.delete("/options/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_option(id:int,db: SessionDB,current_user: User = Depends(get_current_user)):
    fetch_option = db.query(Option).filter(Option.id == id).first()

    if not fetch_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option Not Found"
        )

    fetch_decision = fetch_option.decision

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )

    if current_user.id != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    db.delete(fetch_option)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
    

from app.db.database import SessionDB
from app.models.projects import Project
from app.schemas.option import OptionResponse ,OptionCreate
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision, StatusEnum
from app.models.options import Option
from app.utils.org_query import OrgScopedQuery, get_scoped_query


router = APIRouter(tags=['Options'])

@router.post("/decisions/{decision_id}/options",response_model=OptionResponse,status_code=status.HTTP_201_CREATED)
def adding_option(decision_id:int,new_option:OptionCreate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    query = sq.decisions().filter(Decision.id == decision_id)
    fetch_decision = query.first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )

    if sq.user.id != fetch_decision.author_id:
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
    sq.db.add(options)
    sq.db.commit()
    sq.db.refresh(options)
    return options


@router.delete("/options/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_option(id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    query = sq.db.query(Option).join(Decision).join(Project).filter(Option.id == id,Project.org_id == sq.org_id)

    if sq.is_org_admin:
        query = query.filter(Project.team_id == sq.team_id)

    fetch_option = query.first()
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

    if sq.user.id != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    if fetch_decision.status != StatusEnum.proposed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Options can only be modified while decision is proposed"
        )

    sq.db.delete(fetch_option)
    sq.db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
    

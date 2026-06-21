from app.db.database import SessionDB
from app.models.projects import Project
from app.schemas.comment import CommentResponse,CommentCreate
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision, StatusEnum
from app.models.comments import Comment
from app.utils.org_query import OrgScopedQuery, get_scoped_query

router = APIRouter(tags=['Comments'])

@router.post("/decisions/{decision_id}/comments",response_model=CommentResponse,status_code=status.HTTP_201_CREATED)
def create_comment(decision_id:int,new_comment: CommentCreate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_decision = sq.decisions().filter(Decision.id == decision_id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    if fetch_decision.status in ( StatusEnum.accepted , StatusEnum.deprecated, StatusEnum.superseded):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment are closed for this decision"
        )

    comment = Comment(**new_comment.model_dump(),decision_id = decision_id,author_id = sq.user.id)
    sq.db.add(comment)
    sq.db.commit()
    sq.db.refresh(comment)
    return comment

@router.delete("/comments/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    query = sq.db.query(Comment).join(Decision).join(Project).filter(Comment.id == id,Project.org_id == sq.org_id)

    if not sq.is_org_admin:
        query = query.filter(Project.team_id == sq.team_id)

    fetch_comment = query.first()

    if not fetch_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not Found"
        )

    if fetch_comment.author_id != sq.user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to delete this comment"
        )

    sq.db.delete(fetch_comment)
    sq.db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

    

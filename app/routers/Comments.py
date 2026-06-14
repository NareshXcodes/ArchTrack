from app.db.database import SessionDB
from app.schemas.comment import CommentResponse,CommentCreate
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision
from app.models.comments import Comment

router = APIRouter(tags=['Comments'])

@router.post("/decisions/{decision_id}/comments",response_model=CommentResponse,status_code=status.HTTP_201_CREATED)
def create_comment(decision_id:int,db:SessionDB,new_comment: CommentCreate,current_user: User = Depends(get_current_user)):
    fetch_decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    comment = Comment(**new_comment.model_dump(),decision_id = decision_id,author_id = current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/comments/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id:int,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_comment = db.query(Comment).filter(Comment.id == id).first()

    if not fetch_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not Found"
        )

    if fetch_comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to delete the comment"
        )

    db.delete(fetch_comment)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

    

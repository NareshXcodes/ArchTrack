from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status,Response
from app.db.database import SessionDB
from app.models.decisions import Decision, StatusEnum
from app.models.projects import Project
from app.models.users import User
from app.schemas.admin import UpdateRole
from app.schemas.misc import StatusUpdate
from app.schemas.project import ProjectResponse
from app.schemas.user import UserResponse
from app.utils.permissions import ADMIN_ONLY
from typing import List
from app.utils.oauth2 import get_current_user
from app.schemas.decision import DecisionResponse
from app.models.decisionaudits import DecisionAudit

router = APIRouter(prefix="/admin",tags=['Admin'],dependencies=[Depends(ADMIN_ONLY)])

@router.get("/users",response_model=List[UserResponse])
def fetch_users_with_roles(db:SessionDB):
    fetch_users = db.query(User).all()

    return fetch_users

@router.patch("/users/{id}/role",response_model=UserResponse)
def change_users_role(id:int,new_role:UpdateRole,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_user = db.query(User).filter(User.id == id).first()

    if not fetch_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )

    if fetch_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot change their own role"
        )

    fetch_user.role = new_role.role
    db.commit()
    db.refresh(fetch_user)
    return fetch_user

@router.delete("/users/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_user(id:int,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_user = db.query(User).filter(User.id == id).first()

    if not fetch_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    if fetch_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete their own account"
        )

    db.delete(fetch_user)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@router.get("/projects",response_model=List[ProjectResponse])
def fetch_all_projects(db:SessionDB):
    fetch_projects = db.query(Project).all()

    return fetch_projects

@router.patch("/decisions/{id}/override",response_model=DecisionResponse)
def override_decision_status(id:int,new_status:StatusUpdate,db:SessionDB,current_user: User = Depends(get_current_user)):
    fetch_decision = db.query(Decision).filter(Decision.id == id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = fetch_decision.status.value

    fetch_decision.status = StatusEnum(new_status.status)
    fetch_decision.updated_at = datetime.now(timezone.utc)

    audit = DecisionAudit(
        decision_id = id,
        old_status = old_status,
        new_status = fetch_decision.status.value,
        changed_by = current_user.id
    )
    db.add(audit)
    db.commit()
    db.refresh(fetch_decision)

    return fetch_decision

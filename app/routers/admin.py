from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status,Response
from app.models.decisions import Decision, StatusEnum
from app.models.projects import Project
from app.models.teams import Team
from app.models.users import User
from app.schemas.admin import UpdateRole
from app.schemas.misc import StatusUpdate
from app.schemas.project import ProjectResponse
from app.schemas.user import UserResponse
from app.utils.org_query import OrgScopedQuery, get_scoped_query
from typing import List
from app.schemas.decision import DecisionResponse
from app.models.decisionaudits import DecisionAudit

router = APIRouter(prefix="/admin",tags=['Admin'])

@router.get("/users",response_model=List[UserResponse])
def fetch_users_with_roles(sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_users = sq.users().all()

    return fetch_users

@router.patch("/users/{id}/role",response_model=UserResponse)
def change_users_role(id:int,new_role:UpdateRole,sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_user = sq.users().filter(User.id == id).first()

    if not fetch_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not Found"
        )

    if fetch_user.id == sq.user.id and fetch_user.role == "org_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot change their own role"
        )

    if fetch_user.role == "org_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify another organization admin"
        )

    if new_role.role == "org_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign org_admin role"
        )


    if new_role.role == "team_admin" and fetch_user.team_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign team_admin role to a user without a team"
        )

    fetch_user.role = new_role.role
    sq.db.commit()
    sq.db.refresh(fetch_user)
    return fetch_user

@router.delete("/users/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_user(id:int,sq: OrgScopedQuery = Depends(get_scoped_query)):
    if not sq.is_org_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only organization admins can delete users"
        )

    fetch_user = sq.users().filter(User.id == id).first()

    if not fetch_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    if fetch_user.id == sq.user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cannot delete themselves"
        )

    if fetch_user.role == "org_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization admin cannot be deleted"
        )

    team = (
        sq.teams()
        .filter(Team.admin_id == fetch_user.id)
        .first()
    )

    if team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer team admin rights before deleting this user"
        )

    sq.db.delete(fetch_user)
    sq.db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@router.get("/projects",response_model=List[ProjectResponse])
def fetch_all_projects(sq: OrgScopedQuery = Depends(get_scoped_query)):

    if not sq.is_org_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can access all projects"
        )

    fetch_projects = sq.db.query(Project).filter(Project.org_id == sq.org_id).all()

    return fetch_projects

@router.patch("/decisions/{id}/override",response_model=DecisionResponse)
def override_decision_status(id:int,new_status:StatusUpdate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    if not sq.is_org_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization admins can override decision status"
        )

    fetch_decision = sq.decisions().filter(Decision.id == id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = fetch_decision.status.value

    if old_status == new_status.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision is already in this status"
        )

    fetch_decision.status = StatusEnum(new_status.status)
    fetch_decision.updated_at = datetime.now(timezone.utc)

    audit = DecisionAudit(
        decision_id = id,
        old_status = old_status,
        new_status = new_status.status,
        changed_by = sq.user.id
    )
    sq.db.add(audit)
    sq.db.commit()
    sq.db.refresh(fetch_decision)

    return fetch_decision

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException,status, Response
from app.db.database import SessionDB, get_db
from app.models.teams import Team
from app.models.users import User
from app.schemas.team import TeamCreate, TeamDetailResponse, TeamResponse, TransferAdminRequest
from app.utils.context import OrgContext, get_org_admin_context, get_org_context, get_team_admin_context
from app.utils.org_query import OrgScopedQuery, get_scoped_query
from typing import Literal, Optional


router = APIRouter(prefix="/teams", tags=['Team'])

@router.post("/",response_model=TeamResponse)
def create_team(new_team: TeamCreate,ctx:OrgContext = Depends(get_org_admin_context), db: Session = Depends(get_db)):

    existing_team = db.query(Team).filter(Team.org_id == ctx.org_id,Team.name == new_team.name).first()

    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team already exists"
        )

    team = Team(
        name = new_team.name,
        org_id = ctx.org_id,
        admin_id = None,
        transferred_at = None
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return TeamResponse(
        id=team.id,
        name=team.name,
        org_id=team.org_id,
        admin_id=team.admin_id,
        member_count=len(team.members),
        transferred_at=team.transferred_at,
        created_at=team.created_at,
    )

@router.get("/",response_model=list[TeamResponse])
def get_your_team(status:Optional[Literal["no_admin"]]=None,sq : OrgScopedQuery = Depends(get_scoped_query)):
    teams_query = sq.teams()

    if status == "no_admin":
        teams_query = teams_query.filter(Team.admin_id.is_(None))

    teams = teams_query.all()

    return [
        TeamResponse(
            id=team.id,
            name=team.name,
            org_id=team.org_id,
            admin_id=team.admin_id,
            member_count=len(team.members),
            transferred_at=team.transferred_at,
            created_at=team.created_at,
        )
        for team in teams
    ]

@router.get("/{id}",response_model=TeamDetailResponse)
def get_team_detail(id:int,ctx:OrgContext = Depends(get_org_context),db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == id).first()

    if not team:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if team.org_id != ctx.org_id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not ctx.is_org_admin and team.id != ctx.team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return TeamDetailResponse(
        id = team.id,
        name = team.name,
        org_id = team.org_id,
        admin_id = team.admin_id,
        member_count = len(team.members),
        members = team.members,
        transferred_at = team.transferred_at,
        created_at = team.created_at
    )

@router.patch("/{id}/admin",response_model=TeamResponse)
def modify_team_admin(id:int,payload: TransferAdminRequest,ctx:OrgContext = Depends(get_org_admin_context),db:Session = Depends(get_db)):
    fetch_team = db.query(Team).filter(Team.id == id,Team.org_id == ctx.org_id).first()

    if not fetch_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if fetch_team.admin_id == payload.new_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already the team admin"
        )
    
    new_admin = db.query(User).filter(User.id == payload.new_admin_id).first()

    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if fetch_team.id != new_admin.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this team"
        )

    if fetch_team.admin_id is not None:
        old_admin = db.query(User).filter(User.id == fetch_team.admin_id).first()

        if old_admin:
            old_admin.role = "architect"

    new_admin.role ="team_admin"
    fetch_team.admin_id = new_admin.id
    fetch_team.transferred_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(fetch_team)
    return TeamResponse(
        id=fetch_team.id,
        name=fetch_team.name,
        org_id=fetch_team.org_id,
        admin_id=fetch_team.admin_id,
        member_count=len(fetch_team.members),
        transferred_at=fetch_team.transferred_at,
        created_at=fetch_team.created_at
    )


@router.patch("/{id}/transfer-admin")
def tranfer_team_admin(id:int,payload: TransferAdminRequest,ctx:OrgContext = Depends(get_team_admin_context),db:Session = Depends(get_db)):

    team = db.query(Team).filter(Team.id == id,Team.org_id == ctx.org_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not (ctx.is_org_admin or (ctx.team_id == team.id and ctx.user.role == "team_admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    if team.admin_id == payload.new_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already team admin"
        )

    new_admin = db.query(User).filter(User.id == payload.new_admin_id).first()

    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if new_admin.team_id != team.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this team"
        )

    if new_admin.role in ["developer","reviewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User cannot be promoted to team admin"
        )
    if team.admin_id is not None:
        old_admin = db.query(User).filter(User.id == team.admin_id).first()

        if old_admin:
            old_admin.role = "architect"

    new_admin.role ="team_admin"
    team.admin_id = new_admin.id
    team.transferred_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(team)
    return TeamResponse(
        id=team.id,
        name=team.name,
        org_id=team.org_id,
        admin_id=team.admin_id,
        member_count=len(team.members),
        transferred_at=team.transferred_at,
        created_at=team.created_at
    )

@router.delete("/{id}/members/{user_id}")
def remove_team_members(id:int,user_id:int,ctx: OrgContext = Depends(get_team_admin_context),db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == id,Team.org_id == ctx.org_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not ctx.is_org_admin and ctx.team_id != team.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    user = db.query(User).filter(User.id==user_id,User.org_id == ctx.org_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.team_id != team.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this team"
        )

    if user.id == team.admin_id:

        member_count = len(team.members)

        if member_count == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are the only member. Delete the team instead."
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer admin rights before leaving. Use PATCH /teams/{id}/transfer-admin."
        )

    if user.role == "org_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization admins cannot be removed from a team."
        )

    if user.role in ["team_admin","architect","reviewer"]:
        user.role = "developer"

    user.team_id = None

    db.commit()

    return {
        "message": "Member removed successfully"
    }


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_team(id:int, ctx:OrgContext = Depends(get_org_admin_context),db:Session=Depends(get_db)):
    team = db.query(Team).filter(Team.id == id,Team.org_id == ctx.org_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    member_count = len(team.members)

    if member_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove all members before deleting team."
        )

    db.delete(team)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )









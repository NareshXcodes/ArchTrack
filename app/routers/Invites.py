from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Session, status
from app.db.database import get_db
from app.models.invites import Invite
from app.models.teams import Team
from app.models.users import User
from app.schemas.invite import InviteCreate, InviteResponse
from app.utils.context import OrgContext, get_team_admin_context
from app.utils.token_generator import generate_invite_token


router = APIRouter(tags=['Invites'])

@router.post("/teams/{team_id}/invites",response_model=InviteResponse,status_code=status.HTTP_201_CREATED)
def create_invite(team_id:int,invites:InviteCreate,ctx:OrgContext=Depends(get_team_admin_context),db:Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id,Team.org_id == ctx.org_id).first()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if (not ctx.is_org_admin and ctx.team_id != team.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    existing_invite = (
        db.query(Invite)
        .filter(
            Invite.email == invites.email,
            Invite.org_id == ctx.org_id,
            Invite.used_at.is_(None)
        )
        .first()
    )

    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Active invite already exists"
        )

    existing_user = db.query(User).filter(User.email == invites.email,User.org_id == ctx.org_id).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists in organization"
        )

    token = generate_invite_token()
    expires_at = datetime.now(timezone.utc)+timedelta(hours=48)

    invite = Invite(
        email=invites.email,
        role=invites.role,
        token=token,
        org_id = ctx.org_id,
        team_id=team.id,
        invited_by=ctx.user.id,
        expires_at=expires_at,
        used_at=None
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        org_id=invite.org_id,
        team_id=invite.team_id,
        invited_by=invite.invited_by,
        expires_at=invite.expires_at,
        is_used=invite.used_at is not None,
    )


@router.get("/teams/{team_id}/invites",response_model=list[InviteResponse])
def get_pending_invites(team_id:int,ctx:OrgContext=Depends(get_team_admin_context),db:Session=Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id,Team.org_id == ctx.org_id).first()

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

    invites = db.query(Invite).filter(Invite.team_id == team.id,Invite.used_at.is_(None),Invite.expires_at > datetime.now(timezone.utc)).all()

    return [  
        InviteResponse(
            id=invite.id,
            email=invite.email,
            role=invite.role,
            org_id=invite.org_id,
            team_id=invite.team_id,
            invited_by=invite.invited_by,
            expires_at=invite.expires_at,
            is_used=False,
        )
        for invite in invites
    ]

@router.delete("/invites/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_pending_invite(id:int,ctx:OrgContext=Depends(get_team_admin_context),db:Session=Depends(get_db)):
    invite = db.query(Invite).filter(Invite.id == id,Invite.org_id == ctx.org_id).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    if (not ctx.is_org_admin and invite.team_id != ctx.team_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )

    if invite.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite has already been used"
        )
    db.delete(invite)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
    
from datetime import datetime, timezone
from app.models.invites import Invite
from app.models.organizations import Organization
from app.models.teams import Team
from app.models.users import User
from app.db.database import SessionDB
from fastapi import Depends , APIRouter , HTTPException, status
from app.schemas.BootstrapRequest import BootstrapRequest
from app.schemas.invite import InvitePreview, InviteRegister
from app.utils.oauth2 import get_current_user
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.utils.jwt import create_access_token
from app.utils.hashing import hashed_password , verifying_password
from app.schemas.user import  UserResponse , TokenResponse
import traceback

router = APIRouter(tags=['Authentication'])

@router.post("/login",response_model=TokenResponse)
def login(db:SessionDB, user_credential : OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == user_credential.username).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Crediantial"
        )

    if not verifying_password(user_credential.password,user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Crediantial"
        )

    access_token = create_access_token(data={"user_id" : user.id})
    return {"access_token" : access_token , "token_type" : "bearer"}

@router.post("/auth/bootstrap",response_model=TokenResponse ,status_code = status.HTTP_201_CREATED)
def bootstrap(payload: BootstrapRequest,db:SessionDB):
    existing_user = db.query(User).first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail="System already bootstrapped."
        )

    try:
        user = User(
            email=payload.email,
            password = hashed_password(payload.password),
            role="org_admin"
        )
        db.add(user)
        db.flush()

        org = Organization(
            name=payload.org_name,
            slug=payload.org_slug,
            created_by=user.id
        )

        db.add(org)
        db.flush()

        team = Team(
            name=payload.default_team_name,
            org_id=org.id,
            admin_id=user.id
        )
        db.add(team)
        db.flush()

        user.org_id = org.id
        user.team_id = team.id

        db.commit()

        access_token = create_access_token(
            {"user_id":user.id}
        )

        return {
            "access_token" : access_token,
            "token_type" : "bearer"
        }
    except Exception:
        traceback.print_exc()
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bootstrap Failed"
        )

@router.post("/auth/register-via-invite",response_model=TokenResponse,status_code=status.HTTP_201_CREATED)
def team_users_register_via_invitation(invited: InviteRegister,db:SessionDB):
    token = invited.token

    try :
        invite = db.query(Invite).filter(Invite.token == token).first()

        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid invite Token"
            )

        if invite.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invite already used"
            )

        if invite.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="invite expired"
            )

        existing_user = db.query(User).filter(User.email == invite.email,User.org_id == invite.org_id).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists in organization."
            )

        user = User(
            email = invite.email,
            role = invite.role,
            org_id = invite.org_id,
            team_id = invite.team_id,
            password = hashed_password(invited.password)
        )

        db.add(user)

        invite.used_at = datetime.now(timezone.utc)

        db.flush()
        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            {"user_id": user.id}
        )

        return {
            "access_token" : access_token,
            "token_type" : "Bearer"
        }
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed."
        )

@router.get("/auth/invite-info/{token}",response_model=InvitePreview)
def invite_info(token:str, db:SessionDB):
    invite = db.query(Invite).filter(Invite.token == token).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Invite token"
        )

    org = invite.org

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    team = invite.team

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    inviter = invite.inviter

    if not inviter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inviter not found"
        )
    
    preview = InvitePreview(
        org_name = org.name,
        team_name = team.name,
        role = invite.role,
        invited_by_email = inviter.email,
        expires_at = invite.expires_at
    )
    return preview



@router.get("/auth/me",response_model=UserResponse)
def get_current_user_profile(current_user : User = Depends(get_current_user)):

    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not assigned to organization"
        )
    org = current_user.organization
        
    team = current_user.team

    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    
    return UserResponse(
        id = current_user.id,
        email = current_user.email,
        role = current_user.role,
        org_id = org.id,
        org_name = org.name,
        team_id = team.id,
        team_name = team.name,
        created_at= current_user.created_at
    )

    
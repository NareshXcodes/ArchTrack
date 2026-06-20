from dataclasses import dataclass
from typing import Optional
from fastapi import Depends, HTTPException, status
from app.models.users import User
from app.utils.oauth2 import get_current_user

@dataclass
class OrgContext:
    user : User
    org_id : int
    team_id : Optional[int]
    is_org_admin : bool

def get_org_context(current_user:User = Depends(get_current_user)) -> OrgContext:
    if current_user.org_id is None :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization"
        )
        
    return OrgContext(
        user=current_user,
        org_id=current_user.org_id,
        team_id=current_user.team_id,
        is_org_admin=current_user.role == "org_admin",
    )

def get_team_admin_context(ctx:OrgContext=Depends(get_org_context)) -> OrgContext:
    if ctx.user.role not in ["org_admin","team_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team admin access required"
        )

    return ctx

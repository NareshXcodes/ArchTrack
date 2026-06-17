from fastapi import Depends, HTTPException, status
from .oauth2 import get_current_user
from app.models.users import User

def require_role(*roles: str):

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


ADMIN_ONLY = require_role("admin")
ARCHITECTS = require_role("admin","architect")
REVIEWERS = require_role("admin","reviewer")
ALL_ROLES = require_role("admin","architect","reviewer","developer")
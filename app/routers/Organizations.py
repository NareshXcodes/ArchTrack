import re

from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import SessionDB, get_db
from app.models.organizations import Organization
from app.schemas.organization import OrgResponse, OrgUpdate, OrgDetailResponse
from app.utils.context import OrgContext, get_org_admin_context, get_org_context
from app.utils.org_query import OrgScopedQuery, get_scoped_query


router = APIRouter(prefix="/organizations",tags=['Organization'])

@router.get("/me", response_model=OrgDetailResponse)
def get_my_org_detail(ctx: OrgContext = Depends(get_org_context),sq : OrgScopedQuery = Depends(get_scoped_query)):
    org = ctx.user.organization

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not Found"
        )

    teams = sq.teams().all()

    total_members = sum(len(team.members) for team in teams)

    return OrgDetailResponse(
        id = org.id,
        name = org.name,
        slug = org.slug,
        created_by = org.created_by,
        created_at = org.created_at,
        teams = teams,
        total_members = total_members
    )

@router.put("/me",response_model=OrgResponse)
def update_org_detail(updated_org : OrgUpdate,ctx: OrgContext = Depends(get_org_admin_context),db:SessionDB = Depends(get_db)):
    org = ctx.user.organization

    updated_slug = updated_org.slug

    if updated_slug:
        if not re.match(updated_slug , r"^[a-z0-9-]+$"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid slug"
            )
        
        existing_slug = db.query(Organization).filter(Organization.slug == updated_slug).first()
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slug already exists"
            )

        org.slug = updated_slug

    if updated_org.name:
        org.name = updated_org.name

    db.commit()
    db.refresh(org)

    return org

from app.models.decisions import Decision
from app.models.projects import Project
from app.schemas.tag import TagUsageResponse
from fastapi import APIRouter, Depends
from app.models.tags import Tag, DecisionTag
from sqlalchemy import func
from typing import List
from app.utils.org_query import OrgScopedQuery, get_scoped_query


router = APIRouter(tags=['Tags'])

@router.get("/tags",response_model=List[TagUsageResponse])
def get_all_tags(sq: OrgScopedQuery = Depends(get_scoped_query)):

    query = sq.db.query(Tag, func.count(DecisionTag.decision_id)).join(DecisionTag, Tag.id == DecisionTag.tag_id).join(Decision, Decision.id == DecisionTag.decision_id).join(Project, Project.id == Decision.project_id).filter(Project.org_id == sq.org_id)

    if not sq.is_org_admin:
        query = query.filter(Project.team_id == sq.team_id)

    results = query.group_by(Tag.id).order_by(func.count(DecisionTag.decision_id).desc()).all()

    tags = [TagUsageResponse(id=tag.id,name=tag.name,usage_count=count) for tag , count in results]

    return tags
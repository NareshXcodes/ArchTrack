from app.db.database import SessionDB
from app.schemas.tag import TagUsageResponse
from fastapi import APIRouter
from app.models.tags import Tag, DecisionTag
from sqlalchemy import func
from typing import List


router = APIRouter(tags=['Tags'])

@router.get("/tags",response_model=List[TagUsageResponse])
def get_all_tags(db:SessionDB):

    results = db.query(Tag,func.count(DecisionTag.decision_id)).outerjoin(DecisionTag, Tag.id == DecisionTag.tag_id).group_by(Tag.id).order_by(func.count(DecisionTag.decision_id).desc()).all()

    tags = [TagUsageResponse(id=tag.id,name=tag.name,usage_count=count) for tag , count in results]

    return tags
from app.db.database import SessionDB
from app.schemas.decision import DecisionCreate, DecisionResponse, DecisionDetailResponse,DecisionUpdate
from app.schemas.option import OptionWithVotes
from app.schemas.comment import CommentResponse
from app.schemas.tag import TagResponse
from app.schemas.misc import StatusUpdate
from fastapi import APIRouter,status,HTTPException,Depends,Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.decisions import Decision, StatusEnum
from app.models.votes import Vote
from app.models.tags import DecisionTag , Tag
from app.models.projects import Project
from datetime import datetime , timezone
from sqlalchemy import func
from app.utils.workflow import validate_transition
from typing import List, Optional
from app.utils.permissions import ARCHITECTS

router = APIRouter(tags=['Decisions'])

@router.post("/projects/{project_id}/decisions", response_model=DecisionResponse ,status_code=status.HTTP_201_CREATED)
def create_decision(project_id:int, new_decision : DecisionCreate,db:SessionDB,current_user: User = Depends(ARCHITECTS)):
    project_data = db.query(Project).filter(Project.id == project_id).first()

    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found"
        )

    if project_data.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    decision = Decision(
        title=new_decision.title,
        context=new_decision.context,
        decision_made=new_decision.decision_made,
        consequences=new_decision.consequences,
        project_id=project_data.id,
        author_id=current_user.id
    )

    db.add(decision)
    db.flush()

    for tag_name in new_decision.tags:
        tag_name = tag_name.strip().lower()
        tag = db.query(Tag).filter(Tag.name == tag_name).first()

        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()

        decision_tag = DecisionTag(decision_id = decision.id, tag_id = tag.id)

        db.add(decision_tag)

    db.commit()
    db.refresh(decision)
    return decision


@router.get("/projects/{project_id}/decisions",response_model=List[DecisionResponse])
def all_decisions(project_id:int,db:SessionDB,tags: Optional[str] = None, decision_status: Optional[str]= None,current_user: User = Depends(get_current_user)):
    project_data = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found"
        )
    
    query = db.query(Decision).filter(Decision.project_id == project_id)

    if decision_status:
        valid_status=[
            "proposed",
            "under_review",
            "accepted",
            "deprecated",
            "superseded"
        ]

        decision_status = decision_status.lower()
        if decision_status not in valid_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status value Invalid"
            )
        
        query = query.filter(Decision.status == decision_status)

    if tags:
        query =  query.join(Decision.tags).filter(Tag.name == tags.lower())

    all_decision = query.all()
    return all_decision


@router.get("/decisions/{id}",response_model=DecisionDetailResponse)
def get_decision_detail(id:int, db:SessionDB, current_user: User = Depends(get_current_user)):
    fetch_decision = db.query(Decision).filter(Decision.id == id).first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision Not Found"
        )

    if current_user.id != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    user_vote = db.query(Vote).filter(Vote.user_id == current_user.id,Vote.decision_id == fetch_decision.id).first()

    options_response = []
    
    for option in fetch_decision.options:

        vote_count = db.query(func.count(Vote.id)).filter(Vote.option_id == option.id).scalar()

        options_response.append(
            OptionWithVotes(
                id = option.id,
                description=option.description,
                pros=option.pros,
                cons=option.cons,
                title=option.title,
                decision_id=option.decision_id,
                created_at=option.created_at,
                vote_count=vote_count
            )
        )

    comments_response = []

    for comment in fetch_decision.comments:
        comments_response.append(CommentResponse.model_validate(comment))

    return DecisionDetailResponse(
        id = fetch_decision.id,
        title=fetch_decision.title,
        context=fetch_decision.context,
        decision_made=fetch_decision.decision_made,
        consequences=fetch_decision.consequences,
        status = fetch_decision.status,
        author_id = fetch_decision.author_id,
        project_id = fetch_decision.project_id,
        tags =[
            TagResponse.model_validate(tag) for tag in fetch_decision.tags
        ],
        created_at = fetch_decision.created_at,
        updated_at = fetch_decision.updated_at,
        options = options_response,
        comments = comments_response,
        user_voted_option_id = (
            user_vote.option_id if user_vote else None
        )
    )


@router.put("/decisions/{id}",response_model=DecisionResponse)
def update_decisions(id: int,updated_decision :DecisionUpdate ,db:SessionDB,current_user: User = Depends(ARCHITECTS)):
    query = db.query(Decision).filter(Decision.id == id)
    update_fetch_decision = query.first()
    if not update_fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not Found"
        )

    if current_user.role == "architect" and update_fetch_decision.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    if update_fetch_decision.status.value == "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Accepted decision are Locked"
        )

    update_data = updated_decision.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    query.update(update_data,synchronize_session=False)
    db.commit()
    db.refresh(update_fetch_decision)
    return update_fetch_decision
    

@router.patch("/decisions/{id}/status",response_model=DecisionResponse)
def update_decision_status(id:int,updated_status:StatusUpdate,db:SessionDB,current_user: User = Depends(get_current_user)):
    query = db.query(Decision).filter(Decision.id == id)
    fetch_update_decision = query.first()

    if not fetch_update_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="decision not found"
        )
    current_status = fetch_update_decision.status.value
    new_status = updated_status.status
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use /admin/decisions/{id}/override"
        )
    elif current_user.role == "architect":
        # proposed -> under_review
        # rejected -> proposed
        if current_user.id != fetch_update_decision.author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Authorized"
            )
        if current_status == "proposed" or current_status == "rejected":
            validate_transition(current_status,new_status)
            fetch_update_decision.status = StatusEnum(new_status)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Architect cannot perform this transition"
            )
    elif current_user.role == "reviewer":
        #under_review -> accepted
        #under_review -> rejected
        if current_status == "under_review" and new_status != "proposed":
            validate_transition(current_status,new_status)
            fetch_update_decision.status = StatusEnum(new_status)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reviewer cannot perform this transition"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    fetch_update_decision.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(fetch_update_decision)

    return fetch_update_decision


@router.delete("/decisions/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_decision(id:int,db:SessionDB,current_user: User = Depends(get_current_user)):
    query = db.query(Decision).filter(Decision.id == id)
    fetch_decision = query.first()

    if not fetch_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="decision not found"
        )

    if current_user.id != fetch_decision.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    db.delete(fetch_decision)
    db.commit()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


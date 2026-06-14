from app.db.database import SessionDB
from app.schemas.project import ProjectCreate , ProjectResponse , ProjectUpdate
from app.schemas.misc import ProjectSummary
from fastapi import APIRouter,status,HTTPException,Depends, Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.projects import Project
from app.models.decisions import Decision
from app.models.tags import DecisionTag
from app.models.tags import Tag
from typing import List, Optional
from collections import Counter
from app.schemas.decision import DecisionCreate , DecisionResponse


router = APIRouter(prefix="/projects",tags=["Projects"])

@router.post("/",response_model=ProjectResponse ,status_code=status.HTTP_201_CREATED)
def createProject(db:SessionDB,new_project : ProjectCreate,current_user: User = Depends(get_current_user)):
    new_project = Project(**new_project.model_dump(),owner_id = current_user.id)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/",response_model=List[ProjectResponse])
def all_project(db:SessionDB,current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@router.get("/{id}",response_model=ProjectResponse)
def get_projects(id: int ,db:SessionDB,current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Project Not Found !!"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    return project

@router.put("/{id}",response_model=ProjectResponse)
def update_project(id:int, db:SessionDB ,updated_project : ProjectUpdate ,current_user: User = Depends(get_current_user)):
    query = db.query(Project).filter(Project.id == id)
    update_project = query.first()
    if not update_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found !!"
        )

    if current_user.id != update_project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    update_data = updated_project.model_dump(exclude_unset=True)
    query.update(update_data,synchronize_session=False)
    db.commit()
    db.refresh(update_project)
    return update_project

@router.delete("/{id}",status_code =status.HTTP_204_NO_CONTENT)
def delete_project(id:int, db:SessionDB,current_user: User = Depends(get_current_user) ):
    fetch_project = db.query(Project).filter(Project.id == id).first()

    if not fetch_project:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Project not Found"
        )

    if fetch_project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    db.delete(fetch_project)
    db.commit()
    return Response(
        status_code = status.HTTP_204_NO_CONTENT
    )

@router.get("/{id}/summary",response_model=ProjectSummary)
def stats(id:int, db:SessionDB,current_user: User = Depends(get_current_user)):

    # Total decisions
    project = db.query(Project).filter(Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not Found"
        )

    if current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    # count total decisions
    decisions = db.query(Decision).filter(Decision.project_id == id).all()
    total_decisions = len(decisions)

    #count status
    status_counter = Counter()
    tag_counter = Counter()

    for decision in decisions:
        status_counter[decision.status.value] += 1

        if decision.tags:
            for tag in decision.tags:
                tag_counter[tag.name] += 1

    most_used_tag = [
        tag_name
        for tag_name, _ in tag_counter.most_common(5)
    ]

    return ProjectSummary(
        total_decisions=total_decisions,
        decisions_per_status=dict(status_counter),
        top_tags=most_used_tag
    )


@router.post("/{project_id}/decisions", response_model=DecisionResponse ,status_code=status.HTTP_201_CREATED)
def create_decision(project_id:int, new_decision : DecisionCreate,db:SessionDB,current_user: User = Depends(get_current_user)):
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


@router.get("/{project_id}/decisions",response_model=List[DecisionResponse])
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
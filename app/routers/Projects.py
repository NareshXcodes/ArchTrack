from app.db.database import SessionDB
from app.schemas.project import ProjectCreate , ProjectResponse , ProjectUpdate
from app.schemas.misc import ProjectSummary
from fastapi import APIRouter,status,HTTPException,Depends, Response
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.projects import Project
from app.models.decisions import Decision
from collections import Counter
from typing import List


router = APIRouter(tags=["Projects"])

@router.post("/projects/",response_model=ProjectResponse ,status_code=status.HTTP_201_CREATED)
def createProject(db:SessionDB,new_project : ProjectCreate,current_user: User = Depends(get_current_user)):
    new_project = Project(**new_project.model_dump(),owner_id = current_user.id)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/projects/",response_model=List[ProjectResponse])
def all_projects(db:SessionDB,current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@router.get("/projects/{id}",response_model=ProjectResponse)
def get_project(id: int ,db:SessionDB,current_user: User = Depends(get_current_user)):
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

@router.put("/projects/{id}",response_model=ProjectResponse)
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

@router.delete("/projects/{id}",status_code =status.HTTP_204_NO_CONTENT)
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

@router.get("/projects/{id}/summary",response_model=ProjectSummary)
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
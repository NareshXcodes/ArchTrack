from app.db.database import SessionDB
from app.models.teams import Team
from app.schemas.project import ProjectCreate , ProjectResponse , ProjectUpdate
from app.schemas.misc import ProjectSummary
from fastapi import APIRouter,status,HTTPException,Depends, Response
from app.utils.context import OrgContext
from app.utils.oauth2 import get_current_user
from app.models.users import User
from app.models.projects import Project
from app.models.decisions import Decision
from collections import Counter
from typing import List

from app.utils.org_query import OrgScopedQuery, get_scoped_query


router = APIRouter(tags=["Projects"])

@router.post("/projects/",response_model=ProjectResponse ,status_code=status.HTTP_201_CREATED)
def createProject(payload : ProjectCreate,sq: OrgScopedQuery = Depends(get_scoped_query)):
    if sq.user.role not in ("org_admin", "team_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create projects"
        )

    if sq.is_org_admin:
        if payload.team_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team_id is required for org_admin"
            )

        team = sq.teams().filter(Team.id == payload.team_id).first()

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        team_id = team.id
    else:
        if sq.team_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not assigned to a team"
            )
        team_id = team.id

    project = Project(
        name=payload.name,
        description=payload.description,
        owner_id=sq.user.id,
        org_id=sq.org_id,
        team_id=team_id,
    )

    sq.db.add(project)
    sq.db.commit()
    sq.db.refresh(project)
    return project

@router.get("/projects/",response_model=List[ProjectResponse])
def all_projects(sq: OrgScopedQuery = Depends(get_scoped_query)):
    projects = sq.projects().all()
    return projects

@router.get("/projects/{id}",response_model=ProjectResponse)
def get_project(id: int ,sq: OrgScopedQuery = Depends(get_scoped_query)):
    project = sq.projects().filter(Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Project Not Found !!"
        )

    return project

@router.put("/projects/{id}",response_model=ProjectResponse)
def update_project(id:int ,updated_project : ProjectUpdate ,sq: OrgScopedQuery = Depends(get_scoped_query)):
    query = sq.projects().filter(Project.id == id)
    update_project = query.first()
    if not update_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found !!"
        )

    if update_project.owner_id != sq.user.id and sq.user.role not in ["team_admin","org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    update_data = updated_project.model_dump(exclude_unset=True)
    query.update(update_data,synchronize_session=False)
    sq.db.commit()
    sq.db.refresh(update_project)
    return update_project

@router.delete("/projects/{id}",status_code =status.HTTP_204_NO_CONTENT)
def delete_project(id:int, sq: OrgScopedQuery = Depends(get_scoped_query)):
    fetch_project = sq.projects().filter(Project.id == id).first()
    
    if not fetch_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Not Found !!"
        )

    if fetch_project.owner_id != sq.user.id and sq.user.role not in ["team_admin","org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )


    sq.db.delete(fetch_project)
    sq.db.commit()
    return Response(
        status_code = status.HTTP_204_NO_CONTENT
    )

@router.get("/projects/{id}/summary",response_model=ProjectSummary)
def stats(id:int, sq: OrgScopedQuery = Depends(get_scoped_query)):

    # Total decisions
    project = sq.projects().filter(Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not Found"
        )

    # count total decisions
    decisions = project.decisions
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
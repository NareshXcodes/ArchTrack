from sqlalchemy.orm import Session
from app.models.decisions import Decision
from app.models.projects import Project
from app.models.users import User
from app.models.teams import Team

class OrgScopedQuery:
    def __init__(self,db:Session,org_id:int,team_id:int | None,is_org_admin:bool):
        self.db = db
        self.org_id = org_id
        self.team_id = team_id
        self.is_org_admin = is_org_admin

    def projects(self):
        query = self.db.query(Project).filter(Project.org_id == self.org_id)

        if not self.is_org_admin:
            query = query.filter(Project.team_id == self.team_id)

        return query

    def decisions(self,project_id:int):
        query = self.db.query(Decision).join(Project,Project.id == Decision.project_id).filter(Project.org_id == self.org_id,Project.id == project_id)

        if not self.is_org_admin:
            query = query.filter(Project.team_id == self.team_id)

        return query

    def users(self):
        query = self.db.query(User).filter(User.org_id == self.org_id)

        return query

    def team_users(self):
        query = self.db.query(User).filter(User.org_id == self.org_id)

        if not self.is_org_admin:
            query = query.filter(User.team_id == self.team_id)

        return query

    def teams(self):
        query = self.db.query(Team).filter(Team.org_id == self.org_id)

        if not self.is_org_admin:
            query = query.filter(Team.id == self.team_id)

        return query
    
from fastapi import FastAPI , Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine , Base
from app.models.comments import Comment
from app.models.decisions import Decision, DecisionReviewer
from app.models.options import Option
from app.models.projects import Project
from app.models.tags import Tag , DecisionTag
from app.models.users import User
from app.models.votes import Vote
from app.models.reviewcomments import ReviewComment
from app.routers import auth , Projects, Decisions, Options, Comments, Tags, Votes,ReviewerAssignments
from app.utils.permissions import ADMIN_ONLY

Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
def root():
    return {"message" : "Welcome to the ADR Manager APP"}

@app.get("/test/role")
def admin_role(current_user = Depends(ADMIN_ONLY)):
    return {
        "message": "Access granted",
        "user_id": current_user.id,
        "role": current_user.role
    }


app.include_router(auth.router)
app.include_router(Projects.router)
app.include_router(Decisions.router)
app.include_router(Options.router)
app.include_router(Votes.router)
app.include_router(Comments.router)
app.include_router(Tags.router)
app.include_router(ReviewerAssignments.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
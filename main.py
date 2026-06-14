from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine , Base
from app.models.comments import Comment
from app.models.decisions import Decision
from app.models.options import Option
from app.models.projects import Project
from app.models.tags import Tag , DecisionTag
from app.models.users import User
from app.models.votes import Vote
from app.routers import auth , Projects, Decisions, Options

Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message" : "Welcome to the ADR Manager APP"}

app.include_router(auth.router)
app.include_router(Projects.router)
app.include_router(Decisions.router)
app.include_router(Options.router)
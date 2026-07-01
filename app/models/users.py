from colorama import Fore
from sqlalchemy import ForeignKey, Integer , String , DateTime , func
from sqlalchemy.orm import Mapped , mapped_column, relationship
from datetime import datetime
from typing import List 
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer , primary_key = True , index = True)

    email : Mapped[str] = mapped_column(String, unique=True , nullable=False,index=True)

    password : Mapped[str] = mapped_column(String,nullable=False)

    role :  Mapped[str] = mapped_column(String, default="developer", nullable=False)
    
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True) , 
        server_default = func.now()
    )

    org_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    team_id : Mapped[int] = mapped_column(
        ForeignKey("teams.id",ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        lazy="selectin"
    )

    votes : Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    projects : Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    decisions : Mapped[List["Decision"]] = relationship(
        "Decision",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    assigned_decisions: Mapped[list["Decision"]] = relationship(
        "Decision",
        secondary="decision_reviewers",
        primaryjoin="User.id == DecisionReviewer.reviewer_id",
        secondaryjoin="Decision.id == DecisionReviewer.decision_id",
        back_populates="reviewers"
    )

    review_comments : Mapped[List["ReviewComment"]] = relationship(
        "ReviewComment",
        back_populates="reviewer",
        cascade="all, delete-orphan"
    )

    audit_logs: Mapped[List["DecisionAudit"]] = relationship(
        "DecisionAudit",
        back_populates="changed_by_user"
    )

    invites_sent: Mapped[list["Invite"]] = relationship(
        "Invite",
        back_populates="inviter"
    )

    team : Mapped["Team | None"] = relationship(
        "Team",
        back_populates="members",
        foreign_keys=[team_id],
        lazy="selectin"
    )

    organization: Mapped["Organization | None"] = relationship(
        "Organization",
        back_populates="users",
        lazy="selectin"
    )
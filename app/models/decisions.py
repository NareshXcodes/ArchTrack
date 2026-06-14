from sqlalchemy.orm import Mapped , mapped_column, relationship
from sqlalchemy import Integer , DateTime , func, String, ForeignKey, Text
from app.db.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum
from typing import List

class StatusEnum(str,PyEnum):
    proposed = "proposed"
    under_review = "under_review"
    accepted = "accepted"
    deprecated = "deprecated"
    suspended = "suspended"

class Decision(Base):
    __tablename__ = "decisions"
    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False)

    title : Mapped[str] = mapped_column(String(200), nullable=False)

    context : Mapped[str] = mapped_column(Text,nullable=False)

    decision_made : Mapped[str] = mapped_column(Text, nullable=False)

    consequences : Mapped[str] = mapped_column(Text , nullable=True)

    status : Mapped[StatusEnum] = mapped_column(
        SQLEnum(StatusEnum), 
        default=StatusEnum.proposed,
        nullable=False
    )

    # projects
    project_id : Mapped[int] = mapped_column(
        ForeignKey("projects.id",ondelete="CASCADE") , 
        nullable=False
    )

    project : Mapped["Project"] = relationship(
        "Project" , 
        back_populates="decisions"
    )

    #users
    author_id : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    author : Mapped["User"] = relationship(
        "User" , 
        back_populates="decisions"
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    #previous it was Vote
    options : Mapped[List["Option"]] = relationship(
        "Option",
        back_populates="decision",
        cascade="all, delete-orphan"
    )


    comments : Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

    tags : Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="decision_tags",
        back_populates="decisions",
    )

    votes : Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="decision",
        cascade="all, delete-orphan"
    )

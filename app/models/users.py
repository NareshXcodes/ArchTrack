from sqlalchemy import Integer , String , DateTime , func
from sqlalchemy.orm import Mapped , mapped_column, relationship
from datetime import datetime
from typing import List 
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer , primary_key = True , index = True)
    email : Mapped[str] = mapped_column(String, unique=True , nullable=False,index=True)
    password : Mapped[str] = mapped_column(String,nullable=False)
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True) , 
        server_default = func.now()
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="author"
    )

    votes : Mapped[List["Vote"]] = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    projects : Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    decisions : Mapped[List["Decision"]] = relationship(
        "Decision",
        back_populates="author",
        cascade="all, delete-orphan"
    )



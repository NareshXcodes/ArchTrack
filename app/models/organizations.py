from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, DateTime, func
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Organization(Base):

    __tablename__="organizations"

    id : Mapped[int] = mapped_column(Integer,primary_key=True)

    name : Mapped[str] = mapped_column(String(100),nullable=False)

    slug : Mapped[str] = mapped_column(String(100),nullable=False ,unique=True, index=True)

    created_by : Mapped[int | None] = mapped_column(Integer, nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    teams : Mapped[List["Team"]] = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    invites : Mapped[List["Invite"]] = relationship(
        "Invite",
        back_populates="org",
        cascade="all, delete-orphan"
    )
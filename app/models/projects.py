from sqlalchemy.orm import Mapped , mapped_column, relationship
from sqlalchemy import Integer , DateTime , func, String, ForeignKey , Text,UniqueConstraint
from app.db.database import Base
from datetime import datetime
from typing import List

class Project(Base):
    __tablename__ = "projects"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)

    name : Mapped[str] = mapped_column(String(255), nullable=False)

    description : Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    __table_args__ = (
            UniqueConstraint(
            "owner_id",
            "name",
            name= "uq_name_user"
        ),
    )

    # Ownership of User and relationship established
    owner_id : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    owner : Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )

    decisions : Mapped[List["Decision"]] = relationship(
        "Decision",
        back_populates="project",
        cascade="all, delete-orphan"
    )
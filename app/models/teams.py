from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import List

class Team(Base):
    __tablename__ ="teams"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)

    name : Mapped[str] = mapped_column(String(100), nullable=False)

    org_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    admin_id : Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    transferred_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True) ,nullable=True)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now() ,nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "name",
            "org_id",
            name="uq_team_name_org"
        ),
    )

    organization : Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams"
    )

    members : Mapped[List["User"]] = relationship(
        "User",
        back_populates="team",
        foreign_keys="User.team_id"
    )

    invites: Mapped[list["Invite"]] = relationship(
        "Invite",
        back_populates="team"
    )

    projects : Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="team"
    )
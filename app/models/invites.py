from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import List

class Invite(Base):

    __tablename__="invites"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)

    email : Mapped[str] = mapped_column(String(255),nullable=False,index=True)

    role : Mapped[str] = mapped_column(String(20),nullable=False)

    token : Mapped[str] = mapped_column(String(64),unique=True,nullable=False, index=True)

    org_id : Mapped[int] = mapped_column(
        ForeignKey("organizations.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    team_id : Mapped[int] = mapped_column(
        ForeignKey("teams.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    invited_by : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    expires_at : Mapped[datetime] = mapped_column(DateTime(timezone=True))

    used_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    org : Mapped["Organization"] = relationship(
        "Organization",
        back_populates="invites"
    )

    team : Mapped["Team"] = relationship(
        "Team",
        back_populates="invites"
    )

    inviter : Mapped["User"]= relationship(
        "User",
        back_populates="invites_sent"
    )
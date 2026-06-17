from app.db.database import Base
from sqlalchemy import Text , Integer, ForeignKey,DateTime, func
from sqlalchemy.orm import Mapped,mapped_column, relationship
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

class VerdictEnum(str, PyEnum):
    approved = "approved"
    rejected = "rejected"
    needs_changes = "needs_changes"


class ReviewComment(Base):
    __tablename__ = "review_comments"
    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    decision_id : Mapped[int] = mapped_column(
        ForeignKey("decisions.id",ondelete="CASCADE"),
        nullable=False
    )
    reviewer_id : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )
    body : Mapped[str] = mapped_column(
        Text
    )
    verdict : Mapped[VerdictEnum] = mapped_column(
        SQLEnum(VerdictEnum),
        nullable=False
    )
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    decision: Mapped["Decision"] = relationship(
        "Decision",
        back_populates="review_comments"
    )

    reviewer: Mapped["User"] = relationship(
        "User",
        back_populates="review_comments"
    )
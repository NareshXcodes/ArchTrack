from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.decisions import StatusEnum


class DecisionAudit(Base):
    __tablename__ ="decision_audits"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    decision_id : Mapped[int] = mapped_column(
        ForeignKey("decisions.id",ondelete="CASCADE"),
        nullable=False
    )

    old_status : Mapped[StatusEnum] = mapped_column(
        String,
        nullable=False
    )

    new_status : Mapped[StatusEnum] = mapped_column(
        String,
        nullable=False
    )

    changed_by : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    decision : Mapped["Decision"] = relationship(
        "Decision",
        back_populates="audit_logs"
    )

    changed_by_user : Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs",
        foreign_keys=[changed_by]
    )
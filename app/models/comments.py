from sqlalchemy.orm import Mapped , mapped_column, relationship
from sqlalchemy import Integer , DateTime , func, ForeignKey, Text
from app.db.database import Base
from datetime import datetime



class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    decision_id: Mapped[int] = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE"),
        nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    decision: Mapped["Decision"] = relationship(
        "Decision",
        back_populates="comments"
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="comments"
    )
from sqlalchemy.orm import Mapped , mapped_column, relationship
from sqlalchemy import Integer , DateTime , func, ForeignKey, String, Text
from app.db.database import Base
from datetime import datetime



class Option(Base):
    __tablename__="options"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    title : Mapped[str] = mapped_column(
        String(200),
        nullable = False
    )

    description : Mapped[str | None] = mapped_column(
        Text,
        nullable = True
    )

    pros : Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    cons: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    decision_id : Mapped[int] = mapped_column(
        ForeignKey("decisions.id",ondelete="CASCADE"),
        nullable=False
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    decision : Mapped["Decision"] = relationship(
        "Decision",
        back_populates="options" 
    )

    votes: Mapped[list["Vote"]] = relationship(
        "Vote",
        back_populates="option",
        cascade="all, delete-orphan"
    )
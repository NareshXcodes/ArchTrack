from sqlalchemy.orm import Mapped , mapped_column, relationship
from sqlalchemy import Integer , DateTime , func, String, ForeignKey
from app.db.database import Base
from typing import List

class DecisionTag(Base):
    __tablename__="decision_tags"

    decision_id : Mapped[int] = mapped_column(
        ForeignKey("decisions.id",ondelete="CASCADE"),
        primary_key=True,
    )

    tag_id : Mapped[int] = mapped_column(
        ForeignKey("tags.id",ondelete="CASCADE"),
        primary_key=True,
    )


class Tag(Base):
    __tablename__ = "tags"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, index=True)
    name : Mapped[str] = mapped_column(String(225), unique=True, nullable=False)

    decisions : Mapped[List["Decision"]] = relationship(
        "Decision",
        secondary="decision_tags",
        back_populates="tags"
    )



    
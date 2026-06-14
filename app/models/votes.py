from sqlalchemy.orm import Mapped , mapped_column, relationship 
from sqlalchemy import Integer , ForeignKey , UniqueConstraint
from app.db.database import Base


class Vote(Base):
    __tablename__="votes"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key = True,
        index=True
    )

    user_id : Mapped[int] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )

    decision_id = mapped_column(
        ForeignKey("decisions.id", ondelete="CASCADE")
    )

    option_id = mapped_column(
        ForeignKey("options.id", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "decision_id",
            name="uq_user_decision_vote"
        ),
    )

    user : Mapped["User"] = relationship(
        "User",
        back_populates="votes"
    )

    decision : Mapped["Decision"] = relationship(
        "Decision",
        back_populates="votes"
    )

    option : Mapped["Option"] = relationship(
        "Option",
        back_populates="votes"
    )
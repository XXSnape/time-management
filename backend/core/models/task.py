from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, CheckConstraint, ForeignKey, String, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

if TYPE_CHECKING:
    from .user import User


class Task(Base):
    __table_args__ = (
        CheckConstraint(
            "hour_before_reminder >= 1 AND hour_before_reminder <= 24",
            name="ck_reminder_range",
        ),
    )
    name: Mapped[str]
    description: Mapped[str] = mapped_column(TEXT)
    deadline_datetime: Mapped[datetime]
    hour_before_reminder: Mapped[int]
    date_of_completion: Mapped[date | None] = mapped_column(
        default=None,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="tasks")

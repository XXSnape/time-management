from datetime import date

from sqlalchemy import TEXT, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Task(Base):
    __table_args__ = (
        CheckConstraint(
            "deadline_time >= 0 AND deadline_time <= 23",
            name="ck_time_range",
        ),
        CheckConstraint(
            "hour_before_reminder >= 1 AND hour_before_reminder <= 24",
            name="ck_reminder_range",
        ),
    )
    name: Mapped[str]
    description: Mapped[str] = mapped_column(TEXT)
    deadline_date: Mapped[date]
    deadline_time: Mapped[int]
    hour_before_reminder: Mapped[int]
    date_of_completion: Mapped[date | None] = mapped_column(
        default=None,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

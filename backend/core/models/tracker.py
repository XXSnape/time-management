from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .habit import Habit


class Tracker(Base):
    __tablename__ = "tracking"

    __table_args__ = (
        UniqueConstraint(
            "reminder_date",
            "reminder_hour",
            "habit_id",
        ),
    )

    reminder_date: Mapped[date]
    reminder_hour: Mapped[int]
    is_completed: Mapped[bool]
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
    )
    habit: Mapped["Habit"] = relationship(back_populates="trackers")

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from core.utils.enums import Weekday

if TYPE_CHECKING:
    from .habit import Habit


class Schedule(Base):
    __table_args__ = (
        UniqueConstraint(
            "day",
            "habit_id",
        ),
    )
    day: Mapped[Weekday]
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
    )
    habit: Mapped["Habit"] = relationship(back_populates="schedules")

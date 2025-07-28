from enum import StrEnum, auto

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Weekday(StrEnum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()


class Schedule(Base):
    day: Mapped[Weekday]
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
    )

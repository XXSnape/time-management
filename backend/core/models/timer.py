from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .habit import Habit


class Timer(Base):
    __table_args__ = (
        CheckConstraint(
            "notification_hour >= 0 AND notification_hour <= 23",
            name="ck_notification_hour_range",
        ),
    )
    notification_hour: Mapped[int]
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"),
    )
    habit: Mapped["Habit"] = relationship(back_populates="timers")

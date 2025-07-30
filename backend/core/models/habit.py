from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, ForeignKey, func
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .schedule import Schedule
    from .timer import Timer


class Habit(Base):
    name: Mapped[str]
    purpose: Mapped[str] = mapped_column(TEXT)
    created: Mapped[date] = mapped_column(server_default=func.current_date())
    date_of_completion: Mapped[date | None] = mapped_column(
        default=None,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    timers: Mapped[list["Timer"]] = relationship(back_populates="habit")
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="habit")

    hours: AssociationProxy[list[str]] = association_proxy(
        "timers", "notification_hour"
    )
    days: AssociationProxy[list[str]] = association_proxy("schedules", "day")

from sqlalchemy import TEXT, func, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from .base import Base


class Habit(Base):
    __table_args__ = (
        CheckConstraint(
            "notification_hour >= 0 AND notification_hour <= 23",
            name="ck_notification_hour_range",
        ),
    )
    name: Mapped[str]
    purpose: Mapped[str] = mapped_column(TEXT)
    notification_hour: Mapped[int]
    created: Mapped[date] = mapped_column(server_default=func.current_date())
    date_of_completion: Mapped[date | None] = mapped_column(
        default=None,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

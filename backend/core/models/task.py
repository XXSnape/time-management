from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import TEXT, CheckConstraint, ForeignKey, extract, func, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from core.utils.dt import get_moscow_tz_and_dt


if TYPE_CHECKING:
    from .user import User


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
    user: Mapped["User"] = relationship(back_populates="tasks")

    @hybrid_property
    def full_datetime(self):
        moscow_tz, _ = get_moscow_tz_and_dt()
        return datetime(
            year=self.deadline_date.year,
            month=self.deadline_date.month,
            day=self.deadline_date.day,
            hour=self.deadline_time,
            tzinfo=moscow_tz,
        )

    @full_datetime.expression
    def full_datetime(cls):
        return func.timezone(
            "UTC+3",
            func.to_timestamp(
                func.concat(
                    func.to_char(cls.deadline_date, "YYYY-MM-DD"),
                    " ",
                    func.lpad(func.cast(cls.deadline_time, String), 2, "0"),
                    ":00:00",
                ),
                "YYYY-MM-DD HH24:MI:SS",
            ),
        )

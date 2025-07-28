from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Tracker(Base):
    __tablename__ = "tracking"

    reminder_date: Mapped[date]
    is_completed: Mapped[bool] = mapped_column(
        default=False,
        server_default="0",
    )

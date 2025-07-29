from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .task import Task


class User(Base):
    """
    Модель пользователя.
    """

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
    tasks: Mapped["Task"] = relationship(back_populates="user")

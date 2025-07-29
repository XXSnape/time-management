from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """
    Модель пользователя.
    """

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

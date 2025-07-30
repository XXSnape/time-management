from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    access_token: Mapped[str]

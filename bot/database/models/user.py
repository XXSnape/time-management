from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from core.enums import Languages


class User(Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        unique=True,
    )
    access_token: Mapped[str]
    language: Mapped[Languages] = mapped_column(
        default=Languages.ru, server_default=Languages.ru
    )

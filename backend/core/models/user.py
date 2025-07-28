from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """
    Модель пользователя.

    username - юзернейм
    password - пароль
    is_active - True, если пользователь активен, иначе False
    """

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

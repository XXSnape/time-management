from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from .base import Base


class User(Base):
    """
    Модель пользователя.

    username - юзернейм
    password - пароль
    is_active - True, если пользователь активен, иначе False
    """

    username: Mapped[str]
    password: Mapped[bytes]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from core.config import settings


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Возвращает название таблицы по имени модели.
        """
        return f"{cls.__name__.lower()}s"

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
    number_output_fields = 2

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Возвращает название таблицы по имени модели.
        """
        return f"{cls.__name__.lower()}s"

    def __repr__(self) -> str:
        """
        Возвращает строку с первыми 3 колонками и значениями.
        """
        cols = [
            f"{field}={getattr(self, field)}"
            for field in self.__table__.columns.keys()[
                : self.number_output_fields
            ]
        ]

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

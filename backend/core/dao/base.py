import logging
from datetime import timedelta

from pydantic import BaseModel
from sqlalchemy import delete, select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Base
from core.utils.enums import Periods

logger = logging.getLogger(__name__)


class BaseDAO[M: Base]:
    """
    Базовый класс DAO для работы с моделями SQLAlchemy.
    """

    model: type[M] | None = None
    periods: tuple[tuple[timedelta, Periods], ...] = (
        (timedelta(weeks=1), "1 Week"),
        (timedelta(weeks=4), "1 Month"),
        (timedelta(weeks=12), "3 Months"),
        (timedelta(weeks=26), "6 Months"),
        (timedelta(weeks=39), "9 Months"),
        (timedelta(weeks=52), "1 Year"),
        (None, "Аll time"),
    )

    def __init__(self, session: AsyncSession):
        """
        Инициализация DAO сессией SQLAlchemy.
        """
        self._session = session
        if self.model is None:
            raise ValueError(
                "Модель должна быть указана в дочернем классе"
            )

    async def add(self, values: BaseModel) -> M:
        """
        Добавляет новую запись в базу данных.
        """
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            "Добавление записи %s с параметрами: %s",
            self.model.__name__,
            values_dict,
        )
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            await self._session.flush()
            logger.info(
                "Запись %s успешно добавлена.", self.model.__name__
            )
            return new_instance
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error("Ошибка при добавлении записи %s", e)
            raise

    async def find_one_or_none(self, filters: BaseModel) -> M | None:
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            "Поиск одной записи %s по фильтрам: %s",
            self.model.__name__,
            filter_dict,
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            logger.info(
                "Запись %s по фильтрам: %s",
                "найдена" if record else "не найдена",
                filter_dict,
            )
            return record
        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при поиске записи по фильтрам %s: %s",
                filter_dict,
                e,
            )
            raise

    async def update(
        self,
        filters: BaseModel,
        values: BaseModel,
        exclude: set[str] | None = None,
    ) -> int:
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(
            exclude_unset=True, exclude=exclude
        )
        if not values_dict:
            return 0
        logger.info(
            "Обновление записей %s по фильтру: %s с параметрами: %s",
            self.model.__name__,
            filter_dict,
            values_dict,
        )
        try:
            query = (
                update(self.model)
                .where(
                    *[
                        getattr(self.model, k) == v
                        for k, v in filter_dict.items()
                    ]
                )
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            await self._session.flush()
            logger.info("Обновлено %s записей.", result.rowcount)
            return result.rowcount
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error("Ошибка при обновлении записей: %s", e)
            raise

    async def delete(self, filters: BaseModel) -> int:
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            "Удаление записей %s по фильтру: %s",
            self.model.__name__,
            filter_dict,
        )
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError(
                "Нужен хотя бы один фильтр для удаления."
            )
        try:
            query = delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            await self._session.flush()
            logger.info("Удалено %s записей.", result.rowcount)
            return result.rowcount
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error("Ошибка при удалении записей: %s", e)
            raise

    async def add_many(
        self,
        instances: list[BaseModel],
    ) -> list[M]:
        values_list = [
            item.model_dump(exclude_unset=True) for item in instances
        ]
        logger.info(
            "Добавление нескольких записей %s. Количество: %s",
            self.model.__name__,
            len(values_list),
        )
        try:
            new_instances = [
                self.model(**values) for values in values_list
            ]
            self._session.add_all(new_instances)
            await self._session.flush()
            logger.info(
                "Успешно добавлено %s записей.", len(new_instances)
            )
            return new_instances
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(
                "Ошибка при добавлении нескольких записей: %s", e
            )
            raise

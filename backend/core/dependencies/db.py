"""
Модуль для работы с базой данных.
"""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated, TypeAlias

from core.config import settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

log = logging.getLogger(__name__)


class DBHelper:
    """
    Класс - помощник для работы с базой данных.
    """

    def __init__(self, url: str, echo: bool = False) -> None:
        """
        Инициализация класса.

        Параметры:
        url: Строка для подключения к базе данных
        echo: Принимает значения True или False

        Если установлен в True, то в консоль будут
        выводиться запросы к базе. По умолчанию False.
        """
        self.engine = create_async_engine(
            url=url, echo=echo
        )  # Двигатель для работы с асинхронной базой данных
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autocommit=False,
            expire_on_commit=False,
        )  # Фабрика сессий для работы с асинхронной базой данных

    async def dispose(self) -> None:
        """
        Освобождает ресурсы, связанные с базой данных.
        """
        await self.engine.dispose()
        log.info("Соединение с базой данных закрыто.")

    async def get_async_session_without_commit(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Возвращает сессию для асинхронной работы с базой данных.
        """
        async with self.session_factory() as session:  # type: AsyncSession
            yield session

    async def get_async_session_with_commit(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Возвращает сессию для асинхронной работы с базой данных и делает коммит.
        """
        async with self.session_factory() as session:  # type: AsyncSession
            yield session
            await session.commit()


db_helper = DBHelper(
    url=settings.db.url,
    echo=settings.db.echo,
)

SessionWithoutCommit: TypeAlias = Annotated[
    AsyncSession, Depends(db_helper.get_async_session_without_commit)
]

SessionWithCommit: TypeAlias = Annotated[
    AsyncSession, Depends(db_helper.get_async_session_with_commit)
]

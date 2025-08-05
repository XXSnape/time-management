"""
Модуль с настройками для тестов.
"""

from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings
from core.dependencies.db import db_helper
from core.models import Base, User
from services.auth import get_access_token, hash_password
from main import main_app


engine = create_async_engine(settings.db.url, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        session.add_all(
            [
                User(
                    username="user1",
                    telegram_id=111,
                    password=hash_password("123"),
                )
            ]
        )

        await session.commit()


@pytest.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генерирует сессию для асинхронного взаимодействия с тестовой базой данных внутри тестов.
    """
    async with async_session_maker() as session:  # type: AsyncSession
        yield session


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """
    Возвращает клиента для асинхронного взаимодействия с приложением внутри тестов.
    """

    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test/api/v1",
        cookies={
            "access-token": get_access_token(
                user_id=1,
                username="user1",
            )
        },
    ) as ac:
        yield ac


async def override_get_async_session_without_commit() -> (
    AsyncGenerator[AsyncSession, None]
):
    """
    Генерирует сессию для асинхронного взаимодействия
    с тестовой базой данных внутри приложения без коммита.
    """
    async with async_session_maker() as session:  # type: AsyncSession
        yield session


async def override_get_async_session_with_commit() -> (
    AsyncGenerator[AsyncSession, None]
):
    """
    Генерирует сессию для асинхронного взаимодействия
    с тестовой базой данных внутри приложения c коммитом.
    """
    async with async_session_maker() as session:  # type: AsyncSession
        yield session
        await session.commit()


main_app.dependency_overrides[
    db_helper.get_async_session_with_commit
] = override_get_async_session_with_commit
main_app.dependency_overrides[
    db_helper.get_async_session_without_commit
] = override_get_async_session_without_commit

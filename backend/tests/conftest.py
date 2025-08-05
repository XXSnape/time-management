"""
Модуль с настройками для тестов.
"""

from typing import AsyncGenerator
from datetime import datetime, timedelta, UTC

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
from core.models import Base, User, Task
from services.auth import get_access_token, hash_password
from main import main_app


engine = create_async_engine(settings.db.url, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)


@pytest.fixture
def user2_token():
    """
    Генерирует токен для второго пользователя.
    """
    return get_access_token(
        user_id=2,
        username="user2",
    )


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        user1 = User(
            username="user1",
            telegram_id=111,
            password=hash_password("123"),
        )
        session.add(user1)
        user2 = User(
            username="user2",
            telegram_id=222,
            password=hash_password("456"),
        )
        session.add(user2)
        await session.flush()

        now = datetime.now(UTC)
        tasks = [
            Task(
                name="Task 1",
                description="Первое задание",
                deadline_datetime=now + timedelta(hours=2),
                hour_before_reminder=2,
                user_id=user1.id,
            ),
            Task(
                name="Task 2",
                description="Второе задание",
                deadline_datetime=now + timedelta(minutes=2),
                hour_before_reminder=5,
                user_id=user1.id,
            ),
            Task(
                name="Task 3",
                description="Третье задание",
                deadline_datetime=now + timedelta(hours=3),
                hour_before_reminder=1,
                user_id=user1.id,
            ),
            Task(
                name="Task 4",
                description="Четвертое задание",
                deadline_datetime=now + timedelta(days=3),
                hour_before_reminder=1,
                user_id=user1.id,
                date_of_completion=now.date(),
            ),
        ]
        session.add_all(tasks)
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

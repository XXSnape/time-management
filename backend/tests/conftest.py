"""
Модуль с настройками для тестов.
"""

from typing import AsyncGenerator
from datetime import datetime, timedelta, UTC, date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from create_certs import create_private_and_public_keys
from core.config import settings
from core.dependencies.db import db_helper
from core.models import (
    Base,
    User,
    Task,
    Habit,
    Timer,
    Tracker,
    Schedule,
)
from core.utils.enums import Weekday
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
        user_id=2, username="user2", is_admin=False
    )


@pytest.fixture(scope="session", autouse=True)
async def init_workspace():
    create_private_and_public_keys()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        user1 = User(
            username="user1",
            telegram_id=111,
            password=hash_password("123"),
            is_admin=True,
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
            Task(
                name="Просроченное задание",
                description="Не отправлено вовремя",
                deadline_datetime=now - timedelta(days=3),
                hour_before_reminder=1,
                user_id=user1.id,
            ),
        ]
        session.add_all(tasks)

        habit1 = Habit(
            name="Утренняя зарядка",
            purpose="Быть бодрым",
            user_id=user1.id,
        )
        habit2 = Habit(
            name="Чтение",
            purpose="Развиваться",
            user_id=user1.id,
        )
        habit3 = Habit(
            name="Медитация",
            purpose="Снизить стресс",
            user_id=user1.id,
            date_of_completion=now.date(),
        )
        session.add_all([habit1, habit2, habit3])
        await session.flush()

        timers1 = [
            Timer(notification_hour=7, habit_id=habit1.id),
            Timer(notification_hour=8, habit_id=habit1.id),
        ]
        schedules1 = [
            Schedule(day=Weekday.MONDAY, habit_id=habit1.id),
            Schedule(day=Weekday.TUESDAY, habit_id=habit1.id),
        ]
        trackers1 = [
            Tracker(
                reminder_date=date(year=2025, month=8, day=4),
                reminder_hour=7,
                is_completed=True,
                habit_id=habit1.id,
            ),
            Tracker(
                reminder_date=now.date(),
                reminder_hour=8,
                is_completed=False,
                habit_id=habit1.id,
            ),
        ]

        timers2 = [
            Timer(notification_hour=8, habit_id=habit2.id),
            Timer(notification_hour=21, habit_id=habit2.id),
        ]
        schedules2 = [
            Schedule(day=Weekday.TUESDAY, habit_id=habit2.id),
            Schedule(day=Weekday.WEDNESDAY, habit_id=habit2.id),
        ]
        trackers2 = [
            Tracker(
                reminder_date=now.date(),
                reminder_hour=21,
                is_completed=True,
                habit_id=habit2.id,
            ),
        ]

        timers3 = [
            Timer(notification_hour=7, habit_id=habit3.id),
            Timer(notification_hour=8, habit_id=habit3.id),
        ]
        schedules3 = [
            Schedule(day=Weekday.MONDAY, habit_id=habit3.id),
            Schedule(day=Weekday.TUESDAY, habit_id=habit3.id),
            Schedule(day=Weekday.SUNDAY, habit_id=habit3.id),
        ]
        trackers3 = [
            Tracker(
                reminder_date=now.date(),
                reminder_hour=10,
                is_completed=True,
                habit_id=habit3.id,
            ),
        ]

        session.add_all(timers1 + timers2 + timers3)
        session.add_all(schedules1 + schedules2 + schedules3)
        session.add_all(trackers1 + trackers2 + trackers3)
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
                is_admin=True,
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

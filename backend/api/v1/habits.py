import logging
from typing import Annotated

from fastapi import APIRouter, Query, status

from core.dao.habits import HabitsDAO
from core.dependencies.auth import UserId
from core.dependencies.db import (
    SessionWithCommit,
    SessionWithoutCommit,
)

from core.schemas.common import PaginationSchema
from core.schemas import habits as habits_schemas
from core.schemas.result import ResultSchema
from core.utils.enums import Weekday
from services import habits
from services.common import delete_entity

log = logging.getLogger(__name__)


router = APIRouter(tags=["Привычки"])


@router.post(
    "",
    response_model=habits_schemas.HabitOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_habit(
    habit_in: habits_schemas.HabitInSchema,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await habits.create_habit(
        habit_in=habit_in, user_id=user_id, session=session
    )


@router.get(
    "/schedules", response_model=habits_schemas.HabitsWithUserSchema
)
async def get_habits_on_schedule(
    day: Weekday,
    hour: Annotated[int, Query(ge=0, le=23)],
    session: SessionWithoutCommit,
):
    return await habits.get_habits_on_schedule(
        session=session, day=day, hour=hour
    )


@router.get(
    "/statistics",
    response_model=habits_schemas.HabitStatisticsSchema,
)
async def get_statistics(
    session: SessionWithoutCommit, user_id: UserId
):
    return await habits.get_habit_statistics(
        session=session,
        user_id=user_id,
    )


@router.get(
    "", response_model=habits_schemas.PaginatedHabitsOutSchema
)
async def get_active_user_habits(
    user_id: UserId,
    session: SessionWithoutCommit,
    page: Annotated[
        int,
        Query(
            ge=1,
            le=1_000_000,
            description="Страница для пагинации (начиная с 1)",
        ),
    ] = 1,
    per_page: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество записей на странице (макс. 100)",
        ),
    ] = 10,
):
    return await habits.get_active_user_habits(
        session=session,
        user_id=user_id,
        page=page,
        per_page=per_page,
    )


@router.patch(
    "/{habit_id}",
    response_model=habits_schemas.HabitOutSchema,
)
async def update_habit(
    updated_habit_in: habits_schemas.HabitUpdateSchema,
    habit_id: int,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await habits.update_habit(
        session=session,
        habit_id=habit_id,
        user_id=user_id,
        updated_habit_in=updated_habit_in,
    )


@router.delete(
    "/{habit_id}",
    response_model=PaginationSchema,
)
async def delete_habit(
    habit_id: int,
    user_id: UserId,
    session: SessionWithCommit,
    per_page: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество записей на странице (макс. 100)",
        ),
    ] = 10,
):
    return await delete_entity(
        session=session,
        user_id=user_id,
        entity_id=habit_id,
        dao=HabitsDAO,
        exc=habits.exc,
        per_page=per_page,
    )


@router.post(
    "/{habit_id}/mark",
    response_model=ResultSchema,
    status_code=status.HTTP_201_CREATED,
)
async def mark_habit(
    habit_id: int,
    user_id: UserId,
    tracker_in: habits_schemas.TrackerInSchema,
    session: SessionWithCommit,
):
    return await habits.mark_habit(
        tracker_in=tracker_in,
        habit_id=habit_id,
        user_id=user_id,
        session=session,
    )


@router.get(
    "/{habit_id}",
    response_model=habits_schemas.HabitOutSchema,
)
async def get_habit_by_id(
    habit_id: int,
    user_id: UserId,
    session: SessionWithoutCommit,
):
    return await habits.get_habit_by_id(
        session=session, user_id=user_id, habit_id=habit_id
    )

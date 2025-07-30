import logging

from fastapi import APIRouter, status

from core.dao.habits import HabitsDAO
from core.dependencies.auth import UserId
from core.dependencies.db import SessionWithCommit
from core.schemas.habits import HabitOutSchema, HabitInSchema, HabitUpdateSchema
from services import habits
from services.common import delete_entity

log = logging.getLogger(__name__)


router = APIRouter(tags=["Привычки"])


@router.post(
    "",
    response_model=HabitOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_habit(
    habit_in: HabitInSchema,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await habits.create_habit(
        habit_in=habit_in, user_id=user_id, session=session
    )


@router.patch(
    "/{habit_id}",
    response_model=HabitOutSchema,
)
async def update_habit(
    updated_habit_in: HabitUpdateSchema,
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
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_habit(
    habit_id: int,
    user_id: UserId,
    session: SessionWithCommit,
):
    await delete_entity(
        session=session,
        user_id=user_id,
        entity_id=habit_id,
        dao=HabitsDAO,
        exc=habits.exc,
    )

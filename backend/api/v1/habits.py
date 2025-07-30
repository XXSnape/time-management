import logging

from fastapi import APIRouter, status

from core.dependencies.auth import UserId
from core.dependencies.db import SessionWithCommit
from core.schemas.habits import HabitOutSchema, HabitInSchema
from services import habits


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
    # pass

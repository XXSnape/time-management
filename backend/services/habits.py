from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.habits import HabitsDAO
from core.dao.schedules import SchedulesDAO
from core.dao.timers import TimersDAO
from core.schemas.common import IdSchema
from core.schemas.habits import (
    HabitInSchema,
    HabitCreateSchema,
    ScheduleSchema,
    TimerSchema,
    HabitOutSchema,
)


async def create_habit(
    habit_in: HabitInSchema,
    user_id: int,
    session: AsyncSession,
) -> HabitOutSchema:
    dao = HabitsDAO(session=session)
    habit = await dao.add(
        HabitCreateSchema(**habit_in.model_dump(), user_id=user_id),
    )

    await SchedulesDAO(session=session).add_many(
        [ScheduleSchema(day=day, habit_id=habit.id) for day in habit_in.days]
    )
    await TimersDAO(session=session).add_many(
        [
            TimerSchema(notification_hour=hour, habit_id=habit.id)
            for hour in habit_in.hours
        ]
    )
    created_habit = await dao.get_habit_with_all_data(IdSchema(id=habit.id))
    return HabitOutSchema.model_validate(
        created_habit,
        from_attributes=True,
    )

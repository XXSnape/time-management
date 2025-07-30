from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.habits import HabitsDAO
from core.dao.schedules import SchedulesDAO
from core.dao.timers import TimersDAO
from core.dao.trackers import TrackersDAO
from core.schemas.common import (
    DateOfCompletionSchema,
    IdSchema,
    BaseStatisticSchema,
)
from core.schemas.habits import (
    HabitCreateSchema,
    HabitIdSchema,
    HabitInSchema,
    HabitOutSchema,
    HabitUpdateSchema,
    LittleInfoHabitOutSchema,
    PaginatedHabitsOutSchema,
    ScheduleSchema,
    TimerSchema,
    TrackerInSchema,
    TrackerCreateSchema,
    HabitsWithUserSchema,
    HabitWithUserSchema,
    HabitStatisticsSchema,
)
from core.schemas.result import ResultSchema
from core.utils.enums import Weekday

exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Привычка не найдена",
)


async def create_schedulers_and_timers(
    session: AsyncSession,
    habit_id: int,
    days: set[Weekday] | None,
    hours: set[int] | None,
):
    habit_id_schema = HabitIdSchema(habit_id=habit_id)
    if days:
        schedule_dao = SchedulesDAO(session=session)
        await schedule_dao.delete(habit_id_schema)
        await schedule_dao.add_many(
            [
                ScheduleSchema(day=day, habit_id=habit_id)
                for day in days
            ]
        )
    if hours:
        timers_dao = TimersDAO(session=session)
        await timers_dao.delete(habit_id_schema)
        await timers_dao.add_many(
            [
                TimerSchema(
                    notification_hour=hour, habit_id=habit_id
                )
                for hour in hours
            ]
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
    await create_schedulers_and_timers(
        session=session,
        habit_id=habit.id,
        days=habit_in.days,
        hours=habit_in.hours,
    )
    created_habit = await dao.get_habit_with_all_data(
        IdSchema(id=habit.id)
    )
    return HabitOutSchema.model_validate(
        created_habit,
        from_attributes=True,
    )


async def update_habit(
    session: AsyncSession,
    habit_id: int,
    user_id: int,
    updated_habit_in: HabitUpdateSchema,
):
    dao = HabitsDAO(session=session)
    habit = await dao.find_one_or_none(
        DateOfCompletionSchema(
            id=habit_id,
            user_id=user_id,
        )
    )
    if not habit:
        raise exc
    await dao.update(
        filters=IdSchema(id=habit_id),
        values=updated_habit_in,
        exclude={"days", "hours"},
    )
    await create_schedulers_and_timers(
        session=session,
        habit_id=habit.id,
        days=updated_habit_in.days,
        hours=updated_habit_in.hours,
    )
    updated_habit = await dao.get_habit_with_all_data(
        IdSchema(id=habit_id)
    )
    return HabitOutSchema.model_validate(
        updated_habit,
        from_attributes=True,
    )


async def get_active_user_habits(
    session: AsyncSession,
    user_id: int,
    page: int,
    per_page: int,
) -> PaginatedHabitsOutSchema:
    habits, total_count = await HabitsDAO(
        session=session
    ).get_active_user_habits(
        user_id=user_id, page=page, per_page=per_page
    )
    return PaginatedHabitsOutSchema(
        items=[
            LittleInfoHabitOutSchema.model_validate(
                habit,
                from_attributes=True,
            )
            for habit in habits
        ],
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


async def get_habit_by_id(
    session: AsyncSession,
    user_id: int,
    habit_id: int,
) -> HabitOutSchema:
    habit = await HabitsDAO(session=session).get_habit_with_all_data(
        DateOfCompletionSchema(user_id=user_id, id=habit_id)
    )
    if not habit:
        raise exc
    return HabitOutSchema.model_validate(
        habit,
        from_attributes=True,
    )


async def mark_habit(
    session: AsyncSession,
    tracker_in: TrackerInSchema,
    user_id: int,
    habit_id: int,
) -> ResultSchema:
    res = await HabitsDAO(session=session).find_one_or_none(
        DateOfCompletionSchema(user_id=user_id, id=habit_id)
    )
    if not res:
        raise exc
    try:
        await TrackersDAO(session=session).add(
            TrackerCreateSchema(
                **tracker_in.model_dump(), habit_id=habit_id
            )
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="За эту дату и время привычка уже отмечена",
        )
    return ResultSchema()


async def get_habits_on_schedule(
    session: AsyncSession,
    day: Weekday,
    hour: int,
):
    habits = await HabitsDAO(session=session).get_habits_on_schedule(
        day=day, hour=hour
    )
    return HabitsWithUserSchema(
        items=[
            HabitWithUserSchema.model_validate(
                habit, from_attributes=True
            )
            for habit in habits
        ]
    )


async def get_habit_statistics(
    session: AsyncSession,
    user_id: int,
) -> HabitStatisticsSchema:
    stats = await HabitsDAO(session=session).get_statistics(
        user_id=user_id
    )
    return HabitStatisticsSchema(
        items=[
            BaseStatisticSchema.model_validate(
                stat, from_attributes=True
            )
            for stat in stats
        ]
    )

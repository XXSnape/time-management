import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.tasks import TasksDao
from core.schemas.common import IdSchema
from core.schemas.tasks import (
    TaskCreateSchema,
    TaskInSchema,
    TaskOutSchema,
    TaskUpdateSchema,
    TaskSchema,
)
from fastapi import status


async def create_task(
    session: AsyncSession,
    user_id: int,
    task_in: TaskInSchema,
) -> TaskOutSchema:
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    dt = datetime.datetime(
        year=task_in.deadline_date.year,
        month=task_in.deadline_date.month,
        day=task_in.deadline_date.day,
        hour=task_in.deadline_time,
        tzinfo=moscow_tz,
    )
    moscow_dt = datetime.datetime.now(moscow_tz)
    if moscow_dt >= dt:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Входящие дата и время меньше, чем текущее московское",
        )

    task = await TasksDao(session=session).add(
        TaskCreateSchema(
            **task_in.model_dump(),
            user_id=user_id,
        )
    )
    return TaskOutSchema.model_validate(task, from_attributes=True)


async def update_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    updated_task_in: TaskUpdateSchema,
) -> TaskOutSchema:
    dao = TasksDao(session=session)
    task = await dao.find_one_or_none(
        TaskSchema(
            id=task_id,
            user_id=user_id,
        )
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Действующая задача не найдена",
        )
    await dao.update(filters=IdSchema(id=task_id), values=updated_task_in)
    return TaskOutSchema.model_validate(task, from_attributes=True)

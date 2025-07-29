import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.tasks import TasksDao
from core.schemas.common import IdSchema
from core.schemas.result import ResultSchema
from core.schemas.tasks import (
    TaskCreateSchema,
    TaskInSchema,
    TaskOutSchema,
    TaskUpdateSchema,
    TaskSchema,
)
from fastapi import status

from core.utils.dt import get_moscow_tz_and_dt

exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Действующая задача не найдена",
)


async def create_task(
    session: AsyncSession,
    user_id: int,
    task_in: TaskInSchema,
) -> TaskOutSchema:
    moscow_tz, moscow_dt = get_moscow_tz_and_dt()
    dt = datetime.datetime(
        year=task_in.deadline_date.year,
        month=task_in.deadline_date.month,
        day=task_in.deadline_date.day,
        hour=task_in.deadline_time,
        tzinfo=moscow_tz,
    )
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


async def get_active_tasks():
    pass


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
        raise exc
    await dao.update(filters=IdSchema(id=task_id), values=updated_task_in)
    return TaskOutSchema.model_validate(task, from_attributes=True)


async def delete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> ResultSchema:
    result = await TasksDao(session=session).delete(
        TaskSchema(
            id=task_id,
            user_id=user_id,
        )
    )
    if result == 0:
        raise exc
    return ResultSchema()

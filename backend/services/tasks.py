import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.tasks import TasksDao
from core.schemas.common import IdSchema
from core.schemas.result import ResultSchema
from core.schemas.tasks import (
    LittleInfoTaskOutSchema,
    PaginatedTasksOutSchema,
    StatisticSchema,
    TaskCreateSchema,
    TaskInSchema,
    TaskOutSchema,
    TaskSchema,
    TasksStatisticSchema,
    TasksWithUserSchema,
    TaskUpdateSchema,
    TaskWithUserSchema,
)

exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Действующая задача не найдена",
)


async def create_task(
    session: AsyncSession,
    user_id: int,
    task_in: TaskInSchema,
) -> TaskOutSchema:

    now = datetime.datetime.now(datetime.UTC)
    if now >= task_in.deadline_datetime:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Входящие дата и время меньше, чем текущее",
        )

    task = await TasksDao(session=session).add(
        TaskCreateSchema(
            **task_in.model_dump(),
            user_id=user_id,
        )
    )
    return TaskOutSchema.model_validate(task, from_attributes=True)


async def get_active_user_tasks(
    session: AsyncSession,
    user_id: int,
    page: int,
    per_page: int,
):
    tasks, total_count = await TasksDao(session=session).get_active_user_tasks(
        user_id=user_id, page=page, per_page=per_page
    )
    return PaginatedTasksOutSchema(
        items=[
            LittleInfoTaskOutSchema.model_validate(task, from_attributes=True)
            for task in tasks
        ],
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


async def get_all_active_tasks_by_hour(
    session: AsyncSession,
):
    tasks = await TasksDao(session=session).get_active_tasks_by_hour()
    return TasksWithUserSchema(
        items=[
            TaskWithUserSchema.model_validate(task, from_attributes=True)
            for task in tasks
        ]
    )


async def get_task_by_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> TaskOutSchema:
    task = await TasksDao(session=session).find_one_or_none(
        TaskSchema(
            id=task_id,
            user_id=user_id,
        )
    )
    if not task:
        raise exc
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
        raise exc
    await dao.update(filters=IdSchema(id=task_id), values=updated_task_in)
    return TaskOutSchema.model_validate(task, from_attributes=True)


async def delete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
):
    result = await TasksDao(session=session).delete(
        TaskSchema(
            id=task_id,
            user_id=user_id,
            date_of_completion=None,
        )
    )
    if result == 0:
        raise exc


async def get_tasks_statistics(
    session: AsyncSession,
    user_id: int,
) -> TasksStatisticSchema:
    stats = await TasksDao(session=session).get_statistics(user_id=user_id)
    return TasksStatisticSchema(
        items=[
            StatisticSchema.model_validate(stat, from_attributes=True) for stat in stats
        ]
    )

import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.tasks import TasksDao
from core.schemas import tasks as tasks_schemas
from core.schemas.common import DateOfCompletionSchema, IdSchema

exc = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Действующая задача не найдена",
)


async def create_task(
    session: AsyncSession,
    user_id: int,
    task_in: tasks_schemas.TaskInSchema,
) -> tasks_schemas.TaskOutSchema:

    now = datetime.datetime.now(datetime.UTC)
    if task_in.deadline_datetime.tzinfo is None:
        deadline_utc = task_in.deadline_datetime.replace(
            tzinfo=datetime.UTC
        )
    else:
        deadline_utc = task_in.deadline_datetime.astimezone(
            datetime.UTC
        )
    if now >= deadline_utc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Входящие дата и время меньше, чем текущее",
        )
    task_in.deadline_datetime = deadline_utc
    task = await TasksDao(session=session).add(
        tasks_schemas.TaskCreateSchema(
            **task_in.model_dump(),
            user_id=user_id,
        )
    )
    return tasks_schemas.TaskOutSchema.model_validate(
        task, from_attributes=True
    )


async def get_active_user_tasks(
    session: AsyncSession,
    user_id: int,
    page: int,
    per_page: int,
) -> tasks_schemas.PaginatedTasksOutSchema:
    tasks, total_count = await TasksDao(
        session=session
    ).get_active_user_tasks(
        user_id=user_id, page=page, per_page=per_page
    )
    return tasks_schemas.PaginatedTasksOutSchema(
        items=[
            tasks_schemas.LittleInfoTaskOutSchema.model_validate(
                task, from_attributes=True
            )
            for task in tasks
        ],
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


async def get_all_active_tasks_by_hour(
    session: AsyncSession,
) -> tasks_schemas.TasksWithUserSchema:
    tasks = await TasksDao(
        session=session
    ).get_active_tasks_by_hour()
    return tasks_schemas.TasksWithUserSchema(
        items=[
            tasks_schemas.TaskWithUserSchema.model_validate(
                task, from_attributes=True
            )
            for task in tasks
        ]
    )


async def get_task_by_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> tasks_schemas.TaskOutSchema:
    task = await TasksDao(session=session).find_one_or_none(
        DateOfCompletionSchema(
            id=task_id,
            user_id=user_id,
        )
    )
    if not task:
        raise exc
    return tasks_schemas.TaskOutSchema.model_validate(
        task, from_attributes=True
    )


async def update_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    updated_task_in: tasks_schemas.TaskUpdateSchema,
) -> tasks_schemas.TaskOutSchema:
    dao = TasksDao(session=session)
    task = await dao.find_one_or_none(
        DateOfCompletionSchema(
            id=task_id,
            user_id=user_id,
        )
    )

    if not task:
        raise exc
    await dao.update(
        filters=IdSchema(id=task_id), values=updated_task_in
    )
    return tasks_schemas.TaskOutSchema.model_validate(
        task, from_attributes=True
    )


async def get_tasks_statistics(
    session: AsyncSession,
    user_id: int,
) -> tasks_schemas.TasksStatisticSchema:
    stats = await TasksDao(session=session).get_statistics(
        user_id=user_id
    )
    return tasks_schemas.TasksStatisticSchema(
        items=[
            tasks_schemas.StatisticSchema.model_validate(
                stat, from_attributes=True
            )
            for stat in stats
        ]
    )

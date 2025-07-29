import logging

from fastapi import APIRouter

from core.dao.tasks import TasksDao
from core.dependencies.auth import UserId
from core.dependencies.db import SessionWithCommit, SessionWithoutCommit
from core.schemas.result import ResultSchema
from core.schemas.tasks import (
    TaskInSchema,
    TaskOutSchema,
    TaskUpdateSchema,
    TasksOutSchema,
)
from services import tasks
from fastapi import status

log = logging.getLogger(__name__)


router = APIRouter(tags=["Задачи"])


@router.post(
    "",
    response_model=TaskOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_in: TaskInSchema,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await tasks.create_task(
        session=session,
        task_in=task_in,
        user_id=user_id,
    )


@router.get("")
async def get_active_tasks(
    user_id: UserId,
    session: SessionWithoutCommit,
):
    tasks = await TasksDao(session=session).get_active_tasks(user_id=user_id)
    return TasksOutSchema(
        items=[
            TaskOutSchema.model_validate(task, from_attributes=True) for task in tasks
        ]
    )


@router.put("/{task_id}", response_model=TaskOutSchema)
async def update_task(
    updated_task_in: TaskUpdateSchema,
    task_id: int,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await tasks.update_task(
        session=session,
        user_id=user_id,
        task_id=task_id,
        updated_task_in=updated_task_in,
    )


@router.delete("/{task_id}", response_model=ResultSchema)
async def delete_task(
    task_id: int,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await tasks.delete_task(
        session=session,
        user_id=user_id,
        task_id=task_id,
    )

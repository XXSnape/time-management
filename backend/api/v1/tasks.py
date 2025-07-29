import logging
from typing import Annotated

from fastapi import APIRouter, Query, status

from core.dao.tasks import TasksDao
from core.dependencies.auth import UserId
from core.dependencies.db import SessionWithCommit, SessionWithoutCommit
from core.schemas.result import ResultSchema
from core.schemas.tasks import (
    TaskInSchema,
    TaskOutSchema,
    TasksOutSchema,
    TaskUpdateSchema,
)
from services import tasks

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
async def get_active_user_tasks(
    user_id: UserId,
    session: SessionWithoutCommit,
):
    return await tasks.get_active_user_tasks(
        session=session,
        user_id=user_id,
    )


@router.get("/schedule")
async def get_all_tasks_by_hour(
    session: SessionWithoutCommit,
    hour: Annotated[int | None, Query(ge=0, le=23)],
):
    return await tasks.get_all_active_tasks_by_hour(
        session=session,
        hour=hour,
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

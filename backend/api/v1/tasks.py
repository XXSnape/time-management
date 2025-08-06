import logging
from typing import Annotated

from fastapi import APIRouter, Query, status

from core.dao.tasks import TasksDao
from core.dependencies.auth import UserId, IsAdmin
from core.dependencies.db import (
    SessionWithCommit,
    SessionWithoutCommit,
)

from core.schemas.common import (
    PaginationSchema,
    UpdateDateOfCompletionSchema,
)
from core.schemas import tasks as tasks_schemas
from services import tasks
from services.common import delete_entity, mark_completed

log = logging.getLogger(__name__)


router = APIRouter(tags=["Задачи"])


@router.post(
    "",
    response_model=tasks_schemas.TaskOutSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Дата и время выполнения задачи не могут "
            "быть меньше текущего времени"
        }
    },
)
async def create_task(
    task_in: tasks_schemas.TaskInSchema,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await tasks.create_task(
        session=session,
        task_in=task_in,
        user_id=user_id,
    )


@router.get(
    "",
    response_model=tasks_schemas.PaginatedTasksOutSchema,
)
async def get_active_user_tasks(
    user_id: UserId,
    session: SessionWithoutCommit,
    page: Annotated[
        int,
        Query(
            ge=1,
            le=1_000_000,
            description="Страница для пагинации (начиная с 1)",
        ),
    ] = 1,
    per_page: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество записей на странице (макс. 100)",
        ),
    ] = 10,
):
    return await tasks.get_active_user_tasks(
        session=session,
        user_id=user_id,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/schedules",
    response_model=tasks_schemas.TasksWithUserSchema,
    dependencies=[IsAdmin],
    responses={403: {"description": "Только для администраторов"}},
)
async def get_all_tasks_by_hour(
    session: SessionWithoutCommit,
):
    return await tasks.get_all_active_tasks_by_hour(
        session=session,
    )


@router.get(
    "/statistics",
    response_model=tasks_schemas.TasksStatisticSchema,
)
async def get_statistics(
    session: SessionWithoutCommit, user_id: UserId
):
    return await tasks.get_tasks_statistics(
        session=session,
        user_id=user_id,
    )


@router.get(
    "/{task_id}",
    response_model=tasks_schemas.TaskOutSchema,
    responses={404: {"description": "Задача не найдена"}},
)
async def get_task_by_id(
    task_id: int,
    user_id: UserId,
    session: SessionWithoutCommit,
):
    return await tasks.get_task_by_id(
        session=session,
        user_id=user_id,
        task_id=task_id,
    )


@router.patch(
    "/{task_id}/completion",
    response_model=PaginationSchema,
    responses={
        404: {"description": "Задача не найдена или уже завершена"}
    },
)
async def mark_task_completed(
    updated_date_of_completion: UpdateDateOfCompletionSchema,
    task_id: int,
    user_id: UserId,
    session: SessionWithCommit,
    per_page: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество записей на странице (макс. 100)",
        ),
    ] = 10,
):
    return await mark_completed(
        session=session,
        user_id=user_id,
        entity_id=task_id,
        dao=TasksDao,
        exc=tasks.exc,
        per_page=per_page,
        updated_date_of_completion=updated_date_of_completion,
    )


@router.patch(
    "/{task_id}",
    response_model=tasks_schemas.TaskOutSchema,
    responses={
        404: {"description": "Задача не найдена"},
        409: {
            "description": "Дата и время выполнения задачи не могут быть меньше текущего времени"
        },
    },
)
async def update_task(
    updated_task_in: tasks_schemas.TaskUpdateSchema,
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


@router.delete(
    "/{task_id}",
    response_model=PaginationSchema,
    responses={404: {"description": "Задача не найдена"}},
)
async def delete_task(
    task_id: int,
    user_id: UserId,
    session: SessionWithCommit,
    per_page: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Количество записей на странице (макс. 100)",
        ),
    ] = 10,
):
    return await delete_entity(
        session=session,
        user_id=user_id,
        entity_id=task_id,
        dao=TasksDao,
        exc=tasks.exc,
        per_page=per_page,
    )

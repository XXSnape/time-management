import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Request, Form, HTTPException

from core.dao.tasks import TasksDao
from core.dependencies.auth import UserDep
from core.dependencies.db import (
    SessionWithoutCommit,
    SessionWithCommit,
)
from core.schemas.common import UpdateDateOfCompletionSchema
from core.schemas.tasks import TaskInSchema, TaskUpdateSchema
from core.utils.dt import convert_utc_to_moscow, validate_dt
from core.utils.templates import templates
from services.common import mark_completed
from services.tasks import (
    get_active_user_tasks,
    create_task,
    get_task_by_id,
    update_task,
    exc,
)

router = APIRouter()


@router.get("/tasks")
async def get_tasks(
    request: Request,
    user: UserDep,
    session: SessionWithoutCommit,
    page: int = 1,
    per_page: int = 10,
):
    tasks = await get_active_user_tasks(
        session=session,
        user_id=user.id,
        page=page,
        per_page=per_page,
    )
    for task in tasks.items:
        task.deadline_datetime = convert_utc_to_moscow(
            task.deadline_datetime
        )

    return templates.TemplateResponse(
        "tasks-list.html",
        {
            "request": request,
            "username": user.username,
            **tasks.model_dump(),
        },
    )


@router.get("/tasks/create")
async def create_task_get(request: Request, user: UserDep):
    return templates.TemplateResponse(
        "tasks-create.html",
        {
            "request": request,
            "username": user.username,
        },
    )


@router.post("/tasks/create")
async def create_task_post(
    request: Request,
    user: UserDep,
    task_in: Annotated[TaskInSchema, Form()],
    session: SessionWithCommit,
):
    task_in.deadline_datetime -= timedelta(hours=3)
    try:
        await create_task(
            user_id=user.id, task_in=task_in, session=session
        )
    except HTTPException:
        return templates.TemplateResponse(
            "tasks-create.html",
            {
                "request": request,
                "username": user.username,
            },
        )


@router.get("/tasks/{task_id}/edit")
async def edit_task_get(
    request: Request,
    user: UserDep,
    task_id: int,
    session: SessionWithoutCommit,
):
    task = await get_task_by_id(
        session=session, user_id=user.id, task_id=task_id
    )
    result = task.model_dump()
    d = convert_utc_to_moscow(result["deadline_datetime"])
    result["deadline_datetime"] = str(
        convert_utc_to_moscow(result["deadline_datetime"])
    )
    return templates.TemplateResponse(
        "tasks-edit.html",
        {
            "request": request,
            "username": user.username,
            **result,
        },
    )


@router.post("/tasks/{task_id}/edit")
async def edit_task_post(
    request: Request,
    user: UserDep,
    task_id: int,
    session: SessionWithCommit,
    updated_task_in: Annotated[TaskUpdateSchema, Form()],
):
    updated_task_in.deadline_datetime -= timedelta(hours=3)
    try:
        await update_task(
            session=session,
            user_id=user.id,
            task_id=task_id,
            updated_task_in=updated_task_in,
        )
    except HTTPException:
        pass

    task = await get_task_by_id(
        session=session, user_id=user.id, task_id=task_id
    )
    result = task.model_dump()
    result["deadline_datetime"] = str(
        convert_utc_to_moscow(result["deadline_datetime"])
    )
    return templates.TemplateResponse(
        "tasks-edit.html",
        {
            "request": request,
            "username": user.username,
            **result,
        },
    )


@router.get("/tasks/{task_id}/completion")
async def mark_task(
    request: Request,
    user: UserDep,
    task_id: int,
    session: SessionWithCommit,
):
    updated_date_of_completion = UpdateDateOfCompletionSchema(
        date_of_completion=datetime.datetime.now(datetime.UTC).date()
    )
    await mark_completed(
        session=session,
        user_id=user.id,
        entity_id=task_id,
        dao=TasksDao,
        exc=exc,
        per_page=10,
        updated_date_of_completion=updated_date_of_completion,
    )
    tasks = await get_active_user_tasks(
        session=session,
        user_id=user.id,
        page=1,
        per_page=10,
    )
    for task in tasks.items:
        task.deadline_datetime = convert_utc_to_moscow(
            task.deadline_datetime
        )

    return templates.TemplateResponse(
        "tasks-list.html",
        {
            "request": request,
            "username": user.username,
            **tasks.model_dump(),
        },
    )

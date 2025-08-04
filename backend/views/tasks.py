from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Request, Form, HTTPException

from core.dependencies.auth import UserDep
from core.dependencies.db import (
    SessionWithoutCommit,
    SessionWithCommit,
)
from core.schemas.tasks import TaskInSchema
from core.utils.dt import convert_utc_to_moscow
from core.utils.templates import templates
from services.tasks import get_active_user_tasks, create_task

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

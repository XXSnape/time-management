import datetime
from contextlib import suppress
from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException,
    Query,
    status,
)
from starlette.responses import RedirectResponse

from core.dao.tasks import TasksDao
from core.dependencies.auth import UserDep
from core.dependencies.db import (
    SessionWithoutCommit,
    SessionWithCommit,
)
from core.dependencies.language import Translations
from core.schemas.common import UpdateDateOfCompletionSchema
from core.schemas.tasks import TaskInSchema, TaskUpdateSchema
from core.utils.dt import convert_utc_to_moscow, validate_dt
from core.utils.templates import templates
from services.common import mark_completed, delete_entity
from services.tasks import (
    get_active_user_tasks,
    create_task,
    get_task_by_id,
    update_task,
    exc,
    get_tasks_statistics,
)

router = APIRouter()


@router.get("/tasks", name="tasks:view")
async def get_tasks(
    request: Request,
    user: UserDep,
    session: SessionWithoutCommit,
    translations: Translations,
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
            **translations,
        },
    )


@router.get("/tasks/create", name="tasks:create")
async def create_task_get(
    request: Request,
    user: UserDep,
    translations: Translations,
):
    return templates.TemplateResponse(
        "tasks-create.html",
        {
            "request": request,
            "username": user.username,
            **translations,
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
        task = await create_task(
            user_id=user.id, task_in=task_in, session=session
        )
    except HTTPException:
        return RedirectResponse(
            request.url_for("tasks:create"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        request.url_for("tasks:edit", task_id=task.id)
    )


@router.get("/tasks/{task_id}/edit", name="tasks:edit")
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
    with suppress(HTTPException):
        await update_task(
            session=session,
            user_id=user.id,
            task_id=task_id,
            updated_task_in=updated_task_in,
        )
    return RedirectResponse(
        request.url_for("tasks:edit", task_id=task_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/tasks/{task_id}/completion", name="tasks:mark")
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
    return RedirectResponse(request.url_for("tasks:view"))


@router.post("/tasks/{task_id}/delete")
async def delete_task(
    request: Request,
    user: UserDep,
    task_id: int,
    session: SessionWithCommit,
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
    redirect_url = request.url_for(
        "tasks:view"
    ).include_query_params(
        page=page,
        per_page=per_page,
    )
    await delete_entity(
        session=session,
        user_id=user.id,
        entity_id=task_id,
        dao=TasksDao,
        exc=exc,
        per_page=10,
    )
    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/tasks/stats", name="tasks:stats")
async def get_stats(
    request: Request,
    user: UserDep,
    session: SessionWithoutCommit,
):
    stats = await get_tasks_statistics(
        session=session, user_id=user.id
    )
    return templates.TemplateResponse(
        "tasks-stats.html",
        {
            "request": request,
            "username": user.username,
            **stats.model_dump(),
        },
    )

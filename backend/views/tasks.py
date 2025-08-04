from fastapi import APIRouter, Request

from core.dependencies.auth import UserDep
from core.dependencies.db import SessionWithoutCommit
from core.utils.dt import convert_utc_to_moscow
from core.utils.templates import templates
from services.tasks import get_active_user_tasks

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

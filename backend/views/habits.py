import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Request,
    Form,
    status,
)
from starlette.responses import RedirectResponse

from api.v1.habits import get_active_user_habits, get_habit_by_id
from core.dao.habits import HabitsDAO
from core.dependencies.auth import UserDep
from core.dependencies.db import (
    SessionWithoutCommit,
    SessionWithCommit,
)
from core.dependencies.language import Translations, Language
from core.schemas.common import UpdateDateOfCompletionSchema
from core.schemas.habits import HabitInSchema, HabitUpdateSchema
from core.utils.enums import Weekday
from core.utils.templates import templates
from services.common import mark_completed, delete_entity
from services.habits import (
    create_habit,
    update_habit,
    exc,
    get_habit_statistics,
)

router = APIRouter()


@router.get("/habits", name="habits:view")
async def get_habits(
    request: Request,
    user: UserDep,
    session: SessionWithoutCommit,
    translations: Translations,
    page: int = 1,
    per_page: int = 10,
):
    habits = await get_active_user_habits(
        session=session,
        user_id=user.id,
        page=page,
        per_page=per_page,
    )
    return templates.TemplateResponse(
        "habits-list.html",
        {
            "request": request,
            "username": user.username,
            **habits.model_dump(),
            **translations,
        },
    )


@router.get("/habits/create", name="habits:create")
async def create_habit_get(
    request: Request,
    user: UserDep,
    language: Language,
    translations: Translations,
):
    if language == "ru":
        days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
    else:
        days = [day.title() for day in Weekday]

    return templates.TemplateResponse(
        "habits-create.html",
        {
            "request": request,
            "username": user.username,
            "days": [
                (day, value) for day, value in zip(days, Weekday)
            ],
            **translations,
        },
    )


@router.post("/habits/create")
async def create_habit_post(
    request: Request,
    user: UserDep,
    habit_in: Annotated[HabitInSchema, Form()],
    session: SessionWithCommit,
):
    await create_habit(
        habit_in=habit_in, user_id=user.id, session=session
    )
    return RedirectResponse(
        request.url_for("habits:view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/habits/{habit_id}/edit", name="habits:edit")
async def edit_habit_get(
    request: Request,
    user: UserDep,
    habit_id: int,
    session: SessionWithoutCommit,
    language: Language,
    translations: Translations,
):
    habit = await get_habit_by_id(
        habit_id=habit_id, user_id=user.id, session=session
    )
    result = habit.model_dump()
    if language == "ru":
        days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
    else:
        days = [day.title() for day in Weekday]

    return templates.TemplateResponse(
        "habits-edit.html",
        {
            "request": request,
            "username": user.username,
            **result,
            "all_days": [
                (day, value) for day, value in zip(days, Weekday)
            ],
            **translations,
        },
    )


@router.post("/habits/{habit_id}/edit")
async def edit_habit_post(
    request: Request,
    user: UserDep,
    habit_id: int,
    session: SessionWithCommit,
    updated_habit_in: Annotated[HabitUpdateSchema, Form()],
):
    await update_habit(
        session=session,
        habit_id=habit_id,
        user_id=user.id,
        updated_habit_in=updated_habit_in,
    )
    return RedirectResponse(
        request.url_for("habits:edit", habit_id=habit_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/habits/{habit_id}/completion", name="habits:mark")
async def mark_habit(
    request: Request,
    user: UserDep,
    habit_id: int,
    session: SessionWithCommit,
):
    updated_date_of_completion = UpdateDateOfCompletionSchema(
        date_of_completion=datetime.datetime.now(datetime.UTC).date()
    )
    await mark_completed(
        session=session,
        user_id=user.id,
        entity_id=habit_id,
        dao=HabitsDAO,
        exc=exc,
        per_page=10,
        updated_date_of_completion=updated_date_of_completion,
    )
    return RedirectResponse(request.url_for("habits:view"))


@router.post("/habits/{habit_id}/delete")
async def delete_habit(
    request: Request,
    user: UserDep,
    habit_id: int,
    session: SessionWithCommit,
    page: int = 1,
    per_page: int = 10,
):
    redirect_url = request.url_for(
        "habits:view"
    ).include_query_params(
        page=page,
        per_page=per_page,
    )
    await delete_entity(
        session=session,
        user_id=user.id,
        entity_id=habit_id,
        dao=HabitsDAO,
        exc=exc,
        per_page=10,
    )
    return RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/habits/stats", name="habits:stats")
async def get_stats(
    request: Request,
    user: UserDep,
    session: SessionWithoutCommit,
):
    stats = await get_habit_statistics(
        session=session, user_id=user.id
    )
    return templates.TemplateResponse(
        "habits-stats.html",
        {
            "request": request,
            "username": user.username,
            **stats.model_dump(),
        },
    )

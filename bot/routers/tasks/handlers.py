import datetime
from datetime import date
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select
from httpx import AsyncClient, codes

from backend.core.schemas.users import UserTelegramIdSchema
from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.utils.dt import get_moscow_tz_and_dt
from core.utils.request import make_request
from database.dao.users import UsersDAO
from routers.tasks.states import CreateTaskStates, ViewTaskStates
from aiogram.utils.i18n import gettext as _


async def start_create_task(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        CreateTaskStates.name,
        mode=StartMode.RESET_STACK,
    )


async def start_view_tasks(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        ViewTaskStates.view_all,
        mode=StartMode.RESET_STACK,
    )


async def on_date_selected(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    selected_date: date,
):
    __, dt = get_moscow_tz_and_dt()
    if (
        selected_date < dt.date()
        or selected_date == dt.date()
        and dt.hour == 23
    ):
        await callback.answer(
            _(
                "Дата должна быть позже или равна сегодняшней по Москве"
            )
        )
        return
    manager.dialog_data.update(date=str(selected_date))
    await manager.next()


async def save_hour(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data.update(hour=int(item_id))
    await dialog_manager.next()


async def save_task(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    client: AsyncClient = dialog_manager.middleware_data["client"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(telegram_id=callback.from_user.id)
    )

    moscow_date = datetime.datetime.strptime(
        dialog_manager.dialog_data["date"],
        "%Y-%m-%d",
    ).date()

    moscow_dt = datetime.datetime(
        year=moscow_date.year,
        month=moscow_date.month,
        day=moscow_date.day,
        hour=dialog_manager.dialog_data["hour"],
    )
    moscow_tz = ZoneInfo("Europe/Moscow")
    moscow_dt_aware = moscow_dt.replace(tzinfo=moscow_tz)

    utc_dt = moscow_dt_aware.astimezone(datetime.timezone.utc)
    try:
        await make_request(
            client=client,
            endpoint="tasks",
            method=Methods.post,
            access_token=user.access_token,
            json={
                "name": dialog_manager.dialog_data["name"],
                "deadline_datetime": str(utc_dt),
                "description": dialog_manager.dialog_data[
                    "description"
                ],
                "hour_before_reminder": int(item_id),
            },
        )
    except ServerIsUnavailableExc as e:
        if (
            not e.response
        ) or e.response.status_code != codes.CONFLICT:
            raise
        json = e.response.json()
        await callback.answer(
            _("Не удалось создать задачу: {detail}").format(
                detail=json["detail"]
            ),
            show_alert=True,
        )
        return

    await callback.answer(
        _("Задача успешно создана!"), show_alert=True
    )
    await dialog_manager.done()

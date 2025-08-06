import datetime
from datetime import date

from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select
from httpx import AsyncClient, codes

from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import (
    convert_moscow_dt_to_utc,
    selected_date_validator,
)
from core.utils.request import make_request
from database.dao.users import UsersDAO
from routers.tasks.states import (
    CreateTaskStates,
    TasksManagementStates,
)


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
        TasksManagementStates.view_all,
        mode=StartMode.RESET_STACK,
    )


async def on_date_selected(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    selected_date: date,
):
    res = await selected_date_validator(
        callback=callback, selected_date=selected_date
    )
    if not res:
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


async def catching_deadline_error(
    callback: CallbackQuery, e: ServerIsUnavailableExc, create: bool
):
    if (not e.response) or e.response.status_code != codes.CONFLICT:
        raise
    json = e.response.json()
    if create:
        text = _("❌Не удалось создать задачу: {detail}").format(
            detail=json["detail"]
        )
    else:
        text = _("❌Не удалось обновить дедлайн: {detail}").format(
            detail=json["detail"]
        )
    await callback.answer(
        text,
        show_alert=True,
    )


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

    utc_dt = convert_moscow_dt_to_utc(moscow_dt=moscow_dt)
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
        await catching_deadline_error(
            callback=callback, e=e, create=True
        )
        return

    await callback.answer(
        _("✅Задача успешно создана!"), show_alert=True
    )
    await dialog_manager.done()

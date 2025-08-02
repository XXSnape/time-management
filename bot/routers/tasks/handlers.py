import datetime
from datetime import date

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from httpx import AsyncClient, codes

from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import (
    get_pretty_dt,
    selected_date_validator,
    parse_utc_string_to_dt,
    convert_utc_to_moscow,
    convert_moscow_dt_to_utc,
)
from core.utils.request import make_request
from core.utils.server import check_items_count
from database.dao.users import UsersDAO

# from routers.common.handlers import get_index_from_cache
from routers.tasks.getters import get_texts_by_tasks
from routers.tasks.states import (
    CreateTaskStates,
    TasksManagementStates,
)
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
        text = _("Не удалось создать задачу: {detail}").format(
            detail=json["detail"]
        )
    else:
        text = _("Не удалось обновить дедлайн: {detail}").format(
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
        _("Задача успешно создана!"), show_alert=True
    )
    await dialog_manager.done()


def generate_task_info(
    dialog_manager: DialogManager,
    item: dict,
    item_id: str | int,
):
    completed = "✅" if item["date_of_completion"] else "❌"
    text = _(
        "Название: {name}\n\n"
        "Описание: {description}\n\n"
        "Количество часов до напоминания о дедлайне: {hours}\n\n"
        "Дата дедлайна: {deadline}\n\n"
        "Успешно завершена - {completed}"
    ).format(
        name=item["name"],
        description=item["description"],
        hours=item["hour_before_reminder"],
        deadline=get_pretty_dt(item["deadline_datetime"]),
        completed=completed,
    )
    dialog_manager.dialog_data.update(
        {
            f"item_{item_id}_data": {
                "text": text,
                "deadline_utc": item["deadline_datetime"],
            },
            "current_item": int(item_id),
        }
    )


async def change_item_and_go_next(
    dialog_manager: DialogManager, item: str, value: str | int
):
    from routers.common.handlers import get_index_from_cache

    client: AsyncClient = dialog_manager.middleware_data["client"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(
            telegram_id=dialog_manager.event.from_user.id
        )
    )
    task_id = dialog_manager.dialog_data["current_task"]
    task = await make_request(
        client=client,
        endpoint=f"tasks/{task_id}",
        method=Methods.patch,
        json={item: value},
        access_token=user.access_token,
    )
    texts = get_texts_by_tasks(tasks=[task])
    index_to_replace = get_index_from_cache(
        texts=dialog_manager.dialog_data["tasks"], id=task_id
    )
    dialog_manager.dialog_data["tasks"][index_to_replace] = texts[0]
    generate_task_info(
        dialog_manager=dialog_manager, item=task, item_id=task_id
    )
    await dialog_manager.switch_to(
        TasksManagementStates.view_details
    )


async def change_notification_hour(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    await change_item_and_go_next(
        dialog_manager=dialog_manager,
        item="hour_before_reminder",
        value=int(item_id),
    )


async def change_deadline(
    manager: DialogManager, callback: CallbackQuery, **kwargs: int
):
    task_id = manager.dialog_data["current_task"]
    deadline_utc = manager.dialog_data[f"task_{task_id}_data"][
        "deadline_utc"
    ]
    utc_dt = parse_utc_string_to_dt(deadline_utc)
    moscow_dt = convert_utc_to_moscow(utc_dt)
    moscow_dt = moscow_dt.replace(**kwargs)
    new_utc_dt = convert_moscow_dt_to_utc(moscow_dt=moscow_dt)
    try:
        await change_item_and_go_next(
            dialog_manager=manager,
            item="deadline_datetime",
            value=str(new_utc_dt),
        )
    except ServerIsUnavailableExc as e:
        await catching_deadline_error(
            callback=callback, e=e, create=False
        )


async def change_deadline_date(
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
    await change_deadline(
        manager=manager,
        callback=callback,
        year=selected_date.year,
        month=selected_date.month,
        day=selected_date.day,
    )


async def change_deadline_time(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    await change_deadline(
        manager=dialog_manager, callback=callback, hour=int(item_id)
    )


def change_item_by_text(item: str):
    async def _wrapper(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str,
    ):
        await change_item_and_go_next(
            dialog_manager=dialog_manager, item=item, value=text
        )

    return _wrapper

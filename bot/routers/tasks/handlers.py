import datetime
from datetime import date
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from httpx import AsyncClient, codes

from backend.core.schemas.users import UserTelegramIdSchema
from backend.core.utils.dt import get_pretty_dt
from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import get_moscow_tz_and_dt
from core.utils.request import make_request
from database.dao.users import UsersDAO
from routers.tasks.getters import get_texts_by_tasks
from routers.tasks.states import CreateTaskStates, ViewTaskStates
from aiogram.utils.i18n import gettext as _


def get_index_from_cache(texts: list, id: int):
    to_delete_index = None
    for index, (__, id_) in enumerate(texts):
        if id_ == id:
            to_delete_index = index
            break
    return to_delete_index


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


async def upload_more_tasks(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    client: AsyncClient = dialog_manager.middleware_data["client"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(
            telegram_id=dialog_manager.event.from_user.id
        )
    )
    result = await make_request(
        client=client,
        endpoint="tasks",
        method=Methods.get,
        access_token=user.access_token,
        params={"page": dialog_manager.dialog_data["next_page"]},
    )
    count = result["total_count"] - len(
        dialog_manager.dialog_data["tasks"]
    )
    new_texts = get_texts_by_tasks(result["items"][-count:])
    dialog_manager.dialog_data.update(
        last_loaded_page=dialog_manager.dialog_data["next_page"] + 1,
        tasks=dialog_manager.dialog_data["tasks"] + new_texts,
    )


def generate_task_info(
    dialog_manager: DialogManager,
    task: dict,
    item_id: str | int,
):
    completed = "✅" if task["date_of_completion"] else "❌"
    text = _(
        "Название: {name}\n\n"
        "Описание: {description}\n\n"
        "Количество часов до напоминания о дедлайне: {hours}\n\n"
        "Дата дедлайна: {deadline}\n\n"
        "Успешно завершена - {completed}"
    ).format(
        name=task["name"],
        description=task["description"],
        hours=task["hour_before_reminder"],
        deadline=get_pretty_dt(task["deadline_datetime"]),
        completed=completed,
    )
    dialog_manager.dialog_data.update(
        {f"task_{item_id}_text": text, "current_task": int(item_id)}
    )


async def on_click_task(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    item_id: str,
):
    task_text = dialog_manager.dialog_data.get(
        f"task_{item_id}_text"
    )
    if task_text:
        await dialog_manager.next()
        return
    client: AsyncClient = dialog_manager.middleware_data["client"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(
            telegram_id=dialog_manager.event.from_user.id
        )
    )
    task = await make_request(
        client=client,
        endpoint=f"tasks/{item_id}",
        method=Methods.get,
        access_token=user.access_token,
    )
    generate_task_info(
        dialog_manager=dialog_manager, task=task, item_id=item_id
    )
    await dialog_manager.next()


async def delete_task(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
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
    tasks_count = await make_request(
        client=client,
        endpoint=f"tasks/{task_id}",
        method=Methods.delete,
        access_token=user.access_token,
    )
    texts = dialog_manager.dialog_data["tasks"]
    to_delete_index = get_index_from_cache(texts=texts, id=task_id)
    texts.pop(to_delete_index)
    await callback.answer(
        _("Задача успешно удалена!"), show_alert=True
    )
    if (
        tasks_count["pages"]
        < dialog_manager.dialog_data["next_page"]
    ):
        dialog_manager.dialog_data["next_page"] = tasks_count[
            "pages"
        ]
    dialog_manager.dialog_data["total_count"] = tasks_count[
        "total_count"
    ]
    await dialog_manager.switch_to(ViewTaskStates.view_all)


async def change_item_and_go_next(
    dialog_manager: DialogManager, item: str, value: str | int
):
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
        dialog_manager=dialog_manager, task=task, item_id=task_id
    )
    await dialog_manager.switch_to(ViewTaskStates.view_details)


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


async def change_name(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
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
        json={"name": text},
        access_token=user.access_token,
    )
    texts = get_texts_by_tasks(tasks=[task])
    index_to_replace = get_index_from_cache(
        texts=dialog_manager.dialog_data["tasks"], id=task_id
    )
    dialog_manager.dialog_data["tasks"][index_to_replace] = texts[0]
    generate_task_info(
        dialog_manager=dialog_manager, task=task, item_id=task_id
    )
    await dialog_manager.switch_to(ViewTaskStates.view_details)

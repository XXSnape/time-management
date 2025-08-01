import datetime

from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager
from httpx import AsyncClient

from backend.core.utils.dt import get_pretty_dt
from core.enums import Methods
from core.schemas.users import UserTelegramIdSchema
from core.utils.generator import generate_hours
from core.utils.request import make_request
from database.dao.users import UsersDAO


async def task_name(**kwargs):
    return {
        "task_name": _("Введите название задачи"),
        "back": _("Вернуться к выбору"),
    }


async def task_description(**kwargs):
    return {
        "task_description": _("Введите описание задачи"),
        "back": _("Вернуться к названию"),
    }


async def task_date(**kwargs):
    return {
        "calendar": _("Выберите дату дедлайна"),
        "back": _("Изменить описание"),
    }


async def task_hour(dialog_manager: DialogManager, **kwargs):
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    hour = 0
    if (
        datetime.datetime.strptime(
            dialog_manager.dialog_data["date"], "%Y-%m-%d"
        ).date()
        == moscow_dt.date()
    ):
        hour = (moscow_dt.hour + 1) % 24
    return {
        "hours": generate_hours(start_hour=hour, end_hour=24),
        "hour_text": _("Выберете час дедлайна"),
        "back": _("Изменить дату дедлайна"),
    }


async def task_notification_hour(**kwargs):
    return {
        "hours": generate_hours(start_hour=1, end_hour=25),
        "notification_hour_text": _(
            "Выберете, за сколько часов до дедлайна нужно напомнить о задаче"
        ),
        "back": _("Изменить час дедлайна"),
    }


def get_texts_by_tasks(tasks: list[dict]):
    texts = []
    for task in tasks:
        current_text = _("{name} [{deadline}]").format(
            name=task["name"],
            deadline=get_pretty_dt(task["deadline_datetime"]),
        )
        texts.append([current_text, task["id"]])
    return texts


async def get_user_tasks(dialog_manager: DialogManager, **kwargs):
    load_more = _("Загрузить еще")
    tasks_text = _("Нажмите на задачу, чтобы посмотреть подробности")
    tasks_from_cache = dialog_manager.dialog_data.get("tasks")
    if tasks_from_cache is not None:
        scrolling_group = dialog_manager.find("all_tasks")
        pages_count = await scrolling_group.get_page_count(
            dialog_manager.dialog_data
        )
        current_page = await scrolling_group.get_page()
        can_be_loaded = (
            current_page == pages_count - 1
            and dialog_manager.dialog_data["all_pages"]
            != dialog_manager.dialog_data["last_loaded_page"]
        )
        return {
            "tasks_text": tasks_text,
            "tasks": tasks_from_cache,
            "can_be_loaded": can_be_loaded,
            "load_more": load_more,
        }

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
    )
    texts = get_texts_by_tasks(result["items"])
    dialog_manager.dialog_data.update(
        all_pages=result["pages"],
        last_loaded_page=1,
        tasks=texts,
    )
    return {
        "tasks_text": tasks_text,
        "tasks": texts,
        "can_be_loaded": False,
        "load_more": load_more,
    }


async def get_task_details(
    dialog_manager: DialogManager,
    **kwargs,
):
    task_id = dialog_manager.dialog_data["current_task"]
    task_text = dialog_manager.dialog_data[f"task_{task_id}_text"]
    return {
        "task_text": task_text,
        "back": _("Вернуться к задачам"),
    }

from functools import partial
from typing import Literal

from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager
from httpx import AsyncClient

from core.enums import Methods
from core.schemas.users import UserTelegramIdSchema
from core.utils.request import make_request
from database.dao.users import UsersDAO


async def create_task_or_habit(**kwargs):
    return {
        "task_or_habit_text": _(
            "Вы хотите создать задачу или привычку?"
        ),
        "task_text": _("Задача"),
        "habit_text": _("Привычка"),
    }


async def view_tasks_or_habits(**kwargs):
    return {
        "tasks_or_habits_text": _(
            "Вы хотите узнать информацию о действующих задачах или привычках?"
        ),
        "tasks_text": _("Задачи"),
        "habits_text": _("Привычки"),
    }


def get_texts_by_habits(habits: list[dict]):
    texts = []
    for habit in habits:
        current_text = _("{name}").format(
            name=habit["name"],
        )
        texts.append([current_text, habit["id"]])
    return texts


async def get_user_resources(
    dialog_manager: DialogManager,
    resources: Literal["tasks", "habits"],
    **kwargs,
):
    load_more = _("Загрузить еще")
    items_text = _("Нажмите, чтобы посмотреть подробности")
    items_from_cache = dialog_manager.dialog_data.get("items")
    scrolling_group_id = f"all_{resources}"
    if items_from_cache is not None:
        scrolling_group = dialog_manager.find(scrolling_group_id)
        pages_count = await scrolling_group.get_page_count(
            dialog_manager.dialog_data
        )
        current_page = await scrolling_group.get_page()

        can_be_loaded = current_page == pages_count - 1 and len(
            items_from_cache
        ) < dialog_manager.dialog_data.get("total_count")
        return {
            "items_text": items_text,
            "items": items_from_cache,
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
        endpoint=resources,
        method=Methods.get,
        access_token=user.access_token,
    )
    if resources == "tasks":
        pass
        # func = get_texts_by_tasks
    else:
        func = get_texts_by_habits
    texts = func(result["items"])
    dialog_manager.dialog_data.update(
        total_count=result["total_count"],
        next_page=2,
        tasks=texts,
    )
    return {
        "items_text": items_text,
        "items": texts,
        "can_be_loaded": False,
        "load_more": load_more,
    }


get_habits = partial(get_user_resources, resources="habits")

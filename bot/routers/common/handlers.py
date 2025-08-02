from functools import partial

from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from httpx import AsyncClient

from core.enums import Resources, Methods
from core.schemas.users import UserTelegramIdSchema
from core.utils.request import make_request
from core.utils.server import check_items_count
from database.dao.users import UsersDAO
from routers.common.states import CreateTaskHabitStates


async def back_to_selection(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        CreateTaskHabitStates.create_task_or_habit,
        mode=StartMode.RESET_STACK,
    )


def is_short_text(max_length: int):
    def _wrapper(text: str) -> str:
        if len(text) > max_length:
            raise ValueError(max_length)
        return text

    return _wrapper


async def on_incorrect_text(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(
        _(
            "Текст должен быть не длиннее {max_length} символов"
        ).format(max_length=str(error))
    )


def save_text_by_key(key: str):
    async def _wrapper(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str,
    ):
        dialog_manager.dialog_data.update({key: text})
        await dialog_manager.next()

    return _wrapper


async def upload_more_items(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    resources: Resources,
):
    from routers.tasks.getters import get_texts_by_tasks
    from routers.habits.getters import get_texts_by_habits

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
        params={"page": dialog_manager.dialog_data["next_page"]},
    )
    check_items_count(
        dialog_manager=dialog_manager,
        total_count=result["total_count"],
        can_be_equal=False,
    )
    count = result["total_count"] - len(
        dialog_manager.dialog_data["items"]
    )
    if resources == Resources.tasks:
        func = get_texts_by_tasks
    else:
        func = get_texts_by_habits
    new_texts = func(result["items"][-count:])
    dialog_manager.dialog_data.update(
        last_loaded_page=dialog_manager.dialog_data["next_page"] + 1,
        items=dialog_manager.dialog_data["items"] + new_texts,
    )


upload_tasks = partial(upload_more_items, resources=Resources.tasks)
upload_habits = partial(
    upload_more_items, resources=Resources.habits
)


async def on_click_resource(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    item_id: str,
    resource: Resources,
):
    from routers.tasks.handlers import generate_task_info
    from routers.habits.handlers import generate_habit_info

    item_data = dialog_manager.dialog_data.get(
        f"item_{item_id}_data"
    )
    if item_data:
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
    item = await make_request(
        client=client,
        endpoint=f"{resource}/{item_id}",
        method=Methods.get,
        access_token=user.access_token,
    )
    if resource == Resources.tasks:
        func = generate_task_info
    else:
        func = generate_habit_info
    func(dialog_manager=dialog_manager, item=item, item_id=item_id)
    await dialog_manager.next()


on_click_task = partial(on_click_resource, resource=Resources.tasks)
on_click_habit = partial(
    on_click_resource, resource=Resources.habits
)

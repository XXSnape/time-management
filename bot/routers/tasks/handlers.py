import datetime
from datetime import date

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from httpx import AsyncClient

from backend.core.schemas.users import UserTelegramIdSchema
from core.enums import Methods
from core.utils.dt import get_moscow_tz_and_dt
from core.utils.request import make_request
from database.dao.users import UsersDAO
from routers.tasks.states import CreateTaskStates
from aiogram.utils.i18n import gettext as _


async def save_name(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    dialog_manager.dialog_data.update(name=text)
    await dialog_manager.next()


async def save_description(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    dialog_manager.dialog_data.update(description=text)
    await dialog_manager.next()


async def start_create_task(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        CreateTaskStates.name,
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
    session = dialog_manager.middleware_data["session"]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(telegram_id=callback.from_user.id)
    )

    # await make_request(client=client,
    #                    endpoint='tasks',
    #                    method=Methods.post,
    #                    access_token=user.access_token,
    #                    json={})
    # await c
    pass
    # dialog_manager.dialog_data.update(notifucation_hour=int(item_id))

import datetime
from datetime import date

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

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
    current_date = datetime.date.today()
    if selected_date >= current_date:
        manager.dialog_data.update(date=selected_date)
        await manager.next()
        return
    await callback.answer(
        _("Дата должна быть позже или равна сегодняшней по Москве")
    )

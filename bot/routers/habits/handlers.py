from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect
from .states import CreateHabitStates


async def start_create_habit(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        CreateHabitStates.name,
        mode=StartMode.RESET_STACK,
    )


async def save_checkbox(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    checkbox = dialog_manager.find("multi_days").get_checked()
    dialog_manager.dialog_data.update(days=checkbox)
    await dialog_manager.next()

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
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

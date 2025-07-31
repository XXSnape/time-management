from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from routers.common.states import TaskHabitStates


async def back_to_selection(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        TaskHabitStates.create_task_or_habit,
        mode=StartMode.RESET_STACK,
    )

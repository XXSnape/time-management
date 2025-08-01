from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from core.commands import Commands
from routers.common.states import (
    CreateTaskHabitStates,
    ViewTasksHabitsStates,
)

router = Router(name=__name__)


@router.message(Command(Commands.create.name))
async def create_task_or_habit(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=CreateTaskHabitStates.create_task_or_habit,
        mode=StartMode.RESET_STACK,
    )


@router.message(Command(Commands.view.name))
async def view_tasks_or_habits(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=ViewTasksHabitsStates.view_tasks_or_habits,
        mode=StartMode.RESET_STACK,
    )

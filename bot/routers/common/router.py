from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from core.commands import Commands
from core.utils.db import check_user_in_database
from routers.common.states import (
    CreateTaskHabitStates,
    ViewTasksHabitsStates,
)
from routers.stats.states import StatsTasksHabitsStates

router = Router(name=__name__)


@router.message(Command(Commands.create.name))
async def create_task_or_habit(
    message: Message,
    dialog_manager: DialogManager,
    session_without_commit: AsyncSession,
):
    if await check_user_in_database(
        message=message, session=session_without_commit
    ):
        await dialog_manager.start(
            state=CreateTaskHabitStates.create_task_or_habit,
            mode=StartMode.RESET_STACK,
        )


@router.message(Command(Commands.view.name))
async def view_tasks_or_habits(
    message: Message,
    dialog_manager: DialogManager,
    session_without_commit: AsyncSession,
):
    if await check_user_in_database(
        message=message, session=session_without_commit
    ):
        await dialog_manager.start(
            state=ViewTasksHabitsStates.view_tasks_or_habits,
            mode=StartMode.RESET_STACK,
        )


@router.message(Command(Commands.stats.name))
async def stats_tasks_or_habits(
    message: Message,
    dialog_manager: DialogManager,
    session_without_commit: AsyncSession,
):
    if await check_user_in_database(
        message=message, session=session_without_commit
    ):
        await dialog_manager.start(
            state=StatsTasksHabitsStates.stats_tasks_or_habits,
            mode=StartMode.RESET_STACK,
        )

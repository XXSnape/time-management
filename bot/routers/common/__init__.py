from aiogram import Router

from .dialogs import (
    create_task_or_habit_dialog,
    view_tasks_or_habits_dialog,
)
from .router import router as tasks_or_habits_actions

router = Router(name=__name__)

router.include_routers(
    tasks_or_habits_actions,
    create_task_or_habit_dialog,
    view_tasks_or_habits_dialog,
)

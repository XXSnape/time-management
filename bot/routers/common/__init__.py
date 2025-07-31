from aiogram import Router
from .router import router as start_create_task_or_habit_dialog

from .dialogs import create_task_or_habit_dialog


router = Router(name=__name__)

router.include_routers(
    start_create_task_or_habit_dialog,
    create_task_or_habit_dialog,
)

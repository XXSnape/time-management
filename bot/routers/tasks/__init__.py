from aiogram import Router
from .dialogs import create_task_dialog, view_tasks_dialog


router = Router(name=__name__)
router.include_routers(
    create_task_dialog,
    view_tasks_dialog,
)

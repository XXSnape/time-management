from aiogram import Router
from .dialogs import create_task_dialog, tasks_management_dialog


router = Router(name=__name__)
router.include_routers(
    create_task_dialog,
    tasks_management_dialog,
)

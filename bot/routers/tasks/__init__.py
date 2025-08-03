from aiogram import Router
from .dialogs import create_task_dialog, tasks_management_dialog
from .router import router as task_router

router = Router(name=__name__)
router.include_routers(
    task_router,
    create_task_dialog,
    tasks_management_dialog,
)

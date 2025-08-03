from aiogram import Router
from .dialogs import create_habit_dialog, habits_management_dialog
from .router import router as habits_router

router = Router(name=__name__)
router.include_routers(
    habits_router,
    create_habit_dialog,
    habits_management_dialog,
)

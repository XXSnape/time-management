from aiogram import Router
from .dialogs import create_habit_dialog


router = Router(name=__name__)
router.include_routers(
    create_habit_dialog,
)

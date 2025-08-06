from aiogram import Router

from .dialogs import stats_tasks_or_habits_dialog

router = Router(name=__name__)
router.include_routers(stats_tasks_or_habits_dialog)

from aiogram import Router

from .dialogs import change_activity_dialog
from .router import router as activity_router

router = Router(name=__name__)
router.include_routers(
    activity_router,
    change_activity_dialog,
)

from aiogram import Router
from .router import router as activity_router
from .dialogs import change_activity_dialog


router = Router(name=__name__)
router.include_routers(
    activity_router,
    change_activity_dialog,
)

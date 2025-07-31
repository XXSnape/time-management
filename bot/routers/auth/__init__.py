from aiogram import Router
from .router import router as start_dialog_router

from .dialogs import auth_dialog


router = Router(name=__name__)

router.include_routers(
    start_dialog_router,
    auth_dialog,
)

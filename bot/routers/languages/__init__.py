from aiogram import Router

from .dialogs import change_language_dialog
from .router import router as languages_router

router = Router(name=__name__)
router.include_routers(
    languages_router,
    change_language_dialog,
)

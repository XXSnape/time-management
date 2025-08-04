from aiogram import Router
from .router import router as languages_router
from .dialogs import change_language_dialog

router = Router(name=__name__)
router.include_routers(
    languages_router,
    change_language_dialog,
)

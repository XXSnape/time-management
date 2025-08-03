from aiogram import Router
from .cancel import router as cancel_router
from .start import router as start_router
from .auth import router as auth_router
from .common import router as common_router
from .tasks import router as tasks_router
from .habits import router as habits_router

router = Router(name=__name__)
router.include_routers(
    cancel_router,
    start_router,
    auth_router,
    tasks_router,
    habits_router,
    common_router,
)

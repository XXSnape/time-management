from aiogram import Router
from .activity import router as activity_router
from .cancel import router as cancel_router
from .start import router as start_router
from .auth import router as auth_router
from .common import router as common_router
from .tasks import router as tasks_router
from .habits import router as habits_router
from .stats import router as stats_router
from .languages import router as languages_router

router = Router(name=__name__)
router.include_routers(
    cancel_router,
    start_router,
    auth_router,
    tasks_router,
    habits_router,
    common_router,
    stats_router,
    languages_router,
    activity_router,
)

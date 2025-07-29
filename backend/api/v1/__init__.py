from fastapi import APIRouter

from core.config import settings

from .habits import router as habits_router
from .tasks import router as tasks_router
from .users import router as users_router


router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    habits_router,
    prefix=settings.api.v1.habits,
)

router.include_router(
    tasks_router,
    prefix=settings.api.v1.tasks,
)

router.include_router(
    users_router,
    prefix=settings.api.v1.users,
)

from fastapi import APIRouter

from core.config import settings

from .affairs import router as affairs_router
from .users import router as users_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(
    affairs_router,
    prefix=settings.api.v1.affairs,
)
router.include_router(
    users_router,
    prefix=settings.api.v1.users,
)
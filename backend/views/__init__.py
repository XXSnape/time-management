from fastapi import APIRouter

from .auth import router as auth_router
from .habits import router as habits_router
from .index import router as index_router
from .tasks import router as tasks_router

router = APIRouter(include_in_schema=False)
router.include_router(auth_router)
router.include_router(index_router)
router.include_router(tasks_router)
router.include_router(habits_router)

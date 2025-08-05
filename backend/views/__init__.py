from fastapi import APIRouter
from .auth import router as auth_router
from .index import router as index_router
from .tasks import router as tasks_router
from .habits import router as habits_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(index_router)
router.include_router(tasks_router)
router.include_router(habits_router)

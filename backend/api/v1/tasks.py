import logging

from fastapi import APIRouter

from core.dependencies.auth import UserId
from core.dependencies.db import SessionWithCommit
from core.schemas.tasks import TaskInSchema, TaskOutSchema
from services import tasks
from fastapi import status

log = logging.getLogger(__name__)


router = APIRouter(tags=["Задачи"])


@router.post(
    "",
    response_model=TaskOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_in: TaskInSchema,
    user_id: UserId,
    session: SessionWithCommit,
):
    return await tasks.create_task(
        session=session,
        task_in=task_in,
        user_id=user_id,
    )

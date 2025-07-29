from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.tasks import TasksDao
from core.schemas.tasks import TaskCreateSchema, TaskInSchema, TaskOutSchema


async def create_task(
    session: AsyncSession,
    user_id: int,
    task_in: TaskInSchema,
) -> TaskOutSchema:
    task = await TasksDao(session=session).add(
        TaskCreateSchema(
            **task_in.model_dump(),
            user_id=user_id,
        )
    )
    return TaskOutSchema.model_validate(task, from_attributes=True)

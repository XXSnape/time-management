from sqlalchemy import select

from .base import BaseDAO
from core.models import Task
from ..utils.dt import get_moscow_tz_and_dt


class TasksDao(BaseDAO[Task]):
    model = Task

    async def get_active_tasks(self, user_id: int):
        _, moscow_dt = get_moscow_tz_and_dt()
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.full_datetime > moscow_dt,
            self.model.date_of_completion.is_(None),
        )
        result = await self._session.execute(query)
        return result.scalars().all()

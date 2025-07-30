from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseDAO
from core.models import Habit
from ..schemas.common import IdSchema


# from core.schemas.common import IdSchema


class HabitsDAO(BaseDAO[Habit]):
    model = Habit

    async def get_habit_with_all_data(self, id_schema: IdSchema):
        query = (
            select(self.model)
            .options(
                selectinload(self.model.timers),
                selectinload(self.model.schedules),
            )
            .filter_by(**id_schema.model_dump())
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

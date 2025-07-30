from sqlalchemy import func, select
from sqlalchemy.orm import load_only, selectinload

from core.models import Habit, Tracker
from core.schemas.common import IdSchema

from .base import BaseDAO


class HabitsDAO(BaseDAO[Habit]):
    model = Habit

    async def get_habit_with_all_data(self, id_schema: IdSchema):
        query = (
            select(self.model)
            .options(
                selectinload(self.model.timers),
                selectinload(self.model.schedules),
                selectinload(self.model.trackers).load_only(
                    Tracker.is_completed
                ),
            )
            .filter_by(**id_schema.model_dump())
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_active_user_habits(
        self,
        user_id: int,
        page: int,
        per_page: int,
    ):
        filters = (
            self.model.user_id == user_id,
            self.model.date_of_completion.is_(None),
        )
        count_query = select(func.count()).where(*filters)
        count_result = (
            await self._session.execute(count_query)
        ).scalar_one()
        query = (
            select(self.model)
            .options(
                load_only(
                    self.model.id,
                    self.model.name,
                )
            )
            .where(*filters)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(self.model.id)
        )

        result = await self._session.execute(query)
        return result.scalars().all(), count_result

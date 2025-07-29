from collections.abc import Sequence

from sqlalchemy import or_, select, func
from sqlalchemy.orm import joinedload, load_only

from core.models import Task, User
from core.utils.dt import get_moscow_tz_and_dt

from .base import BaseDAO


class TasksDao(BaseDAO[Task]):
    model = Task

    async def get_active_user_tasks(
        self,
        user_id: int,
        page: int,
        per_page: int,
    ) -> tuple[Sequence[Task], int]:
        _, moscow_dt = get_moscow_tz_and_dt()
        filters = (
            self.model.user_id == user_id,
            self.model.full_datetime > moscow_dt,
            self.model.date_of_completion.is_(None),
        )
        count_query = select(func.count()).where(*filters)
        count_result = (await self._session.execute(count_query)).scalar_one()
        query = (
            select(self.model)
            .options(
                load_only(
                    self.model.id,
                    self.model.name,
                    self.model.deadline_date,
                    self.model.deadline_time,
                )
            )
            .where(*filters)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(self.model.id)
        )

        result = await self._session.execute(query)
        return result.scalars().all(), count_result

    async def get_active_tasks_by_hour(
        self,
        hour: int,
    ):
        _, moscow_dt = get_moscow_tz_and_dt()
        query = (
            select(self.model)
            .options(
                load_only(
                    self.model.name,
                    self.model.deadline_date,
                    self.model.deadline_time,
                ),
                joinedload(self.model.user).load_only(
                    User.telegram_id,
                    User.is_active,
                ),
            )
            .where(
                self.model.full_datetime > moscow_dt,
                self.model.date_of_completion.is_(None),
                User.is_active.is_(True),
                or_(
                    self.model.deadline_time == hour,
                    (hour + self.model.hour_before_reminder) % 24
                    == self.model.deadline_time,
                ),
            )
            .order_by(self.model.id)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

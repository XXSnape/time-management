import datetime
from datetime import timedelta
from typing import Sequence

from sqlalchemy import (
    Integer,
    Row,
    and_,
    case,
    cast,
    func,
    literal,
    or_,
    select,
    text,
    union_all,
)
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import joinedload, load_only

from core.models import Task, User

from .base import BaseDAO


class TasksDao(BaseDAO[Task]):
    model = Task

    async def get_active_user_tasks(
        self,
        user_id: int,
        page: int,
        per_page: int,
    ) -> tuple[Sequence[Task], int]:
        now = datetime.datetime.now(datetime.UTC)
        filters = (
            self.model.user_id == user_id,
            self.model.deadline_datetime > now,
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
                    self.model.deadline_datetime,
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
    ):
        current_utc_hour = func.date_trunc(
            "hour", func.timezone("UTC", func.now())
        )

        query = (
            select(self.model)
            .options(
                load_only(
                    self.model.name,
                    self.model.deadline_datetime,
                ),
                joinedload(self.model.user).load_only(
                    User.telegram_id,
                    User.is_active,
                ),
            )
            .where(
                self.model.date_of_completion.is_(None),
                User.is_active.is_(True),
                or_(
                    func.date_trunc("hour", Task.deadline_datetime)
                    == current_utc_hour,
                    func.date_trunc("hour", Task.deadline_datetime)
                    == (
                        current_utc_hour
                        + (
                            Task.hour_before_reminder
                            * cast(
                                text("INTERVAL '1 hour'"), INTERVAL
                            )
                        )
                    ),
                ),
            )
            .order_by(self.model.id)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_statistics(
        self, user_id: int
    ) -> Sequence[Row[tuple[int, int, int, int, str]]]:
        now = datetime.datetime.now(datetime.UTC)
        completed_query = func.count(
            case(
                (
                    self.model.date_of_completion.is_not(None),
                    1,
                ),
                else_=None,
            )
        ).label("completed")
        not_completed_query = func.count(
            case(
                (
                    and_(
                        self.model.date_of_completion.is_(None),
                        self.model.deadline_datetime < now,
                    ),
                    1,
                ),
                else_=None,
            ),
        ).label("not_completed")
        total_query = func.count().label("total")
        performance = case(
            (total_query == 0, 0),
            else_=func.cast(
                completed_query / total_query * 100, Integer
            ),
        ).label("performance")

        queries = []
        for td, period in self.periods:
            query = (
                select(
                    completed_query,
                    not_completed_query,
                    total_query,
                    performance,
                    literal(period).label("period"),
                )
                .select_from(self.model)
                .where(self.model.user_id == user_id)
            )
            if td:
                query = query.where(
                    self.model.deadline_datetime >= now - td
                )
            queries.append(query)
        u = union_all(*queries)

        result = await self._session.execute(u)
        return result.all()

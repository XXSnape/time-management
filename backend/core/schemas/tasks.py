import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from core.schemas.common import (
    BaseStatisticSchema,
    IdSchema,
    PaginatedSchema,
)
from core.schemas.users import UserTelegramIdSchema


class LittleInfoTaskSchema(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    deadline_datetime: datetime.datetime


class TaskInSchema(LittleInfoTaskSchema):
    description: Annotated[str, Field(max_length=300)]
    hour_before_reminder: Annotated[
        int,
        Field(ge=1, le=24),
    ]


class TaskOutSchema(IdSchema, TaskInSchema):
    date_of_completion: datetime.date | None


class LittleInfoTaskOutSchema(
    IdSchema,
    LittleInfoTaskSchema,
):
    pass


class TaskCreateSchema(TaskInSchema):
    user_id: int


class TaskUpdateSchema(TaskInSchema):
    name: Annotated[str | None, Field(max_length=50)] = None
    description: Annotated[str | None, Field(max_length=300)] = None
    hour_before_reminder: Annotated[
        int | None,
        Field(ge=1, le=24),
    ] = None
    deadline_datetime: datetime.datetime | None = None


class TaskWithUserSchema(LittleInfoTaskOutSchema):
    user: UserTelegramIdSchema


class PaginatedTasksOutSchema(
    PaginatedSchema[LittleInfoTaskOutSchema],
):
    pass


class TasksWithUserSchema(BaseModel):
    items: list[TaskWithUserSchema]


class StatisticSchema(BaseStatisticSchema):
    completed: int
    not_completed: int
    performance: int


class TasksStatisticSchema(BaseModel):
    items: list[StatisticSchema]

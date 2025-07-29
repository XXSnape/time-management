import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from core.schemas.common import IdSchema, PaginatedSchema
from core.schemas.users import UserTelegramIdSchema


class LittleInfoTaskSchema(BaseModel):
    name: str
    deadline_date: datetime.date
    deadline_time: Annotated[
        int,
        Field(ge=0, le=23),
    ]


class TaskInSchema(LittleInfoTaskSchema):
    description: str
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


class TaskSchema(IdSchema):
    user_id: int
    date_of_completion: None = None


class TaskUpdateSchema(TaskInSchema):
    name: str | None = None
    description: str | None = None
    deadline_date: datetime.date | None = None
    deadline_time: Annotated[
        int | None,
        Field(ge=0, le=23),
    ] = None
    hour_before_reminder: Annotated[
        int | None,
        Field(ge=1, le=24),
    ] = None
    date_of_completion: datetime.date | None = None


class TaskWithUserSchema(LittleInfoTaskOutSchema):
    user: UserTelegramIdSchema


class PaginatedTasksOutSchema(PaginatedSchema[LittleInfoTaskOutSchema]):
    pass


class TasksWithUserSchema(BaseModel):
    items: list[TaskWithUserSchema]

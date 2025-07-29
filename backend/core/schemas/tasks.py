from typing import Annotated

from pydantic import BaseModel, Field
import datetime

from core.schemas.common import IdSchema


class TaskInSchema(BaseModel):
    name: str
    description: str
    deadline_date: datetime.date
    deadline_time: Annotated[
        int,
        Field(ge=0, le=23),
    ]
    hour_before_reminder: Annotated[
        int,
        Field(ge=1, le=24),
    ]


class TaskOutSchema(TaskInSchema):
    id: int
    date_of_completion: datetime.date | None


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

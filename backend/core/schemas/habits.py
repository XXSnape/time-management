import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from core.schemas.common import IdSchema, PaginatedSchema
from core.utils.enums import Weekday

type HourLimits = Annotated[int, Field(ge=0, le=23)]


class HabitIdSchema(BaseModel):
    habit_id: int


class HabitNameSchema(BaseModel):
    name: str


class HabitSchema(HabitNameSchema):
    purpose: str


class ScheduleSchema(HabitIdSchema):
    day: Weekday


class TimerSchema(HabitIdSchema):
    notification_hour: HourLimits


class HabitInSchema(HabitSchema):
    days: set[Weekday]
    hours: set[HourLimits]


class HabitUpdateSchema(BaseModel):
    name: str | None = None
    purpose: str | None = None
    days: set[Weekday] | None = None
    hours: set[HourLimits] | None = None
    date_of_completion: datetime.date | None = None


class HabitOutSchema(IdSchema, HabitInSchema):
    created: datetime.date
    number_of_executions: int = 0
    completed: int
    total: int
    performance: int


class HabitCreateSchema(HabitSchema):
    user_id: int


class LittleInfoHabitOutSchema(IdSchema, HabitNameSchema):
    pass


class PaginatedHabitsOutSchema(
    PaginatedSchema[LittleInfoHabitOutSchema],
):
    pass

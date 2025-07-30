import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from core.schemas.common import IdSchema
from core.utils.enums import Weekday


type HourLimits = Annotated[int, Field(ge=0, le=23)]


class HabitIdSchema(BaseModel):
    habit_id: int


class HabitSchema(BaseModel):
    name: str
    purpose: str


class ScheduleSchema(HabitIdSchema):
    day: Weekday


class TimerSchema(HabitIdSchema):
    notification_hour: HourLimits


class HabitInSchema(HabitSchema):
    days: set[Weekday]
    hours: set[HourLimits]


class HabitOutSchema(IdSchema, HabitInSchema):
    created: datetime.date
    number_of_executions: int = 0


class HabitBaseInfo(IdSchema, HabitSchema):
    created: datetime.date
    number_of_executions: int = 0


class HabitCreateSchema(HabitSchema):
    user_id: int

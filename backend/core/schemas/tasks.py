from typing import Self, Annotated

from pydantic import BaseModel, model_validator, Field, ValidationError
import datetime


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

    @model_validator(mode="after")
    def check_date_and_time(self) -> Self:
        moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
        dt = datetime.datetime(
            year=self.deadline_date.year,
            month=self.deadline_date.month,
            day=self.deadline_date.day,
            hour=self.deadline_time,
            tzinfo=moscow_tz,
        )
        moscow_dt = datetime.datetime.now(moscow_tz)

        if moscow_dt >= dt:
            raise ValueError(
                "Входящие дата и время меньше, чем текущее московское",
            )
        return self


class TaskOutSchema(TaskInSchema):
    id: int
    date_of_completion: datetime.date | None


class TaskCreateSchema(TaskInSchema):
    user_id: int

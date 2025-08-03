import datetime
from typing import Annotated

from pydantic import BaseModel, Field, computed_field

from core.utils.enums import Periods


class IdSchema(BaseModel):
    id: int


class PaginationSchema(BaseModel):
    total_count: int
    per_page: Annotated[int, Field(exclude=True)]

    @computed_field
    @property
    def pages(self) -> int:
        return (
            self.total_count + self.per_page - 1
        ) // self.per_page


class PaginatedSchema[S: BaseModel](PaginationSchema):
    items: list[S]
    page: int


class DateOfCompletionSchema(IdSchema):
    user_id: int
    date_of_completion: None = None


class UpdateDateOfCompletionSchema(BaseModel):
    date_of_completion: datetime.date


class BaseStatisticSchema(BaseModel):
    period: Periods
    total: int

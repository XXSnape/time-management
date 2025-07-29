from typing import Annotated

from pydantic import BaseModel, computed_field, Field


class IdSchema(BaseModel):
    id: int


class PaginatedSchema[S: BaseModel](BaseModel):
    items: list[S]
    total_count: int
    page: int
    per_page: Annotated[int, Field(exclude=True)]

    @computed_field
    @property
    def pages(self) -> int:
        return (self.total_count + self.per_page - 1) // self.per_page

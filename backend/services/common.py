from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.base import BaseDAO
from core.schemas.common import (
    DateOfCompletionSchema,
    PaginationSchema,
    UpdateDateOfCompletionSchema,
)


async def mark_completed(
    session: AsyncSession,
    user_id: int,
    entity_id: int,
    per_page: int,
    dao: type[BaseDAO],
    updated_date_of_completion: UpdateDateOfCompletionSchema,
    exc: HTTPException,
):
    dao_obj = dao(session=session)
    result = await dao_obj.update(
        filters=DateOfCompletionSchema(
            id=entity_id,
            user_id=user_id,
            date_of_completion=None,
        ),
        values=updated_date_of_completion,
    )
    if result == 0:
        raise exc
    _, total_count = await dao_obj.get_total_items(user_id=user_id)
    return PaginationSchema(
        per_page=per_page,
        total_count=total_count,
    )


async def delete_entity(
    session: AsyncSession,
    user_id: int,
    entity_id: int,
    per_page: int,
    dao: type[BaseDAO],
    exc: HTTPException,
) -> PaginationSchema:
    dao_obj = dao(session=session)
    result = await dao_obj.delete(
        DateOfCompletionSchema(
            id=entity_id,
            user_id=user_id,
            date_of_completion=None,
        )
    )
    if result == 0:
        raise exc
    _, total_count = await dao_obj.get_total_items(user_id=user_id)
    return PaginationSchema(
        per_page=per_page,
        total_count=total_count,
    )

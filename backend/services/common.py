from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.base import BaseDAO
from core.schemas.common import DateOfCompletionSchema


async def delete_entity(
    session: AsyncSession,
    user_id: int,
    entity_id: int,
    dao: type[BaseDAO],
    exc: HTTPException,
) -> None:
    result = await dao(session=session).delete(
        DateOfCompletionSchema(
            id=entity_id,
            user_id=user_id,
            date_of_completion=None,
        )
    )
    if result == 0:
        raise exc

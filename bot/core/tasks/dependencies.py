from typing import TypeAlias, Annotated
from fast_depends import Depends

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.utils.sessions import async_session_maker


async def http_client():
    async with AsyncClient() as client:
        yield client


async def get_session():
    async with async_session_maker() as session:
        yield session


HttpClient: TypeAlias = Annotated[AsyncClient, Depends(http_client)]
Session: TypeAlias = Annotated[AsyncSession, Depends(get_session)]

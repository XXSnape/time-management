from typing import TypeAlias, Annotated
from fast_depends import Depends

from httpx import AsyncClient


async def http_client():
    async with AsyncClient() as client:
        yield client


HttpClient: TypeAlias = Annotated[AsyncClient, Depends(http_client)]

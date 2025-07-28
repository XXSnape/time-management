import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config import settings

from api import router as api_router
from core.dependencies.helper import db_helper

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Завершает соединение с базой данный.
    """

    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
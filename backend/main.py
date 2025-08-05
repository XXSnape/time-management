import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from api import router as api_router
from core.config import settings
from core.dependencies.db import db_helper
from core.locales.localization import get_translations
from core.utils.exc import RedirectException
from views import router as views_router

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Завершает соединение с базой данных.
    """
    app.state.translations = get_translations()

    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api_router)
main_app.include_router(views_router)
main_app.mount(
    "/static",
    StaticFiles(
        directory=Path(__file__).resolve().parent / "static"
    ),
    name="static",
)


@main_app.exception_handler(RedirectException)
async def redirect_exception_handler(
    request: Request, exc: RedirectException
):
    return RedirectResponse(
        url="/login",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )

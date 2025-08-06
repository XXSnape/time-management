import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from sqladmin import Admin
from starlette.responses import RedirectResponse

from api import router as api_router
from core.admin.auth import AdminAuth
from core.config import settings
from core.dependencies.db import db_helper
from core.locales.localization import get_translations
from core.utils.exc import RedirectException
from core.admin import views as admin_views
from services.users import create_admin
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
    await create_admin(
        username=settings.db.admin_login,
        password=settings.db.admin_password,
        telegram_id=settings.db.admin_telegram_id,
    )
    app.state.translations = get_translations()

    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api_router)
main_app.include_router(views_router)
views = [
    admin_views.HabitAdmin,
    admin_views.ScheduleAdmin,
    admin_views.TaskAdmin,
    admin_views.TimerAdmin,
    admin_views.TrackerAdmin,
    admin_views.UserAdmin,
]
admin = Admin(
    main_app,
    db_helper.engine,
    authentication_backend=AdminAuth(settings.auth_jwt.session_key),
)

for view in views:
    admin.add_view(view)


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

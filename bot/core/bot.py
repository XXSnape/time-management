from aiogram import Bot, Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import I18n
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from httpx import AsyncClient

from core.commands import Commands
from core.config import settings
from core.exc import (
    DataIsOutdated,
    ServerIsUnavailableExc,
    UnauthorizedExc,
)
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from middlewares.http import HttpClientMiddleware
from middlewares.i18n import LocaleFromDatabaseMiddleware
from routers import router
from routers.common_handlers import (
    on_data_is_outdated,
    on_server_is_unavailable,
    on_unauthorized,
    on_unknown_intent,
    on_unknown_state,
)


async def configure_bot(
    bot: Bot,
    dp: Dispatcher,
    client: AsyncClient,
):
    commands = [
        BotCommand(command=command.name, description=command)
        for command in Commands
    ]
    await bot.set_my_commands(
        commands, BotCommandScopeAllPrivateChats()
    )
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    dp.include_router(router)
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())
    i18n = I18n(
        path=settings.locale.path,
        default_locale=settings.locale.default_locale,
        domain=settings.locale.domain,
    )
    dp.update.middleware(LocaleFromDatabaseMiddleware(i18n=i18n))
    dp.update.middleware(HttpClientMiddleware(client=client))
    dp.errors.middleware(DatabaseMiddlewareWithoutCommit())
    dp.errors.middleware(LocaleFromDatabaseMiddleware(i18n=i18n))
    setup_dialogs(dp)
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_state,
        ExceptionTypeFilter(UnknownState),
    )
    dp.errors.register(
        on_server_is_unavailable,
        ExceptionTypeFilter(ServerIsUnavailableExc),
    )
    dp.errors.register(
        on_unauthorized,
        ExceptionTypeFilter(UnauthorizedExc),
    )
    dp.errors.register(
        on_data_is_outdated,
        ExceptionTypeFilter(DataIsOutdated),
    )

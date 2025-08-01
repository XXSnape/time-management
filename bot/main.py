import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import (
    I18n,
)
from aiogram_dialog import setup_dialogs
from httpx import AsyncClient

from core.commands import Commands
from core.exc import ServerIsUnavailableExc, UnauthorizedExc
from database.utils.sessions import engine
from middlewares.http import HttpClientMiddleware
from routers import router

from core.config import settings
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
    DatabaseMiddlewareWithCommit,
)
from middlewares.i18n import LocaleFromDatabaseMiddleware
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from routers.common_handlers import (
    on_server_is_unavailable,
    on_unauthorized,
)

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=settings.logging.log_level_value,
        format=settings.logging.log_format,
    )
    commands = [
        BotCommand(command=command.name, description=command)
        for command in Commands
    ]
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.set_my_commands(
        commands, BotCommandScopeAllPrivateChats()
    )
    await bot.delete_webhook(drop_pending_updates=True)
    redis = Redis(host=settings.redis.host, port=settings.redis.port)
    storage = RedisStorage(
        redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp = Dispatcher(
        storage=storage,
    )
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
    client = AsyncClient()
    dp.update.middleware(HttpClientMiddleware(client=client))
    dp.errors.middleware(DatabaseMiddlewareWithoutCommit())
    dp.errors.middleware(LocaleFromDatabaseMiddleware(i18n=i18n))
    dp.errors.register(
        on_server_is_unavailable,
        ExceptionTypeFilter(ServerIsUnavailableExc),
    )
    dp.errors.register(
        on_unauthorized,
        ExceptionTypeFilter(UnauthorizedExc),
    )
    try:
        logger.info("Запускаем бота...")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Завершение работы пользователем")
    finally:
        logger.info("Останавливаем бота...")
        await client.aclose()
        await engine.dispose()
        logger.info("Ресурсы освобождены!")


if __name__ == "__main__":
    asyncio.run(main())

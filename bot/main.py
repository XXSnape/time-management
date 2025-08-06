import asyncio
import logging

from aiogram import Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import (
    I18n,
)
from aiogram_dialog import setup_dialogs
from httpx import AsyncClient

from core.bot import configure_bot
from core.commands import Commands
from core.exc import (
    ServerIsUnavailableExc,
    UnauthorizedExc,
    DataIsOutdated,
)
from core.scheduler.settings import register_tasks
from core.utils.request import set_new_admin_token
from database.utils.sessions import engine
from middlewares.http import HttpClientMiddleware
from routers import router

from core.config import settings, bot, broker, scheduler, redis
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
    DatabaseMiddlewareWithCommit,
)
from middlewares.i18n import LocaleFromDatabaseMiddleware
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from routers.common_handlers import (
    on_server_is_unavailable,
    on_unauthorized,
    on_data_is_outdated,
)

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=settings.logging.log_level_value,
        format=settings.logging.log_format,
    )
    storage = RedisStorage(
        redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp = Dispatcher(
        storage=storage,
    )
    # commands = [
    #     BotCommand(command=command.name, description=command)
    #     for command in Commands
    # ]
    # await bot.set_my_commands(
    #     commands, BotCommandScopeAllPrivateChats()
    # )
    # await bot.delete_webhook(drop_pending_updates=True)
    # setup_dialogs(dp)
    # dp.include_router(router)
    # dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    # dp.update.middleware.register(DatabaseMiddlewareWithCommit())
    # i18n = I18n(
    #     path=settings.locale.path,
    #     default_locale=settings.locale.default_locale,
    #     domain=settings.locale.domain,
    # )
    # dp.update.middleware(LocaleFromDatabaseMiddleware(i18n=i18n))
    client = AsyncClient()
    # dp.update.middleware(HttpClientMiddleware(client=client))
    # dp.errors.middleware(DatabaseMiddlewareWithoutCommit())
    # dp.errors.middleware(LocaleFromDatabaseMiddleware(i18n=i18n))
    # setup_dialogs(dp)
    # dp.errors.register(
    #     on_server_is_unavailable,
    #     ExceptionTypeFilter(ServerIsUnavailableExc),
    # )
    # dp.errors.register(
    #     on_unauthorized,
    #     ExceptionTypeFilter(UnauthorizedExc),
    # )
    # dp.errors.register(
    #     on_data_is_outdated,
    #     ExceptionTypeFilter(DataIsOutdated),
    # )
    await configure_bot(
        bot=bot,
        dp=dp,
        client=client,
    )
    try:
        logger.info("Запускаем бота...")
        try:
            await set_new_admin_token(client=client)
        except (ServerIsUnavailableExc, UnauthorizedExc):
            logger.warning(
                "Не удалось получить токен администратора. "
                "Проверьте настройки и запустите бота снова."
            )
            return
        register_tasks()
        await broker.connect()
        scheduler.start()
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Завершение работы пользователем")
    finally:
        logger.info("Останавливаем бота...")
        await client.aclose()
        await broker.stop()
        await engine.dispose()
        try:
            scheduler.shutdown(wait=False)
        except AttributeError:
            logger.warning("Планировщик не был запущен.")

        logger.info("Ресурсы освобождены!")


if __name__ == "__main__":
    asyncio.run(main())

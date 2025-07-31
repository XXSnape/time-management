import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram.utils.i18n import (
    I18n,
)
from aiogram_dialog import setup_dialogs

from core.commands import Commands
from routers import router

from core.config import settings
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
    DatabaseMiddlewareWithCommit,
)
from middlewares.i18n import LocaleFromDatabaseMiddleware


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

    dp = Dispatcher()
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

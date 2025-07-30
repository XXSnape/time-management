import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings


if __name__ == "__main__":
    logging.basicConfig(
        level=settings.logging.log_level_value,
        format=settings.logging.log_format,
    )

    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.run_polling(bot)

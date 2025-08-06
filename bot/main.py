import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from httpx import AsyncClient

from core.bot import configure_bot
from core.config import bot, broker, redis, scheduler, settings
from core.exc import (
    ServerIsUnavailableExc,
    UnauthorizedExc,
)
from core.scheduler.settings import register_tasks
from core.utils.request import set_new_admin_token
from database.utils.sessions import engine

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
    client = AsyncClient()
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

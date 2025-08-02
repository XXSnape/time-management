import logging
from typing import Literal

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.enums import Languages

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

load_dotenv()


class ApiConfig(BaseModel):
    url_schema: str = "http"
    base_url: str = "localhost"
    port: str = "8000"
    path: str = "api/v1"

    def get_url(self, endpoint: str) -> str:
        port = f":{self.port}" if self.port else ""
        return (
            f"{self.url_schema}://{self.base_url}"
            f"{port}/{self.path}/{endpoint}"
        )


class LoggingConfig(BaseModel):
    """
    Конфигурация логирования приложения.
    """

    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        """
        Возвращает числовое значение уровня логирования.
        """
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class BotConfig(BaseSettings):
    token: str
    max_login_length: int = 40
    max_name_length: int = 50
    max_description_length: int = 250
    model_config = SettingsConfigDict(env_prefix="bot_")


class RedisConfig(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="redis_"
    )


class DatabaseConfig(BaseModel):
    """
    Конфигурация базы данных.
    """

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    echo: bool = False

    @property
    def url(self) -> str:
        """
        Возвращает строку для подключения к базе данных.
        """
        base_dir = Path(__file__).resolve().parent.parent
        return f"sqlite+aiosqlite:///{base_dir}/db.sqlite3"


class LocaleConfig(BaseModel):
    path: str = "locales"
    default_locale: Languages = Languages.ru
    domain: str = "time_management_bot"


class RabbitConfig(BaseSettings):
    default_user: str
    default_pass: str
    host: str
    port: int

    model_config = SettingsConfigDict(
        case_sensitive=False, env_prefix="rabbitmq_"
    )

    @property
    def url(self):
        return (
            f"amqp://{self.default_user}:"
            f"{self.default_pass}@{self.host}:{self.port}/"
        )


class Settings(BaseSettings):
    """
    Основные настройки приложения.
    """

    logging: LoggingConfig = LoggingConfig()
    bot: BotConfig = BotConfig()
    db: DatabaseConfig = DatabaseConfig()
    locale: LocaleConfig = LocaleConfig()
    api: ApiConfig = ApiConfig()
    redis: RedisConfig = RedisConfig()
    rabbit: RabbitConfig = RabbitConfig()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()

bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

scheduler = AsyncIOScheduler(
    jobstores={
        "default": RedisJobStore(
            host=settings.redis.host,
            port=settings.redis.port,
        )
    }
)


broker = RabbitBroker(settings.rabbit.url)
app = FastStream(broker)

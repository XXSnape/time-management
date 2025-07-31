import logging
from typing import Literal

from dotenv import load_dotenv
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
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()

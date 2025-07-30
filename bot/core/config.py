import logging
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

load_dotenv()


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


class BotSettings(BaseSettings):
    token: str
    model_config = SettingsConfigDict(env_prefix="bot_")


class DatabaseConfig(BaseModel):
    """
    Конфигурация базы данных.
    """

    echo: bool = False

    @property
    def url(self) -> str:
        """
        Возвращает строку для подключения к базе данных.
        """
        base_dir = Path(__file__).resolve().parent.parent
        return f"sqlite+aiosqlite:///{base_dir}/db.sqlite3"


class Settings(BaseSettings):
    """
    Основные настройки приложения.
    """

    logging: LoggingConfig = LoggingConfig()
    bot: BotSettings = BotSettings()
    db: DatabaseConfig = DatabaseConfig()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()

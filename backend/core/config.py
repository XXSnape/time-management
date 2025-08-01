import logging
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class AuthJWTSettings(BaseSettings):
    """
    private_key_path - путь к закрытому ключу
    public_key_path - путь к открытому ключу
    access_token_expire_minutes - действие токена в минутах
    algorithm - алгоритм шифрования
    """

    private_key_path: Path = BASE_DIR / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    cookie_key_token: str = "access-token"
    access_token_expire_days: int = 5
    algorithm: str = "RS256"


class RunConfig(BaseModel):
    """
    Конфигурация для запуска приложения.
    """

    host: str = "127.0.0.1"
    port: int = 8000


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


class ApiV1Prefix(BaseModel):
    """
    Префиксы для API версии 1.
    """

    prefix: str = "/v1"
    users: str = "/users"
    tasks: str = "/tasks"
    habits: str = "/habits"


class ApiPrefix(BaseModel):
    """
    Конфигурация префиксов для API.
    """

    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseSettings):
    """
    Конфигурация базы данных.
    """

    db_host: str
    db_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    echo: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        """
        Возвращает строку для подключения к базе данных.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.db_port}/{self.postgres_db}"
        )


class Settings(BaseSettings):
    """
    Основные настройки приложения.
    """

    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig = DatabaseConfig()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


settings = Settings()

# mypy: ignore-errors
import os
from functools import lru_cache
from typing import ClassVar

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(os.getenv('ENV_FILE', '.env'))


class AppConfig(BaseSettings):
    worker_count: int = 2


class DBConfig(BaseSettings):
    url: str
    echo_log: bool

    class Config:
        env_prefix = 'db_'


class RedisConfig(BaseSettings):
    host: str
    port: int

    class Config:
        env_prefix = 'redis_'


class Settings(BaseSettings):
    app: ClassVar = AppConfig()
    db: ClassVar = DBConfig()
    redis: ClassVar = RedisConfig()


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    return settings


config = get_settings()

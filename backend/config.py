from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: PostgresDsn


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings

"""Application configuration via pydantic-settings (Artículo IV.3)."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Load configuration from .env file.

    Constitution Article IV.3: SECRET_KEY and DATABASE_URL live only in .env
    (never versionedand never hardcoded).
    """

    # Secret key for JWT signing (generate via: openssl rand -hex 32)
    SECRET_KEY: str

    # Database URL (SQLite for dev, Postgres for prod)
    DATABASE_URL: str = "sqlite:///./gastos.db"

    # JWT expiry in minutes (configurable, never infinite per Artículo IV.2)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

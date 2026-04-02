"""Application configuration — all settings loaded from environment variables."""
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    APP_NAME: str = "MAEDIIA Platform API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/dbname

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    SESSION_DURATION_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,https://dashboard.maediia.com"

    # xAI
    XAI_API_KEY: str = ""

    # LiveKit
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = ""

    # Telnyx
    TELNYX_API_KEY: str = ""
    TELNYX_WEBHOOK_SECRET: str = ""
    TELNYX_SIP_CONNECTION_ID: str = ""  # SIP connection for voice agent numbers

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # HIPAA
    HIPAA_ENCRYPTION_KEY: str = ""

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Synchronous DB URL for Alembic (psycopg2 driver)."""
        return str(self.DATABASE_URL).replace("postgresql+asyncpg://", "postgresql://")

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        return [origin.strip() for origin in v.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

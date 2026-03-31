"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # App
    APP_NAME: str = "Maediia API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_URL_SYNC: str
    
    # Redis
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Voice
    VOICE_DEFAULT_MODEL: str = "alloy"
    VOICE_WEBSOCKET_TIMEOUT: int = 300
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in v.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

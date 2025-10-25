from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Scalper Bot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for cryptocurrency scalping bot management"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS Settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
    ]

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/scalper_bot"
    DB_ECHO_LOG: bool = False

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase Settings (for multi-user authentication)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None  # Anon key for client-side
    SUPABASE_SERVICE_KEY: Optional[str] = None  # Service role key for server-side
    SUPABASE_JWT_SECRET: Optional[str] = None  # JWT secret for token verification

    # Exchange API Keys (Optional, for testing)
    BYBIT_API_KEY: Optional[str] = None
    BYBIT_SECRET_KEY: Optional[str] = None
    BYBIT_TESTNET: bool = True

    COINDCX_API_KEY: Optional[str] = None
    COINDCX_API_SECRET: Optional[str] = None

    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30

    # Bot Settings
    MAX_BOTS_PER_USER: int = 10
    DEFAULT_BOT_STATUS: str = "STOPPED"

    # Telegram Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached instance of settings
    """
    return Settings()


# Create a global settings instance
settings = get_settings()

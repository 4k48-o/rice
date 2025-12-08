"""
FastAPI application configuration using Pydantic Settings.
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "FastAndtAdmin"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = ""  # REQUIRED: Set via environment variable
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""  # Set via environment variable

    
    # Security
    SECRET_KEY: str = ""  # REQUIRED: Set via environment variable, must be at least 32 characters
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_EXPIRE_DAYS: int = 30 # Password requires change every 30 days
    PASSWORD_REQUIRE_COMPLEXITY: bool = True # Require Upper, Lower, Special chars
    SINGLE_SESSION_MODE: bool = False # Temporarily disabled due to Redis auth issue

    
    # Snowflake ID Generator
    SNOWFLAKE_DATACENTER_ID: int = 0  # 0-31, set unique per datacenter
    SNOWFLAKE_WORKER_ID: int = 0      # 0-31, set unique per worker/instance
    SNOWFLAKE_EPOCH: int = 1609459200000  # 2021-01-01 00:00:00 UTC (milliseconds)

    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.APP_ENV == "development"


# Global settings instance
settings = Settings()

# Validate required settings (only warn in development)
if not settings.DATABASE_URL:
    if settings.is_development:
        import warnings
        warnings.warn("DATABASE_URL is not set. Please set it in .env file.", UserWarning)
    else:
        raise ValueError("DATABASE_URL is required. Please set it in .env file or environment variable.")

if not settings.SECRET_KEY or settings.SECRET_KEY in ("your-secret-key-here", ""):
    import warnings
    warnings.warn(
        "SECRET_KEY is not set or using default value. "
        "Please set a secure SECRET_KEY in .env file for production!",
        UserWarning
    )

"""Application configuration settings using Pydantic Settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application global settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    APP_NAME: str = "ITR-TaxPilot"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = Field(default="development", description="development, staging, production")
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default-insecure-secret-key-for-development-only"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated allowed origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Database & Redis
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/itrtaxpilot"
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-3.6-flash"
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"

    # Document upload limits
    MAX_UPLOAD_SIZE_MB: int = 10
    DOCUMENT_RETENTION_MINUTES: int = 30
    ALLOWED_MIME_TYPES: str = "application/pdf"

    @property
    def allowed_mimes(self) -> list[str]:
        """Parse comma-separated MIME types."""
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(",") if mime.strip()]

    # Logging & Telemetry
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_PII_MASKING: bool = True


@lru_cache
def get_settings() -> Settings:
    """Cached singleton instance of Settings."""
    return Settings()

"""
Application configuration using Pydantic Settings.

All configuration is loaded from environment variables with sensible
development defaults. Production deployments MUST override these via
environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "Cyber Risk Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/cyber_risk"
    )

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Security — MUST be overridden in production
    SECRET_KEY: str = "replace_me_with_a_strong_random_secret"
    JWT_ALGORITHM: str = "HS256"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


# Singleton instance used across the application
settings = Settings()

"""
AMOS Backend Configuration

Centralized configuration management with environment variable support.
Handles production vs development settings, security, and external services.

Creator: Trang Phan
Version: 3.0.0
"""

import json
import os
from functools import lru_cache
from typing import List, Optional


class Settings:
    """Application settings loaded from environment variables."""

    # Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # CORS Configuration
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from environment variable."""
        origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000"]')
        try:
            return json.loads(origins_str)
        except json.JSONDecodeError:
            # Fallback to comma-separated list
            return [origin.strip() for origin in origins_str.split(",")]

    # API Documentation Security
    DOCS_ENABLED: bool = os.getenv("DOCS_ENABLED", "true").lower() == "true"
    DOCS_USERNAME: Optional[str] = os.getenv("DOCS_USERNAME")
    DOCS_PASSWORD: Optional[str] = os.getenv("DOCS_PASSWORD")

    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    SQLITE_URL: Optional[str] = os.getenv("SQLITE_URL", "sqlite:///./amos.db")

    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # External Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text")

    # Monitoring
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def docs_auth_required(self) -> bool:
        """Check if API docs should be password protected."""
        return self.is_production and bool(self.DOCS_USERNAME and self.DOCS_PASSWORD)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

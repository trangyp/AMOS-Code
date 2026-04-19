#!/usr/bin/env python3
"""AMOS Equation Configuration - Centralized Settings Management.

Production-grade configuration management using Pydantic Settings v2.
Provides type-safe, validated configuration with environment variable
support, secrets management, and hierarchical settings.

Features:
    - Pydantic Settings v2 with type validation
    - Environment variable auto-loading (.env support)
    - Hierarchical settings (Base → Dev → Prod → Test)
    - Secrets management with masking
    - Configuration caching and dependency injection
    - Runtime configuration updates
    - Configuration validation on startup

Architecture Pattern: Centralized Configuration with Validation
Best Practice: 2024-2025 Pydantic Settings v2

Usage:
    from equation_config import get_settings, Settings
    settings = get_settings()

    # Or use dependency injection in FastAPI
    from fastapi import Depends
    async def endpoint(settings: Settings = Depends(get_settings)):
        return {"debug": settings.app_debug}

Environment Variables:
    All settings can be overridden via environment variables.
    Examples:
        APP_DEBUG=true
        DATABASE_URL=postgresql://user:pass@host/db
        REDIS_URL=redis://localhost:6379/0
        LOG_LEVEL=INFO

Files:
    .env - Environment variables (gitignored)
    .env.example - Template for required variables
"""

import os
import sys
import logging
import secrets
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

# Pydantic Settings v2 imports with graceful fallback
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field, validator, field_validator, model_validator
    from pydantic import ValidationError, SecretStr, PostgresDsn, RedisDsn
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    PYDANTIC_SETTINGS_AVAILABLE = False
    # Fallback stubs
    BaseSettings = object  # type: ignore
    SettingsConfigDict = dict  # type: ignore
    Field = lambda **kwargs: None  # type: ignore
    SecretStr = str  # type: ignore
    PostgresDsn = str  # type: ignore
    RedisDsn = str  # type: ignore

# Logging configuration
logger = logging.getLogger("amos_equation_config")

# Environment detection
_ENV = os.getenv("APP_ENV", "development").lower()


class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        extra="ignore"
    )

    url: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL connection URL"
    )
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    user: str = Field(default="amos", description="Database user")
    password: SecretStr = Field(
        default=SecretStr("amos"),
        description="Database password"
    )
    name: str = Field(default="amos_equations", description="Database name")

    # Connection pool settings
    pool_size: int = Field(default=5, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        default=10, ge=0, le=100, description="Max pool overflow"
    )
    pool_timeout: int = Field(
        default=30, ge=1, description="Pool timeout in seconds"
    )

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str , values: Dict[str, Any]) -> str:
        """Build database URL from components if not provided."""
        if v:
            return v

        password = values.get("password")
        if isinstance(password, SecretStr):
            password = password.get_secret_value()

        return (
            f"postgresql://{values.get('user', 'amos')}:{password}"
            f"@{values.get('host', 'localhost')}:{values.get('port', 5432)}"
            f"/{values.get('name', 'amos_equations')}"
        )

    def get_async_url(self) -> str:
        """Get async PostgreSQL URL."""
        url = str(self.url) if self.url else self._build_url()
        return url.replace("postgresql://", "postgresql+asyncpg://")

    def _build_url(self) -> str:
        """Build URL from components."""
        password = self.password
        if isinstance(password, SecretStr):
            password = password.get_secret_value()
        return (
            f"postgresql://{self.user}:{password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        extra="ignore"
    )

    url: Optional[RedisDsn] = Field(
        default=None,
        description="Redis connection URL"
    )
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    password: Optional[SecretStr] = Field(
        default=None,
        description="Redis password"
    )

    # Connection settings
    socket_timeout: int = Field(default=5, ge=1, description="Socket timeout")
    socket_connect_timeout: int = Field(
        default=5, ge=1, description="Socket connect timeout"
    )
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout")

    @field_validator("url", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str , values: Dict[str, Any]) -> str:
        """Build Redis URL from components if not provided."""
        if v:
            return v

        password = values.get("password")
        if isinstance(password, SecretStr):
            password = password.get_secret_value()

        auth = f":{password}@" if password else ""
        return (
            f"redis://{auth}{values.get('host', 'localhost')}:"
            f"{values.get('port', 6379)}/{values.get('db', 0)}"
        )


class SecuritySettings(BaseSettings):
    """Security-related settings."""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        extra="ignore"
    )

    # Secret keys
    secret_key: SecretStr = Field(
        default=SecretStr(secrets.token_urlsafe(32)),
        description="Application secret key"
    )
    jwt_secret: SecretStr = Field(
        default=SecretStr(secrets.token_urlsafe(32)),
        description="JWT signing secret"
    )

    # JWT settings
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, description="Access token expiration"
    )
    refresh_token_expire_days: int = Field(
        default=7, ge=1, description="Refresh token expiration"
    )

    # CORS settings
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(
        default=True, description="Allow CORS credentials"
    )

    # Security headers
    hsts_max_age: int = Field(
        default=63072000, ge=0, description="HSTS max age in seconds"
    )
    csp_nonce_enabled: bool = Field(
        default=True, description="Enable CSP nonce generation"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""

    model_config = SettingsConfigDict(
        env_prefix="RATE_LIMIT_",
        extra="ignore"
    )

    enabled: bool = Field(default=True, description="Enable rate limiting")
    default_limit: int = Field(
        default=100, ge=1, description="Default requests per minute"
    )
    verify_limit: int = Field(
        default=30, ge=1, description="Verify endpoint requests per minute"
    )
    batch_limit: int = Field(
        default=10, ge=1, description="Batch endpoint requests per minute"
    )
    window_seconds: int = Field(
        default=60, ge=1, description="Rate limit window in seconds"
    )
    block_duration_seconds: int = Field(
        default=300, ge=1, description="Block duration after limit exceeded"
    )


class MetricsSettings(BaseSettings):
    """Prometheus metrics configuration."""

    model_config = SettingsConfigDict(
        env_prefix="METRICS_",
        extra="ignore"
    )

    enabled: bool = Field(default=True, description="Enable metrics collection")
    endpoint: str = Field(default="/metrics", description="Metrics endpoint path")
    namespace: str = Field(default="amos", description="Metrics namespace")
    subsystem: str = Field(
        default="equation", description="Metrics subsystem"
    )

    # Buckets for histograms
    latency_buckets: List[float] = Field(
        default=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0],
        description="Latency histogram buckets"
    )


class TracingSettings(BaseSettings):
    """OpenTelemetry tracing configuration."""

    model_config = SettingsConfigDict(
        env_prefix="TRACING_",
        extra="ignore"
    )

    enabled: bool = Field(default=True, description="Enable tracing")
    service_name: str = Field(
        default="amos-equation-api", description="Service name for tracing"
    )
    exporter_endpoint: str  = Field(
        default=None, description="OTLP exporter endpoint (e.g., http://jaeger:4317)"
    )
    sampling_rate: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Trace sampling rate"
    )
    console_export: bool = Field(
        default=False, description="Export traces to console"
    )


class TaskQueueSettings(BaseSettings):
    """Celery task queue configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CELERY_",
        extra="ignore"
    )

    broker_url: str  = Field(
        default=None, description="Celery broker URL (defaults to Redis)"
    )
    result_backend: str  = Field(
        default=None, description="Celery result backend (defaults to Redis)"
    )

    # Worker settings
    worker_concurrency: int = Field(
        default=4, ge=1, description="Worker concurrency"
    )
    worker_prefetch_multiplier: int = Field(
        default=4, ge=1, description="Worker prefetch multiplier"
    )
    task_time_limit: int = Field(
        default=3600, ge=1, description="Task time limit in seconds"
    )
    task_soft_time_limit: int = Field(
        default=3300, ge=1, description="Task soft time limit in seconds"
    )

    @model_validator(mode="after")
    def set_defaults_from_redis(self) -> TaskQueueSettings:
        """Set default broker/result backend from Redis URL if not set."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        if self.broker_url is None:
            self.broker_url = redis_url
        if self.result_backend is None:
            self.result_backend = redis_url

        return self


class CacheSettings(BaseSettings):
    """Cache configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        extra="ignore"
    )

    enabled: bool = Field(default=True, description="Enable caching")
    default_ttl: int = Field(
        default=3600, ge=1, description="Default cache TTL in seconds"
    )
    query_cache_ttl: int = Field(
        default=300, ge=1, description="Query cache TTL in seconds"
    )
    result_cache_ttl: int = Field(
        default=86400, ge=1, description="Result cache TTL in seconds"
    )
    max_key_length: int = Field(
        default=250, ge=1, description="Maximum cache key length"
    )


class Settings(BaseSettings):
    """Main application settings.

    All settings can be overridden via environment variables
    with the appropriate prefix or without prefix for top-level settings.
    """

    model_config = SettingsConfigDict(
        # Load from .env file
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra fields for extensibility
        extra="ignore",
        # Validate on assignment
        validate_assignment=True,
        # Case insensitive for env vars
        case_sensitive=False,
    )

    # Application metadata
    app_name: str = Field(
        default="AMOS Equation API",
        description="Application name"
    )
    app_version: str = Field(default="2.0.0", description="Application version")
    app_description: str = Field(
        default="Unified Equation System with 1608+ mathematical functions",
        description="Application description"
    )

    # Environment
    app_env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    app_debug: bool = Field(default=False, description="Debug mode")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server bind port")
    workers: int = Field(default=1, ge=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload (dev only)")

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )

    # API settings
    api_version: str = Field(default="v1", description="Default API version")
    api_prefix: str = Field(default="/api", description="API route prefix")

    # Documentation
    docs_enabled: bool = Field(default=True, description="Enable API documentation")
    docs_url: str = Field(default="/docs", description="Swagger UI URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI schema URL")

    # Sub-settings (nested)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    metrics: MetricsSettings = Field(default_factory=MetricsSettings)
    tracing: TracingSettings = Field(default_factory=TracingSettings)
    celery: TaskQueueSettings = Field(default_factory=TaskQueueSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)

    @field_validator("app_env", mode="before")
    @classmethod
    def parse_env(cls, v: str) -> Environment:
        """Parse environment string to enum."""
        if isinstance(v, str):
            v = v.lower()
            if v in ("dev", "development"):
                return Environment.DEVELOPMENT
            elif v in ("staging", "stage"):
                return Environment.STAGING
            elif v in ("prod", "production"):
                return Environment.PRODUCTION
            elif v in ("test", "testing"):
                return Environment.TESTING
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> Settings:
        """Validate settings for production environment."""
        if self.app_env == Environment.PRODUCTION:
            # Enforce security settings in production
            if self.app_debug:
                logger.warning("Debug mode should be disabled in production")

            if self.workers < 2:
                logger.warning("Production should use multiple workers")

            # Check for default secrets
            if self.security.secret_key.get_secret_value() == secrets.token_urlsafe(32):
                logger.warning("Using auto-generated secret key - set SECURITY_SECRET_KEY")

        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env == Environment.TESTING

    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Convert settings to dictionary.

        Args:
            mask_secrets: Whether to mask secret values

        Returns:
            Dictionary of settings
        """
        data = self.model_dump()

        if mask_secrets:
            # Mask secret fields
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if "password" in sub_key or "secret" in sub_key:
                            value[sub_key] = "***"

        return data

    def configure_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.value),
            format=self.log_format,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )


# Global settings instance (cached)
_settings: Optional[Settings] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance (cached for performance)
    """
    global _settings

    if _settings is None:
        try:
            _settings = Settings()
            _settings.configure_logging()
            logger.info(f"Settings loaded for environment: {_settings.app_env.value}")
        except ValidationError as e:
            logger.error(f"Settings validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise

    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment (for runtime updates).

    Returns:
        Fresh Settings instance
    """
    global _settings
    _settings = None
    get_settings.cache_clear()
    return get_settings()


def get_settings_dependency() -> Settings:
    """FastAPI dependency for settings injection.

    Usage:
        from fastapi import Depends
        from equation_config import get_settings_dependency

        @app.get("/config")
        async def get_config(settings: Settings = Depends(get_settings_dependency)):
            return settings.to_dict(mask_secrets=True)
    """
    return get_settings()


# Environment-specific settings classes
class DevelopmentSettings(Settings):
    """Development environment settings."""

    model_config = SettingsConfigDict(env_file=".env.development")

    app_debug: bool = True
    reload: bool = True
    log_level: LogLevel = LogLevel.DEBUG
    docs_enabled: bool = True


class ProductionSettings(Settings):
    """Production environment settings."""

    model_config = SettingsConfigDict(env_file=".env.production")

    app_debug: bool = False
    reload: bool = False
    workers: int = 4
    log_level: LogLevel = LogLevel.INFO

    # Disable docs in production by default
    docs_enabled: bool = False


class TestingSettings(Settings):
    """Testing environment settings."""

    model_config = SettingsConfigDict(env_file=".env.testing")

    app_env: Environment = Environment.TESTING
    app_debug: bool = True
    log_level: LogLevel = LogLevel.DEBUG

    # Use test database
    database: DatabaseSettings = Field(
        default_factory=lambda: DatabaseSettings(name="amos_equations_test")
    )


def create_env_file_example() -> str:
    """Create example .env file content.

    Returns:
        Example .env file content
    """
    return """# AMOS Equation API Configuration
# Copy this file to .env and customize values

# Application
APP_ENV=development
APP_DEBUG=true
APP_NAME=AMOS Equation API
APP_VERSION=2.0.0

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=true

# Logging
LOG_LEVEL=INFO

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=amos
DB_PASSWORD=your_secure_password
DB_NAME=amos_equations

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (generate strong secrets for production)
SECURITY_SECRET_KEY=your-secret-key-here
SECURITY_JWT_SECRET=your-jwt-secret-here
SECURITY_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_VERIFY=30

# Metrics
METRICS_ENABLED=true
METRICS_ENDPOINT=/metrics

# Tracing
TRACING_ENABLED=true
TRACING_SERVICE_NAME=amos-equation-api
TRACING_EXPORTER_ENDPOINT=http://localhost:4317

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Cache
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=3600
"""


def write_env_example() -> None:
    """Write .env.example file."""
    example_path = Path(".env.example")
    if not example_path.exists():
        example_path.write_text(create_env_file_example())
        logger.info(f"Created {example_path}")


# Initialize on module load
if PYDANTIC_SETTINGS_AVAILABLE:
    write_env_example()

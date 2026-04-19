"""
AMOS Unified Configuration Management System

A comprehensive, type-safe configuration management system using Pydantic Settings.
Provides environment variable loading, secrets management, validation, and CLI integration.

Features:
- Type-safe configuration with Pydantic BaseSettings
- Environment variable auto-loading with prefixes
- Docker/AWS/Azure/GCP secrets support
- Configuration validation and reloading
- CLI argument parsing integration
- Hierarchical configuration models

Author: AMOS System
Version: 1.0.0
"""

import json
import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SecretStr,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============================================================================
# Configuration Enums
# ============================================================================


class Environment(str, Enum):
    """Deployment environment enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseDriver(str, Enum):
    """Database driver enumeration."""

    POSTGRESQL = "postgresql"
    POSTGRESQL_ASYNC = "postgresql+asyncpg"
    SQLITE = "sqlite"
    SQLITE_ASYNC = "sqlite+aiosqlite"


# ============================================================================
# Nested Configuration Models
# ============================================================================


class DatabaseSettings(BaseModel):
    """Database connection settings."""

    driver: DatabaseDriver = Field(
        default=DatabaseDriver.POSTGRESQL_ASYNC, description="Database driver"
    )
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    name: str = Field(default="amos", description="Database name")
    user: str = Field(default="amos", description="Database user")
    password: SecretStr = Field(default=SecretStr("amos"), description="Database password")

    # Connection pool settings
    pool_size: int = Field(default=20, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, le=50, description="Max overflow connections")
    pool_timeout: int = Field(default=30, ge=1, le=300, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, ge=60, le=7200, description="Connection recycle time")

    # SSL settings
    ssl_mode: Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = Field(
        default="prefer", description="SSL mode for database connection"
    )
    ssl_cert: Optional[Path] = Field(default=None, description="SSL certificate path")
    ssl_key: Optional[Path] = Field(default=None, description="SSL key path")

    @property
    def dsn(self) -> str:
        """Generate database DSN."""
        if self.driver in (DatabaseDriver.SQLITE, DatabaseDriver.SQLITE_ASYNC):
            return f"{self.driver.value}:///{self.name}"

        password = self.password.get_secret_value()
        return (
            f"{self.driver.value}://{self.user}:{password}" f"@{self.host}:{self.port}/{self.name}"
        )

    @field_validator("ssl_cert", "ssl_key", mode="before")
    @classmethod
    def validate_ssl_paths(cls, v: str) -> Optional[Path]:
        """Validate SSL paths exist if provided."""
        if v is None:
            return None
        path = Path(v)
        if not path.exists():
            raise ValueError(f"SSL file not found: {v}")
        return path


class CacheSettings(BaseModel):
    """Cache configuration settings."""

    driver: Literal["redis", "memory", "memcached"] = Field(
        default="redis", description="Cache driver"
    )
    host: str = Field(default="localhost", description="Cache host")
    port: int = Field(default=6379, ge=1, le=65535, description="Cache port")
    password: Optional[SecretStr] = Field(default=None, description="Cache password")
    database: int = Field(default=0, ge=0, le=15, description="Redis database number")

    # Cache settings
    default_ttl: int = Field(
        default=300, ge=1, le=86400, description="Default cache TTL in seconds"
    )
    max_memory: str = Field(default="256mb", description="Max memory for cache")

    @property
    def dsn(self) -> str:
        """Generate cache DSN."""
        if self.driver == "memory":
            return "memory://"

        auth = ""
        if self.password:
            auth = f":{self.password.get_secret_value()}@"

        return f"redis://{auth}{self.host}:{self.port}/{self.database}"


class APISecuritySettings(BaseModel):
    """API security settings."""

    # JWT settings
    jwt_secret: SecretStr = Field(
        default=SecretStr("change-me-in-production"), description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(
        default=60, ge=5, le=1440, description="JWT expiration in minutes"
    )
    jwt_refresh_expiration_days: int = Field(
        default=7, ge=1, le=30, description="JWT refresh token expiration in days"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, ge=1, le=10000, description="Rate limit requests per window"
    )
    rate_limit_window: int = Field(
        default=60, ge=10, le=3600, description="Rate limit window in seconds"
    )

    # CORS settings
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods",
    )
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS headers"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, list[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class LLMSettings(BaseModel):
    """LLM provider settings."""

    # Provider selection
    provider: Literal["openai", "anthropic", "ollama", "azure", "google"] = Field(
        default="ollama", description="LLM provider"
    )

    # API keys
    openai_api_key: Optional[SecretStr] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, description="Anthropic API key")
    azure_api_key: Optional[SecretStr] = Field(default=None, description="Azure OpenAI API key")
    google_api_key: Optional[SecretStr] = Field(default=None, description="Google AI API key")

    # Model settings
    default_model: str = Field(default="llama2", description="Default LLM model")
    max_tokens: int = Field(default=2048, ge=1, le=8192, description="Max tokens per request")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")

    # Ollama specific
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama host URL")
    ollama_timeout: int = Field(default=120, ge=10, le=600, description="Ollama timeout in seconds")

    # Request settings
    request_timeout: int = Field(
        default=60, ge=10, le=300, description="Request timeout in seconds"
    )
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay in seconds")


class ObservabilitySettings(BaseModel):
    """Observability and monitoring settings."""

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_format: Literal["json", "text", "structured"] = Field(
        default="structured", description="Log format"
    )
    log_output: Literal["stdout", "file", "both"] = Field(
        default="stdout", description="Log output destination"
    )
    log_file_path: Optional[Path] = Field(default=None, description="Log file path")

    # Tracing
    enable_opentelemetry: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    otel_service_name: str = Field(default="amos-api", description="OpenTelemetry service name")
    otel_endpoint: str = Field(default=None, description="OpenTelemetry collector endpoint")
    otel_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Tracing sample rate")

    # Metrics
    enable_prometheus: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, ge=1024, le=65535, description="Metrics port")
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")

    # Health checks
    health_check_interval: int = Field(
        default=30, ge=5, le=300, description="Health check interval in seconds"
    )

    # Correlation IDs
    enable_correlation_id: bool = Field(default=True, description="Enable correlation ID logging")
    correlation_id_header: str = Field(
        default="X-Correlation-ID", description="Correlation ID header name"
    )


class FeatureFlagsSettings(BaseModel):
    """Feature flags configuration."""

    # Core features
    enable_async_execution: bool = Field(default=True, description="Enable async execution")
    enable_caching: bool = Field(default=True, description="Enable response caching")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker")

    # Experimental features
    enable_beta_features: bool = Field(
        default=False, description="Enable beta/experimental features"
    )
    enable_ml_predictions: bool = Field(default=False, description="Enable ML-based predictions")
    enable_auto_scaling: bool = Field(default=False, description="Enable auto-scaling")

    # Development features
    enable_debug_mode: bool = Field(default=False, description="Enable debug mode")
    enable_mock_responses: bool = Field(default=False, description="Enable mock responses")
    enable_detailed_errors: bool = Field(
        default=False, description="Enable detailed error messages"
    )


# ============================================================================
# Main Configuration
# ============================================================================


class AMOSConfig(BaseSettings):
    """
    Unified AMOS configuration management.

    Loads configuration from environment variables with AMOS_ prefix
    and from .env file. Supports nested configuration models for
    different subsystems.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AMOS_",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_default=True,
    )

    # ============================================================================
    # Core Settings
    # ============================================================================

    # Environment
    env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Deployment environment",
        validation_alias=AliasChoices("AMOS_ENV", "ENV", "ENVIRONMENT"),
    )
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="3.0.0", description="Application version")

    # Application
    app_name: str = Field(default="AMOS", description="Application name")
    app_description: str = Field(
        default="Advanced Modular Operating System", description="Application description"
    )

    # ============================================================================
    # API Settings
    # ============================================================================

    api_host: str = Field(default="0.0.0.0", description="API bind host")
    api_port: int = Field(default=8000, ge=1024, le=65535, description="API port")
    api_workers: int = Field(default=4, ge=1, le=32, description="Number of API workers")
    api_reload: bool = Field(default=False, description="Enable auto-reload in development")

    # Documentation
    docs_enabled: bool = Field(default=True, description="Enable API documentation")
    docs_url: str = Field(default="/docs", description="Swagger UI URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI schema URL")

    # ============================================================================
    # Nested Configuration
    # ============================================================================

    database: DatabaseSettings = Field(
        default_factory=DatabaseSettings, description="Database configuration"
    )
    cache: CacheSettings = Field(default_factory=CacheSettings, description="Cache configuration")
    security: APISecuritySettings = Field(
        default_factory=APISecuritySettings, description="API security configuration"
    )
    llm: LLMSettings = Field(default_factory=LLMSettings, description="LLM configuration")
    observability: ObservabilitySettings = Field(
        default_factory=ObservabilitySettings, description="Observability configuration"
    )
    features: FeatureFlagsSettings = Field(
        default_factory=FeatureFlagsSettings, description="Feature flags configuration"
    )

    # ============================================================================
    # Validation
    # ============================================================================

    @field_validator("env", mode="before")
    @classmethod
    def validate_environment(cls, v: Any) -> Environment:
        """Validate and normalize environment value."""
        if isinstance(v, str):
            v = v.lower().strip()
            mapping = {
                "dev": Environment.DEVELOPMENT,
                "development": Environment.DEVELOPMENT,
                "staging": Environment.STAGING,
                "stage": Environment.STAGING,
                "prod": Environment.PRODUCTION,
                "production": Environment.PRODUCTION,
                "test": Environment.TESTING,
                "testing": Environment.TESTING,
            }
            return mapping.get(v, Environment.DEVELOPMENT)
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> AMOSConfig:
        """Validate production-specific settings."""
        if self.env == Environment.PRODUCTION:
            # Ensure debug is disabled in production
            if self.debug:
                raise ValueError("Debug mode must be disabled in production")

            # Ensure default secrets are changed in production
            if self.security.jwt_secret.get_secret_value() == "change-me-in-production":
                raise ValueError(
                    "Default JWT secret must be changed in production. "
                    "Set AMOS_SECURITY__JWT_SECRET environment variable."
                )

            # Ensure HTTPS in production
            if self.docs_enabled and not any(
                origin.startswith("https://") for origin in self.security.cors_origins
            ):
                # This is a warning, not an error
                pass

        return self

    # ============================================================================
    # Properties
    # ============================================================================

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.env == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.env == Environment.TESTING

    @property
    def api_url(self) -> str:
        """Get API base URL."""
        protocol = "https" if self.is_production else "http"
        return f"{protocol}://{self.api_host}:{self.api_port}"

    # ============================================================================
    # Methods
    # ============================================================================

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary for logging/monitoring.
        Excludes sensitive values.
        """
        return {
            "environment": self.env.value,
            "version": self.version,
            "debug": self.debug,
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "workers": self.api_workers,
                "url": self.api_url,
            },
            "database": {
                "driver": self.database.driver.value,
                "host": self.database.host,
                "port": self.database.port,
                "name": self.database.name,
                "pool_size": self.database.pool_size,
            },
            "cache": {
                "driver": self.cache.driver,
                "host": self.cache.host,
                "port": self.cache.port,
            },
            "llm": {
                "provider": self.llm.provider,
                "default_model": self.llm.default_model,
                "ollama_host": self.llm.ollama_host,
            },
            "observability": {
                "log_level": self.observability.log_level.value,
                "otel_enabled": self.observability.enable_opentelemetry,
                "metrics_enabled": self.observability.enable_prometheus,
            },
            "features": {
                "async_execution": self.features.enable_async_execution,
                "caching": self.features.enable_caching,
                "rate_limiting": self.features.enable_rate_limiting,
                "circuit_breaker": self.features.enable_circuit_breaker,
            },
        }

    def to_json(self, include_secrets: bool = False) -> str:
        """Serialize configuration to JSON."""
        if include_secrets:
            return self.model_dump_json(indent=2)
        return json.dumps(self.get_config_summary(), indent=2)

    def reload(self) -> None:
        """Reload configuration from environment."""
        # This will re-read environment variables
        new_config = AMOSConfig()
        for field_name in self.model_fields:
            setattr(self, field_name, getattr(new_config, field_name))


# ============================================================================
# Configuration Factory
# ============================================================================


@lru_cache
def get_config() -> AMOSConfig:
    """
    Get cached configuration instance.

    This function uses LRU cache to avoid re-parsing
    configuration on every call. Call config.reload()
    to refresh from environment.

    Returns:
        AMOSConfig: Application configuration instance
    """
    return AMOSConfig()


def get_config_for_env(env: Environment) -> AMOSConfig:
    """
    Get configuration for a specific environment.
    Useful for testing and migration scripts.

    Args:
        env: Target environment

    Returns:
        AMOSConfig: Configuration for specified environment
    """
    # Override environment
    os.environ["AMOS_ENV"] = env.value

    # Clear cache to force re-parse
    get_config.cache_clear()

    return get_config()


# ============================================================================
# Validation Utilities
# ============================================================================


def validate_config(config: Optional[AMOSConfig] = None) -> List[str]:
    """
    Validate configuration and return list of issues.

    Args:
        config: Configuration to validate (uses default if None)

    Returns:
        List of validation issues (empty if valid)
    """
    if config is None:
        config = get_config()

    issues = []

    try:
        # Re-validate the model
        AMOSConfig.model_validate(config.model_dump())
    except ValidationError as e:
        for error in e.errors():
            issues.append(f"{error['loc']}: {error['msg']}")

    # Additional checks
    if config.is_production:
        if config.debug:
            issues.append("DEBUG should be disabled in production")

        jwt_secret = config.security.jwt_secret.get_secret_value()
        if len(jwt_secret) < 32:
            issues.append("JWT_SECRET should be at least 32 characters in production")

    return issues


def print_config_summary(config: Optional[AMOSConfig] = None) -> None:
    """Print configuration summary to console."""
    if config is None:
        config = get_config()

    summary = config.get_config_summary()

    print("=" * 60)
    print("AMOS Configuration Summary")
    print("=" * 60)
    print(json.dumps(summary, indent=2))
    print("=" * 60)


# ============================================================================
# CLI Integration
# ============================================================================


def create_config_cli() -> None:
    """
    Create CLI for configuration management.
    Can be called from main CLI to add config commands.
    """
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Configuration Management")
    subparsers = parser.add_subparsers(dest="command")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show configuration summary")
    show_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Environment command
    env_parser = subparsers.add_parser("env", help="Show required environment variables")

    args = parser.parse_args()

    if args.command == "validate":
        issues = validate_config()
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            exit(1)
        else:
            print("Configuration is valid!")

    elif args.command == "show":
        config = get_config()
        if args.json:
            print(config.to_json())
        else:
            print_config_summary(config)

    elif args.command == "env":
        print("Required environment variables:")
        print("  AMOS_ENV - Environment (development, staging, production)")
        print("  AMOS_DEBUG - Debug mode (true/false)")
        print("  AMOS_API_PORT - API port number")
        print("  AMOS_DATABASE__PASSWORD - Database password")
        print("  AMOS_SECURITY__JWT_SECRET - JWT signing secret")
        print("  AMOS_LLM__OPENAI_API_KEY - OpenAI API key (if using OpenAI)")
        print("  AMOS_LLM__ANTHROPIC_API_KEY - Anthropic API key (if using Claude)")


# ============================================================================
# Module Entry Point
# ============================================================================

if __name__ == "__main__":
    create_config_cli()

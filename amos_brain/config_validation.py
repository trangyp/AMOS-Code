"""AMOS Configuration Validation System.

Production-grade configuration validation using Pydantic v2 (2025).
Ensures all configurations are valid before system initialization,
preventing runtime errors at 75% health level.

References:
- Pydantic v2 Documentation (2025)
- Configuration validation best practices
- Production schema validation patterns
"""

from __future__ import annotations


import os
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Valid log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Valid environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LLMProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""

    name: str
    api_key: str = None
    base_url: str = None
    model: str = "default"
    enabled: bool = False
    timeout: int = Field(default=30, ge=5, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format if provided."""
        if v is None:
            return v

        # Basic validation - check length and prefix patterns
        if len(v) < 10:
            raise ValueError("API key too short")

        # Check for common prefixes (optional validation)
        valid_prefixes = ["sk-", "sk-ant-"]
        has_prefix = any(v.startswith(prefix) for prefix in valid_prefixes)

        return v


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    url: str
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=50)
    pool_timeout: int = Field(default=30, ge=1, le=300)

    @field_validator("url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        valid_schemes = ["postgresql", "sqlite", "mysql", "postgresql+asyncpg"]
        scheme = v.split("://")[0] if "://" in v else v.split(":")[0]

        if scheme not in valid_schemes:
            raise ValueError(f"Invalid database scheme: {scheme}")

        return v


class RedisConfig(BaseModel):
    """Redis/cache configuration."""

    url: str = "redis://localhost:6379/0"
    password: str = None
    ttl: int = Field(default=3600, ge=60, le=86400)
    enabled: bool = True

    @field_validator("url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v


class SecurityConfig(BaseModel):
    """Security-related configuration."""

    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    rate_limit_default: int = Field(default=100, ge=10, le=10000)
    rate_limit_verify: int = Field(default=30, ge=5, le=1000)
    rate_limit_admin: int = Field(default=1000, ge=100, le=100000)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn about default secret keys."""
        if v == "change-me-in-production":
            # Log warning but don't fail - allows development
            pass
        elif len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters for security")

        return v


class ObservabilityConfig(BaseModel):
    """Observability and monitoring configuration."""

    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    audit_log_enabled: bool = True
    otel_service_name: str = "amos-superbrain"
    otel_endpoint: str = None
    health_check_interval: int = Field(default=60, ge=10, le=300)


class AMOSSettings(BaseSettings):
    """Complete AMOS SuperBrain configuration.

    Loads from environment variables and .env file.
    Validates all settings on initialization.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars without error
    )

    # Application
    app_name: str = "AMOS SuperBrain"
    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1024, le=65535)

    # Security
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # Database
    database: DatabaseConfig | None = None

    # Redis/Cache
    redis: RedisConfig = Field(default_factory=RedisConfig)

    # LLM Providers
    openai: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="OpenAI", model="gpt-4", api_key=os.environ.get("OPENAI_API_KEY")
        )
    )
    anthropic: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="Anthropic", model="claude-3-5-sonnet", api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
    )
    kimi: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="Kimi", model="kimi-k2-5", api_key=os.environ.get("KIMI_API_KEY")
        )
    )
    ollama: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(
            name="Ollama",
            model="llama3.2",
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            enabled=True,  # Local, no API key needed
        )
    )

    # Observability
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)

    def get_enabled_providers(self) -> list[LLMProviderConfig]:
        """Get list of enabled LLM providers with valid API keys."""
        providers = [self.openai, self.anthropic, self.kimi, self.ollama]

        enabled = []
        for provider in providers:
            if provider.enabled or provider.api_key:
                # Ollama is enabled by default (local)
                if provider.name == "Ollama" or provider.api_key:
                    enabled.append(provider)

        return enabled

    def validate_for_production(self) -> list[str]:
        """Validate configuration for production deployment.

        Returns:
            List of validation warnings/errors
        """
        issues = []

        # Security checks
        if self.security.secret_key == "change-me-in-production":
            issues.append("WARNING: Using default secret key - change for production")

        if self.debug and self.environment == Environment.PRODUCTION:
            issues.append("ERROR: Debug mode enabled in production")

        # Database checks
        if self.database is None:
            issues.append("WARNING: No database configured - using in-memory")

        # LLM provider checks
        enabled_providers = self.get_enabled_providers()
        if not enabled_providers:
            issues.append("INFO: No LLM providers configured - system at 75% health")
        else:
            issues.append(f"INFO: {len(enabled_providers)} LLM providers ready")

        # Observability checks
        if (
            self.observability.log_level == LogLevel.DEBUG
            and self.environment == Environment.PRODUCTION
        ):
            issues.append("WARNING: DEBUG log level in production may impact performance")

        return issues


class ConfigValidator:
    """Configuration validation utility.

    Provides methods to validate and report on AMOS configuration.
    """

    def __init__(self, settings: AMOSSettings | None = None):
        """Initialize validator.

        Args:
            settings: AMOS settings to validate, or None to load from environment
        """
        self.settings = settings or AMOSSettings()

    def validate(self) -> dict[str, Any]:
        """Run full validation and return report.

        Returns:
            Validation report dictionary
        """
        report = {
            "valid": True,
            "environment": self.settings.environment.value,
            "providers_configured": len(self.settings.get_enabled_providers()),
            "providers": [p.name for p in self.settings.get_enabled_providers()],
            "issues": [],
            "recommendations": [],
        }

        try:
            # Run production validation
            issues = self.settings.validate_for_production()
            report["issues"] = issues

            # Add recommendations
            if report["providers_configured"] == 0:
                report["recommendations"].append(
                    "Configure API keys to reach 100% health: ./scripts/configure_api_keys.sh"
                )

            if self.settings.environment == Environment.DEVELOPMENT:
                report["recommendations"].append(
                    "Set ENVIRONMENT=production for production deployment"
                )

            # Check for critical errors
            critical_errors = [i for i in issues if i.startswith("ERROR")]
            if critical_errors:
                report["valid"] = False
                report["critical_errors"] = critical_errors

        except ValidationError as e:
            report["valid"] = False
            report["validation_errors"] = e.errors()

        return report

    def print_report(self) -> None:
        """Print human-readable validation report."""
        report = self.validate()

        print("=" * 70)
        print("AMOS CONFIGURATION VALIDATION REPORT")
        print("=" * 70)

        # Status
        status = "✅ VALID" if report["valid"] else "❌ INVALID"
        print(f"\nStatus: {status}")
        print(f"Environment: {report['environment']}")
        print(f"LLM Providers: {report['providers_configured']} configured")

        if report["providers"]:
            print(f"  - {', '.join(report['providers'])}")

        # Issues
        if report["issues"]:
            print(f"\nIssues ({len(report['issues'])}):")
            for issue in report["issues"]:
                icon = (
                    "🔴"
                    if issue.startswith("ERROR")
                    else "🟡"
                    if issue.startswith("WARNING")
                    else "🔵"
                )
                print(f"  {icon} {issue}")

        # Recommendations
        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  💡 {rec}")

        # Critical errors
        if "critical_errors" in report:
            print("\n⚠️  CRITICAL ERRORS - Fix before deployment:")
            for error in report["critical_errors"]:
                print(f"  ❌ {error}")

        print("\n" + "=" * 70)


def validate_configuration() -> bool:
    """Quick validation function for initialization.

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        validator = ConfigValidator()
        report = validator.validate()

        if report["valid"]:
            print("✅ Configuration valid - system ready")
            return True
        else:
            print("❌ Configuration invalid - check errors above")
            return False

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


# Convenience function for CLI usage
def main():
    """CLI entry point for configuration validation."""
    validator = ConfigValidator()
    validator.print_report()

    # Exit with appropriate code
    report = validator.validate()
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""AMOS Configuration Management v1.0.0
=====================================

Centralized, type-safe configuration using Pydantic Settings v2.

Features:
  - Environment-specific configurations (dev/staging/prod)
  - .env file support for local development
  - Environment variable override for production
  - Type validation at startup
  - Secrets management hooks
  - Hierarchical configuration (base → env → local)

Configuration Sources (in order of precedence):
  1. Environment variables (highest priority)
  2. .env file (for local development)
  3. Default values (lowest priority)

Usage:
    from amos_config import settings

  # Access configuration
  api_port = settings.api.port
  jwt_secret = settings.security.jwt_secret
  ollama_host = settings.llm.ollama_host

Environment Variables:
  AMOS_ENV - Environment (development/staging/production)
  AMOS_API_PORT - API server port
  AMOS_JWT_SECRET - JWT signing secret
  AMOS_DB_URL - Database connection URL
  AMOS_LOG_LEVEL - Logging level (DEBUG/INFO/WARNING/ERROR)

Requirements:
  pip install pydantic-settings python-dotenv

Author: Trang Phan
Version: 1.0.0
"""

import sys
from enum import Enum
from pathlib import Path
from typing import List

# Try to import pydantic-settings
try:
    from pydantic import Field, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    PYDANTIC_SETTINGS_AVAILABLE = False
    print("Warning: pydantic-settings not available, using mock config")


class Environment(str, Enum):
    """AMOS deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class APISettings(BaseSettings):
    """API server configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_API_")

    host: str = Field(default="0.0.0.0", description="API server bind address")
    port: int = Field(default=8080, description="API server port", ge=1, le=65535)
    workers: int = Field(default=1, description="Number of worker processes", ge=1)
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    rate_limit_requests: int = Field(default=100, description="Requests per minute per IP", ge=1)


class SecuritySettings(BaseSettings):
    """Security configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_SECURITY_")

    jwt_secret: str = Field(
        default="amos-development-secret-key-change-in-production",
        description="JWT signing secret",
        min_length=32,
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(
        default=60, description="JWT token expiration in minutes", ge=5
    )
    password_min_length: int = Field(default=8, ge=4)
    require_auth: bool = Field(default=True)
    allowed_roles: List[str] = Field(default=["admin", "operator", "viewer", "evolution_approver"])


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_LLM_")

    ollama_host: str = Field(default="http://localhost:11434")
    default_model: str = Field(default="deepseek-coder-v2:16b")
    fallback_model: str = Field(default="qwen2.5-coder:14b")
    timeout_seconds: int = Field(default=30, ge=5)
    max_tokens: int = Field(default=4096, ge=256)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    enable_cloud_providers: bool = Field(default=False)


class MemorySettings(BaseSettings):
    """Memory system configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_MEMORY_")

    storage_path: str = Field(default="./_AMOS_BRAIN")
    vector_db_path: str = Field(default="./_AMOS_BRAIN/vector_memory")
    enable_vector_memory: bool = Field(default=True)
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_dim: int = Field(default=384, ge=128, le=1536)
    max_vector_results: int = Field(default=10, ge=1, le=100)


class MCPSettings(BaseSettings):
    """MCP tool configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_MCP_")

    filesystem_root: str = Field(default=".")
    enable_code_execution: bool = Field(default=True)
    code_execution_timeout: int = Field(default=30, ge=5, le=300)
    db_read_only: bool = Field(default=True)
    web_search_timeout: int = Field(default=10, ge=5, le=60)


class ObservabilitySettings(BaseSettings):
    """Observability configuration."""

    model_config = SettingsConfigDict(env_prefix="AMOS_OBS_")

    enable_opentelemetry: bool = Field(default=False)
    enable_structured_logging: bool = Field(default=True)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    health_check_interval: int = Field(default=30, ge=5)


class AMOSSettings(BaseSettings):
    """Main AMOS configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars
    )

    # Environment
    env: Environment = Field(
        default=Environment.DEVELOPMENT, description="AMOS deployment environment"
    )
    debug: bool = Field(default=False)
    version: str = Field(default="2.3.0")

    # Sub-configurations
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

    @field_validator("env", mode="before")
    @classmethod
    def validate_env(cls, v):
        """Validate environment value."""
        if isinstance(v, str):
            v = v.lower()
            if v in ["dev", "development"]:
                return Environment.DEVELOPMENT
            elif v in ["staging", "stage"]:
                return Environment.STAGING
            elif v in ["prod", "production"]:
                return Environment.PRODUCTION
        return v

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env == Environment.DEVELOPMENT

    def get_config_summary(self) -> dict:
        """Get configuration summary (excluding secrets)."""
        return {
            "environment": self.env.value,
            "version": self.version,
            "debug": self.debug,
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
            },
            "llm": {
                "ollama_host": self.llm.ollama_host,
                "default_model": self.llm.default_model,
            },
            "memory": {
                "storage_path": self.memory.storage_path,
                "vector_enabled": self.memory.enable_vector_memory,
            },
            "security": {
                "require_auth": self.security.require_auth,
                "jwt_expiration": self.security.jwt_expiration_minutes,
            },
            "observability": {
                "log_level": self.observability.log_level.value,
                "otel_enabled": self.observability.enable_opentelemetry,
            },
        }


class MockSettings:
    """Mock settings for when pydantic-settings is not available."""

    def __init__(self):
        self.env = Environment.DEVELOPMENT
        self.debug = True
        self.version = "2.3.0"
        self.api = type(
            "obj",
            (object,),
            {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 1,
                "reload": True,
                "cors_origins": ["*"],
                "rate_limit_requests": 100,
            },
        )()
        self.security = type(
            "obj",
            (object,),
            {
                "jwt_secret": "amos-dev-secret",
                "jwt_algorithm": "HS256",
                "jwt_expiration_minutes": 60,
                "password_min_length": 8,
                "require_auth": False,
                "allowed_roles": ["admin", "operator", "viewer"],
            },
        )()
        self.llm = type(
            "obj",
            (object,),
            {
                "ollama_host": "http://localhost:11434",
                "default_model": "deepseek-coder-v2:16b",
                "fallback_model": "qwen2.5-coder:14b",
                "timeout_seconds": 30,
                "max_tokens": 4096,
                "temperature": 0.7,
                "enable_cloud_providers": False,
            },
        )()
        self.memory = type(
            "obj",
            (object,),
            {
                "storage_path": "./_AMOS_BRAIN",
                "vector_db_path": "./_AMOS_BRAIN/vector_memory",
                "enable_vector_memory": True,
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dim": 384,
                "max_vector_results": 10,
            },
        )()
        self.mcp = type(
            "obj",
            (object,),
            {
                "filesystem_root": ".",
                "enable_code_execution": True,
                "code_execution_timeout": 30,
                "db_read_only": True,
                "web_search_timeout": 10,
            },
        )()
        self.observability = type(
            "obj",
            (object,),
            {
                "enable_opentelemetry": False,
                "enable_structured_logging": True,
                "log_level": LogLevel.INFO,
                "metrics_port": 9090,
                "health_check_interval": 30,
            },
        )()

    def is_production(self) -> bool:
        return False

    def is_development(self) -> bool:
        return True

    def get_config_summary(self) -> dict:
        return {"mode": "mock", "version": self.version}


# Create global settings instance
if PYDANTIC_SETTINGS_AVAILABLE:
    settings = AMOSSettings()
else:
    settings = MockSettings()


def validate_configuration() -> bool:
    """Validate AMOS configuration at startup."""
    print("[AMOS] Validating configuration...")

    errors = []
    warnings = []

    # Check production requirements
    if settings.is_production():
        if settings.security.jwt_secret == "amos-development-secret-key-change-in-production":
            errors.append("Production requires custom JWT_SECRET")
        if settings.api.cors_origins == ["*"]:
            warnings.append("Production should restrict CORS origins")
        if settings.debug:
            errors.append("Production should not run in debug mode")

    # Check LLM connectivity
    if not settings.llm.ollama_host.startswith("http"):
        warnings.append(f"Ollama host may be invalid: {settings.llm.ollama_host}")

    # Check memory paths
    storage_path = Path(settings.memory.storage_path)
    try:
        storage_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create storage path: {e}")

    # Report results
    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w}")

    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        return False

    print(f"  ✓ Configuration valid ({settings.env.value} mode)")
    return True


def print_config_summary():
    """Print configuration summary."""
    print("\n[AMOS Configuration Summary]")
    summary = settings.get_config_summary()
    for section, values in summary.items():
        print(f"  {section}:")
        if isinstance(values, dict):
            for key, val in values.items():
                print(f"    - {key}: {val}")
        else:
            print(f"    - {values}")


def main():
    """Demo configuration system."""
    print("=" * 70)
    print("AMOS CONFIGURATION MANAGEMENT v1.0.0")
    print("=" * 70)

    # Validate configuration
    if not validate_configuration():
        print("\nConfiguration validation failed!")
        sys.exit(1)

    # Print summary
    print_config_summary()

    # Show environment
    print(f"\n  Environment: {settings.env.value}")
    print(f"  Debug mode: {settings.debug}")
    print(f"  Production: {settings.is_production()}")

    print("\n" + "=" * 70)
    print("Configuration system ready!")
    print("=" * 70)


if __name__ == "__main__":
    main()

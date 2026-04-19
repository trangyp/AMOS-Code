"""Centralized configuration loader to fix hidden interface issues.

This module centralizes all environment variable access to resolve
the 'hidden_interfaces' architectural invariant failure.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


class Config:
    """Centralized configuration - single source of truth for all env vars."""

    # Server Configuration
    PORT: int = int(os.getenv("PORT", "5000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Domain
    DOMAIN: str = os.getenv("DOMAIN", "localhost")

    # Hostinger API
    HOSTINGER_API_KEY: str = os.getenv("HOSTINGER_API_KEY", "")
    HOSTINGER_DOMAIN: str = os.getenv("HOSTINGER_DOMAIN", "")

    # AMOS Brain Paths
    AMOS_BRAIN_PATH: Path = Path(os.getenv("AMOS_BRAIN_PATH", "/app/_AMOS_BRAIN"))
    AMOS_LOGS_PATH: Path = Path(os.getenv("AMOS_LOGS_PATH", "/app/logs"))
    AMOS_MEMORY_PATH: Path = Path(os.getenv("AMOS_MEMORY_PATH", "/app/memory"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))

    # External Services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///app/data/amos.db")

    # Monitoring
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export config as dictionary for debugging."""
        return {
            k: str(v) if isinstance(v, Path) else v
            for k, v in cls.__dict__.items()
            if not k.startswith("_") and k.isupper()
        }

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get config value by key."""
        return getattr(cls, key, default)


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get cached config instance (singleton)."""
    return Config()


# Convenience function for direct env access through centralized config
def env(key: str, default: str = "") -> str:
    """Get environment variable through centralized config.

    This replaces direct os.environ access to fix hidden interface issues.
    """
    return os.getenv(key, default)

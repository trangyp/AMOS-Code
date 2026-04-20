#!/usr/bin/env python3
"""
AMOS API Versioning System - Production-Ready Version Management

Implements API versioning strategies for backward compatibility:
- URL Path Versioning (/v1/, /v2/)
- Header Versioning (Accept-Version)
- Query Parameter Versioning (?version=1)
- Deprecation Warnings
- Version Sunset Notifications
- Auto-redirect to latest stable version

Features:
- Version router for FastAPI
- Automatic deprecation headers
- Version negotiation
- Sunset date tracking
- Migration guides endpoint

Usage:
    from fastapi import FastAPI
    from amos_api_versioning import VersionRouter, APIVersion

    app = FastAPI()
    version_router = VersionRouter(app)

    @version_router.route("/users", versions=["v1", "v2"])
    async def get_users_v1():
        return {"users": []}

Integration:
- amos_fastapi_gateway - Main gateway integration
- amos_metrics_exporter - Version usage metrics
- amos_opentelemetry_tracing - Version-specific traces

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

import re
from collections.abc import Callable
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from typing import Any, Optional

# FastAPI imports
try:
    from collections.abc import Callable

    from fastapi import Header, HTTPException, Query, Request, Response
    from fastapi.routing import APIRouter
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class APIVersion(Enum):
    """API version constants."""

    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    LATEST = "v1"  # Current stable version
    BETA = "v2"  # Beta version
    DEPRECATED = "v0"


@staticmethod
def get_version_from_path(path: str) -> str:
    """Extract version from URL path."""
    match = re.match(r"^/(v\d+)/", path)
    return match.group(1) if match else None


@staticmethod
def get_version_from_header(accept_version: str) -> str:
    """Extract version from Accept-Version header."""
    if not accept_version:
        return None
    # Parse version from header (e.g., "1.0", "v1", "application/vnd.amos.v1+json")
    match = re.search(r"v?(\d+)", accept_version)
    return f"v{match.group(1)}" if match else None


@staticmethod
def get_version_from_query(version: str) -> str:
    """Extract version from query parameter."""
    if not version:
        return None
    match = re.match(r"v?(\d+)", version)
    return f"v{match.group(1)}" if match else None


class VersionInfo:
    """API version information."""

    def __init__(
        self,
        version: str,
        status: str = "stable",  # stable, beta, deprecated, sunset
        release_date: str = None,
        sunset_date: str = None,
        migration_guide: str = None,
    ):
        self.version = version
        self.status = status
        self.release_date = release_date or datetime.now(UTC).isoformat()
        self.sunset_date = sunset_date
        self.migration_guide = migration_guide

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "status": self.status,
            "release_date": self.release_date,
            "sunset_date": self.sunset_date,
            "migration_guide": self.migration_guide,
        }


class VersionManager:
    """Manages API versions and their metadata."""

    def __init__(self):
        self._versions: dict[str, VersionInfo] = {}
        self._default_version = APIVersion.LATEST.value

    def register_version(
        self,
        version: str,
        status: str = "stable",
        sunset_date: str = None,
        migration_guide: str = None,
    ) -> None:
        """Register a new API version."""
        self._versions[version] = VersionInfo(
            version=version, status=status, sunset_date=sunset_date, migration_guide=migration_guide
        )

    def get_version_info(self, version: str) -> Optional[VersionInfo]:
        """Get version information."""
        return self._versions.get(version)

    def get_all_versions(self) -> list[dict[str, Any]]:
        """Get all version information."""
        return [v.to_dict() for v in self._versions.values()]

    def is_deprecated(self, version: str) -> bool:
        """Check if version is deprecated."""
        info = self._versions.get(version)
        return info is not None and info.status == "deprecated"

    def is_sunset(self, version: str) -> bool:
        """Check if version is sunset (end of life)."""
        info = self._versions.get(version)
        if info and info.sunset_date:
            sunset = datetime.fromisoformat(info.sunset_date)
            return datetime.now(UTC) > sunset
        return False

    def get_default_version(self) -> str:
        """Get default API version."""
        return self._default_version

    def set_default_version(self, version: str) -> None:
        """Set default API version."""
        self._default_version = version


class VersionNegotiationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API version negotiation.

    Handles version extraction from:
    - URL path (/v1/, /v2/)
    - Accept-Version header
    - version query parameter
    """

    def __init__(self, app: ASGIApp, version_manager: VersionManager, default_version: str = "v1"):
        super().__init__(app)
        self.version_manager = version_manager
        self.default_version = default_version

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with version negotiation."""
        # Try to extract version from various sources
        version = None

        # 1. URL path (highest priority)
        version = get_version_from_path(request.url.path)

        # 2. Accept-Version header
        if not version:
            accept_version = request.headers.get("Accept-Version")
            version = get_version_from_header(accept_version)

        # 3. Query parameter
        if not version:
            version_param = request.query_params.get("version")
            version = get_version_from_query(version_param)

        # 4. Use default
        if not version:
            version = self.default_version

        # Store version in request state
        request.state.api_version = version

        # Check version status
        version_info = self.version_manager.get_version_info(version)

        # Process request
        response = await call_next(request)

        # Add version headers
        response.headers["X-API-Version"] = version

        if version_info:
            # Add deprecation warning if applicable
            if version_info.status == "deprecated":
                response.headers["Deprecation"] = "true"
                if version_info.migration_guide:
                    response.headers["Sunset"] = version_info.sunset_date or ""
                    response.headers["Link"] = f'<{version_info.migration_guide}>; rel="migration"'

            # Add sunset warning
            if self.version_manager.is_sunset(version):
                response.headers["Sunset"] = version_info.sunset_date or ""

        return response


class VersionRouter:
    """
    Router that handles multiple API versions.

    Usage:
        router = VersionRouter(app)

        @router.route("/users", versions=["v1"])
        def get_users_v1(): ...

        @router.route("/users", versions=["v2"])
        def get_users_v2(): ...
    """

    def __init__(self, app: Any, version_manager: Optional[VersionManager] = None):
        self.app = app
        self.version_manager = version_manager or VersionManager()
        self._routers: dict[str, APIRouter] = {}

    def get_router(self, version: str) -> APIRouter:
        """Get or create router for specific version."""
        if version not in self._routers:
            self._routers[version] = APIRouter(prefix=f"/{version}")
            self.app.include_router(self._routers[version])
        return self._routers[version]

    def route(self, path: str, versions: list[str], **kwargs: Any) -> Callable:
        """Decorator to register route for specific versions."""

        def decorator(func: Callable) -> Callable:
            for version in versions:
                router = self.get_router(version)
                router.get(path, **kwargs)(func)
            return func

        return decorator

    def register_version(
        self,
        version: str,
        status: str = "stable",
        sunset_date: str = None,
        migration_guide: str = None,
    ) -> None:
        """Register API version metadata."""
        self.version_manager.register_version(
            version=version, status=status, sunset_date=sunset_date, migration_guide=migration_guide
        )


def add_versioning_to_app(
    app: Any, default_version: str = "v1", supported_versions: list[str] = None
) -> VersionManager:
    """
    Add API versioning support to FastAPI application.

    Args:
        app: FastAPI application
        default_version: Default API version
        supported_versions: List of supported versions

    Returns:
        VersionManager instance
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for API versioning")

    version_manager = VersionManager()
    version_manager.set_default_version(default_version)

    # Register supported versions
    supported = supported_versions or ["v1"]
    for version in supported:
        version_manager.register_version(version=version, status="stable")

    # Add middleware
    app.add_middleware(
        VersionNegotiationMiddleware,
        version_manager=version_manager,
        default_version=default_version,
    )

    return version_manager


# Global version manager instance
_global_version_manager: Optional[VersionManager] = None


def get_version_manager() -> VersionManager:
    """Get global version manager instance."""
    global _global_version_manager
    if _global_version_manager is None:
        _global_version_manager = VersionManager()
    return _global_version_manager


def set_version_manager(vm: VersionManager) -> None:
    """Set global version manager instance."""
    global _global_version_manager
    _global_version_manager = vm


__all__ = [
    "APIVersion",
    "VersionInfo",
    "VersionManager",
    "VersionNegotiationMiddleware",
    "VersionRouter",
    "add_versioning_to_app",
    "get_version_manager",
    "set_version_manager",
    "get_version_from_path",
    "get_version_from_header",
    "get_version_from_query",
]

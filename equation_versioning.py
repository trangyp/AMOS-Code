#!/usr/bin/env python3
"""AMOS Equation API Versioning - URL and Header-based API Version Management.

Production-grade API versioning with support for:
- URL path versioning (/api/v1/, /api/v2/)
- Header versioning (X-API-Version: 2024-01-15)
- Deprecation handling and sunset headers
- Version negotiation and migration helpers
- Backward compatibility checks

Versioning Strategy:
    - Major versions (v1, v2) for breaking changes
    - Date-based versions for continuous deployment
    - Sunset headers for deprecated versions
    - Grace period for migration

Endpoints:
    GET /api/versions - List available API versions
    GET /api/versions/current - Get current version info

Usage:
    from equation_versioning import VersionRouter
    router = VersionRouter()
    router.register_v1_routes(app)
    router.register_v2_routes(app)

Environment Variables:
    API_VERSION_DEFAULT: Default API version (default: v1)
    API_VERSION_SUNSET_DAYS: Days before version sunset (default: 180)
    API_DEPRECATION_WARNING: Enable deprecation warnings (default: true)
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from collections.abc import Callable
from enum import Enum
from typing import Any, Optional

# FastAPI imports with graceful fallback
try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.routing import APIRoute

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore
    Request = None  # type: ignore
    Response = None  # type: ignore
    HTTPException = None  # type: ignore
    APIRoute = None  # type: ignore

# Configuration
_DEFAULT_VERSION = os.getenv("API_VERSION_DEFAULT", "v1")
_SUNSET_DAYS = int(os.getenv("API_VERSION_SUNSET_DAYS", "180"))
_DEPRECATION_WARNING = os.getenv("API_DEPRECATION_WARNING", "true").lower() == "true"

# Version patterns
_SEMVER_PATTERN = re.compile(r"^v(\d+)$")
_DATE_PATTERN = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


class APIVersionStatus(Enum):
    """API version lifecycle status."""

    STABLE = "stable"
    BETA = "beta"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


class APIVersion:
    """Represents an API version with metadata."""

    def __init__(
        self,
        version: str,
        status: APIVersionStatus,
        release_date: datetime = None,
        sunset_date: datetime = None,
        changes: list[str] = None,
    ):
        self.version = version
        self.status = status
        self.release_date = release_date or datetime.now(timezone.utc)
        self.sunset_date = sunset_date
        self.changes = changes or []
        self.documentation_url: str = None
        self.migration_guide_url: str = None

    def is_deprecated(self) -> bool:
        """Check if version is deprecated."""
        return self.status in (APIVersionStatus.DEPRECATED, APIVersionStatus.SUNSET)

    def days_until_sunset(self) -> int:
        """Calculate days until version sunset."""
        if not self.sunset_date:
            return None
        delta = self.sunset_date - datetime.now(timezone.utc)
        return max(0, delta.days)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "status": self.status.value,
            "release_date": self.release_date.isoformat(),
            "sunset_date": (self.sunset_date.isoformat() if self.sunset_date else None),
            "days_until_sunset": self.days_until_sunset(),
            "changes": self.changes,
            "documentation_url": self.documentation_url,
            "migration_guide_url": self.migration_guide_url,
        }


class VersionRegistry:
    """Registry for managing API versions."""

    def __init__(self) -> None:
        self.versions: dict[str, APIVersion] = {}
        self.default_version = _DEFAULT_VERSION

    def register(
        self,
        version: str,
        status: APIVersionStatus = APIVersionStatus.STABLE,
        release_date: datetime = None,
        sunset_date: datetime = None,
        changes: list[str] = None,
    ) -> APIVersion:
        """Register a new API version.

        Args:
            version: Version string (e.g., "v1", "v2")
            status: Version lifecycle status
            release_date: Version release date
            sunset_date: Version sunset date
            changes: List of changes in this version

        Returns:
            Registered APIVersion instance
        """
        api_version = APIVersion(
            version=version,
            status=status,
            release_date=release_date,
            sunset_date=sunset_date,
            changes=changes,
        )
        self.versions[version] = api_version
        return api_version

    def deprecate(
        self,
        version: str,
        sunset_days: int = _SUNSET_DAYS,
        migration_guide: str = None,
    ) -> APIVersion:
        """Mark a version as deprecated.

        Args:
            version: Version to deprecate
            sunset_days: Days until version sunset
            migration_guide: URL to migration guide

        Returns:
            Updated APIVersion instance
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not registered")

        api_version = self.versions[version]
        api_version.status = APIVersionStatus.DEPRECATED
        api_version.sunset_date = datetime.now(timezone.utc) + timedelta(days=sunset_days)
        api_version.migration_guide_url = migration_guide

        return api_version

    def get(self, version: str) -> Optional[APIVersion]:
        """Get version metadata."""
        return self.versions.get(version)

    def get_default(self) -> APIVersion:
        """Get default version."""
        if self.default_version not in self.versions:
            # Auto-create default version
            return self.register(self.default_version)
        return self.versions[self.default_version]

    def list_active(self) -> list[APIVersion]:
        """List all active (non-sunset) versions."""
        return [v for v in self.versions.values() if v.status != APIVersionStatus.SUNSET]

    def parse_version(self, version_string: str) -> str:
        """Parse and normalize version string.

        Args:
            version_string: Version string from URL or header

        Returns:
            Normalized version string
        """
        # Handle semantic versions (v1, v2)
        if _SEMVER_PATTERN.match(version_string.lower()):
            return version_string.lower()

        # Handle date-based versions (2024-01-15)
        if _DATE_PATTERN.match(version_string):
            # Map date to nearest semantic version
            return self._map_date_to_semver(version_string)

        return self.default_version

    def _map_date_to_semver(self, date_string: str) -> str:
        """Map date-based version to semantic version."""
        # Simplified mapping - in production, use proper date comparison
        # Map to latest stable version
        stable_versions = [v for v in self.versions.values() if v.status == APIVersionStatus.STABLE]
        if stable_versions:
            return max(stable_versions, key=lambda v: v.release_date).version
        return self.default_version


class VersionRouter:
    """Router for handling versioned API endpoints."""

    def __init__(self, app: Optional[Any] = None) -> None:
        self.app = app
        self.registry = VersionRegistry()
        self.v1_routes: list[Callable] = []
        self.v2_routes: list[Callable] = []

        # Register default versions
        self._setup_default_versions()

    def _setup_default_versions(self) -> None:
        """Setup default API versions."""
        # V1 - Stable
        v1 = self.registry.register(
            version="v1",
            status=APIVersionStatus.STABLE,
            release_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            changes=["Initial API release"],
        )
        v1.documentation_url = "/docs/v1"

        # V2 - Beta (example)
        v2 = self.registry.register(
            version="v2",
            status=APIVersionStatus.BETA,
            release_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            changes=[
                "Added batch operations",
                "Improved error responses",
                "GraphQL support",
            ],
        )
        v2.documentation_url = "/docs/v2"

    def register_v1_routes(self, app: Any) -> None:
        """Register v1 API routes."""
        if not FASTAPI_AVAILABLE:
            return

        # Version info endpoint
        @app.get("/api/v1/versions")
        async def list_versions_v1() -> dict[str, Any]:
            """List available API versions (V1 format)."""
            return {
                "versions": [v.to_dict() for v in self.registry.list_active()],
                "current": self.registry.get_default().version,
            }

        @app.get("/api/v1/versions/current")
        async def current_version_v1() -> dict[str, Any]:
            """Get current version info (V1 format)."""
            current = self.registry.get_default()
            return {
                "version": current.version,
                "status": current.status.value,
                "documentation": current.documentation_url,
            }

    def register_v2_routes(self, app: Any) -> None:
        """Register v2 API routes."""
        if not FASTAPI_AVAILABLE:
            return

        # V2 has enhanced version information
        @app.get("/api/v2/versions")
        async def list_versions_v2() -> dict[str, Any]:
            """List available API versions (V2 format)."""
            versions = [
                {
                    **v.to_dict(),
                    "is_default": v.version == self.registry.default_version,
                    "is_deprecated": v.is_deprecated(),
                }
                for v in self.registry.list_active()
            ]

            return {
                "versions": versions,
                "current": self.registry.get_default().version,
                "recommended": self._get_recommended_version(),
            }

        @app.get("/api/v2/versions/current")
        async def current_version_v2() -> dict[str, Any]:
            """Get current version info (V2 format)."""
            current = self.registry.get_default()
            return {
                "version": current.version,
                "status": current.status.value,
                "documentation": current.documentation_url,
                "sunset_date": (current.sunset_date.isoformat() if current.sunset_date else None),
                "migration_guide": current.migration_guide_url,
            }

    def _get_recommended_version(self) -> str:
        """Get recommended version for new integrations."""
        stable = [v for v in self.registry.versions.values() if v.status == APIVersionStatus.STABLE]
        if stable:
            return max(stable, key=lambda v: v.release_date).version
        return self.registry.default_version


def get_version_middleware(registry: Optional[VersionRegistry] = None) -> Callable:
    """Create FastAPI middleware for version handling.

    Args:
        registry: Version registry instance

    Returns:
        ASGI middleware callable
    """
    if not FASTAPI_AVAILABLE:
        return lambda app: app

    if registry is None:
        registry = VersionRegistry()

    async def version_middleware(request: Request, call_next: Callable) -> Response:
        """Process request with version detection."""
        # Detect version from header
        version_header = request.headers.get("x-api-version")
        path_version = None

        # Extract version from URL path
        path = request.url.path
        if match := re.search(r"/api/(v\d+)/", path):
            path_version = match.group(1)

        # Parse version
        version_str = registry.parse_version(version_header or path_version or _DEFAULT_VERSION)
        version = registry.get(version_str)

        if not version:
            raise HTTPException(status_code=400, detail=f"Unknown API version: {version_str}")

        # Add version info to request state
        request.state.api_version = version

        # Process request
        response = await call_next(request)

        # Add deprecation headers if applicable
        if _DEPRECATION_WARNING and version.is_deprecated():
            response.headers["Deprecation"] = "true"
            if version.sunset_date:
                response.headers["Sunset"] = version.sunset_date.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )
            if version.migration_guide_url:
                response.headers["Link"] = (
                    f'<{version.migration_guide_url}>; rel="successor-version"'
                )

        # Add API version header
        response.headers["X-API-Version"] = version.version

        return response

    return version_middleware


def create_versioned_route(
    path: str,
    version: str,
    endpoint: Callable,
    methods: list[str] = None,
) -> APIRoute:
    """Create a versioned API route.

    Args:
        path: Route path pattern
        version: API version (e.g., "v1", "v2")
        endpoint: Route handler function
        methods: HTTP methods

    Returns:
        APIRoute instance
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI required for versioned routes")

    # Modify path to include version
    versioned_path = f"/api/{version}{path}"

    return APIRoute(
        path=versioned_path,
        endpoint=endpoint,
        methods=methods or ["GET"],
    )


def setup_versioning(app: Any, default_version: str = _DEFAULT_VERSION) -> VersionRouter:
    """Setup API versioning for a FastAPI application.

    Args:
        app: FastAPI application instance
        default_version: Default API version

    Returns:
        Configured VersionRouter instance
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI required for API versioning")

    router = VersionRouter(app)
    router.registry.default_version = default_version

    # Register version endpoints for all active versions
    router.register_v1_routes(app)
    router.register_v2_routes(app)

    # Add version middleware
    from fastapi.middleware.basehttp import BaseHTTPMiddleware

    class VersionMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            middleware = get_version_middleware(router.registry)
            return await middleware(request, call_next)

    app.add_middleware(VersionMiddleware)

    return router


# Global registry instance
_global_registry: Optional[VersionRegistry] = None


def get_global_registry() -> VersionRegistry:
    """Get or create global version registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = VersionRegistry()
        # Setup default versions
        VersionRouter()._setup_default_versions()
    return _global_registry


def get_version_info(version: str = None) -> dict[str, Any]:
    """Get version information.

    Args:
        version: Specific version to query, or None for default

    Returns:
        Version information dictionary
    """
    registry = get_global_registry()

    if version:
        v = registry.get(version)
        if v:
            return v.to_dict()
        return {"error": f"Version {version} not found"}

    return registry.get_default().to_dict()


def is_version_deprecated(version: str) -> bool:
    """Check if a version is deprecated.

    Args:
        version: Version string to check

    Returns:
        True if version is deprecated
    """
    registry = get_global_registry()
    v = registry.get(version)
    if v:
        return v.is_deprecated()
    return False

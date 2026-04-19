"""AMOS API Versioning System.

Provides API versioning, deprecation warnings, and backward compatibility.
Ensures smooth API evolution without breaking existing clients.

Features:
- URL-based versioning (/api/v1/, /api/v2/)
- Header-based version negotiation
- Deprecation warnings with sunset dates
- Backward compatibility layer
- Version migration guides

Creator: Trang Phan
Version: 3.0.0
"""


from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional

from fastapi import Header, HTTPException, Request
from pydantic import BaseModel

# API Version Configuration
CURRENT_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1"]
DEPRECATED_VERSIONS: Dict[str, dict[str, Any]] = {}
SUNSET_NOTICE_DAYS = 90  # Days before deprecated version is removed


class VersionInfo(BaseModel):
    """API version information."""

    version: str
    status: str  # "current", "deprecated", "sunset"
    sunset_date: str = None
    documentation_url: str
    migration_guide_url: str = None
    deprecated_fields: list = []
    new_features: list = []
    breaking_changes: list = []


class DeprecationInfo:
    """Information about deprecated endpoints or fields."""

    def __init__(
        self,
        deprecated_since: str,
        sunset_date: str,
        alternative_endpoint: str = None,
        alternative_field: str = None,
        migration_guide: str = None,
    ):
        self.deprecated_since = deprecated_since
        self.sunset_date = sunset_date
        self.alternative_endpoint = alternative_endpoint
        self.alternative_field = alternative_field
        self.migration_guide = migration_guide


# Version registry
VERSION_REGISTRY: Dict[str, VersionInfo] = {
    "v1": VersionInfo(
        version="v1",
        status="current",
        documentation_url="/docs",
        new_features=[
            "Complete AMOS Brain API",
            "Authentication with JWT/OAuth2",
            "52 endpoints",
            "WebSocket support",
        ],
    )
}


def get_version_info(version: str) -> Optional[VersionInfo]:
    """Get version information."""
    return VERSION_REGISTRY.get(version)


def check_version_support(version: str) -> bool:
    """Check if API version is supported."""
    return version in SUPPORTED_VERSIONS


def add_deprecation_headers(response: Any, deprecation_info: DeprecationInfo) -> Any:
    """Add deprecation headers to response."""
    response.headers["Deprecation"] = f"@ {deprecation_info.deprecated_since}"
    response.headers["Sunset"] = deprecation_info.sunset_date

    if deprecation_info.alternative_endpoint:
        response.headers["Link"] = (
            f"<{deprecation_info.alternative_endpoint}>; " 'rel="successor-version"'
        )

    return response


def deprecated_endpoint(
    deprecated_since: str,
    sunset_date: str,
    alternative_endpoint: str = None,
    migration_guide: str = None,
):
    """Decorator to mark endpoint as deprecated."""
    deprecation_info = DeprecationInfo(
        deprecated_since=deprecated_since,
        sunset_date=sunset_date,
        alternative_endpoint=alternative_endpoint,
        migration_guide=migration_guide,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the function
            response = await func(*args, **kwargs)

            # Add deprecation headers
            if hasattr(response, "headers"):
                response = add_deprecation_headers(response, deprecation_info)

            return response

        # Mark function as deprecated
        wrapper._is_deprecated = True  # type: ignore
        wrapper._deprecation_info = deprecation_info  # type: ignore

        return wrapper

    return decorator


def versioned_api(
    version: str = CURRENT_VERSION,
    deprecated: bool = False,
    deprecation_info: Optional[DeprecationInfo] = None,
):
    """Decorator to mark API endpoint with version info."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check version support
            if not check_version_support(version):
                raise HTTPException(
                    status_code=404,
                    detail=f"API version '{version}' is not supported. "
                    f"Supported versions: {', '.join(SUPPORTED_VERSIONS)}",
                )

            # Execute the function
            response = await func(*args, **kwargs)

            # Add version headers
            if hasattr(response, "headers"):
                response.headers["API-Version"] = version

                if deprecated and deprecation_info:
                    response = add_deprecation_headers(response, deprecation_info)

            return response

        # Store version info
        wrapper._api_version = version  # type: ignore
        wrapper._is_deprecated = deprecated  # type: ignore

        return wrapper

    return decorator


class APIVersionManager:
    """Manager for API versioning."""

    def __init__(self):
        self.versions = VERSION_REGISTRY.copy()
        self.deprecated_endpoints: Dict[str, DeprecationInfo] = {}

    def register_version(self, version_info: VersionInfo) -> None:
        """Register a new API version."""
        self.versions[version_info.version] = version_info
        if version_info.version not in SUPPORTED_VERSIONS:
            SUPPORTED_VERSIONS.append(version_info.version)

    def deprecate_version(self, version: str, sunset_date: str = None) -> None:
        """Mark a version as deprecated."""
        if version not in self.versions:
            raise ValueError(f"Version '{version}' not found")

        if sunset_date is None:
            # Calculate sunset date
            sunset = datetime.now() + timedelta(days=SUNSET_NOTICE_DAYS)
            sunset_date = sunset.isoformat()

        self.versions[version].status = "deprecated"
        self.versions[version].sunset_date = sunset_date

        # Remove from supported versions
        if version in SUPPORTED_VERSIONS:
            SUPPORTED_VERSIONS.remove(version)

    def get_versions(self) -> Dict[str, VersionInfo]:
        """Get all registered versions."""
        return self.versions

    def get_current_version(self) -> str:
        """Get current API version."""
        return CURRENT_VERSION

    def check_endpoint_deprecated(self, endpoint: str) -> Optional[DeprecationInfo]:
        """Check if endpoint is deprecated."""
        return self.deprecated_endpoints.get(endpoint)


# Global version manager
version_manager = APIVersionManager()


def get_api_version_from_request(
    request: Request, api_version: str = Header(None, alias="X-API-Version")
) -> str:
    """Extract API version from request URL or header."""
    # Check URL path
    path = request.url.path
    if "/api/v" in path:
        # Extract version from URL (e.g., /api/v1/...)
        parts = path.split("/")
        for part in parts:
            if part.startswith("v") and part[1:].isdigit():
                return part

    # Check header
    if api_version:
        return api_version

    # Default to current version
    return CURRENT_VERSION


# Version response models
class VersionListResponse(BaseModel):
    """Response for version list endpoint."""

    current_version: str
    supported_versions: list
    versions: Dict[str, VersionInfo]


class DeprecationNoticeResponse(BaseModel):
    """Deprecation notice response."""

    endpoint: str
    deprecated_since: str
    sunset_date: str
    alternative: str = None
    migration_guide: str = None
    message: str

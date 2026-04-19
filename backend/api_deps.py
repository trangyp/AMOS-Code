"""AMOS API Dependencies

Shared dependencies for API endpoints including authentication,
database connections, and service instances.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations


from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Import AMOS authentication system
try:
    from equation_auth import verify_token

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    verify_token = None

# Import AMOS database system
try:
    from backend.database_pool import get_db_session as _get_db_session

    DB_AVAILABLE = True
except ImportError:
    try:
        from amos_db_sqlalchemy import get_db_session as _get_db_session

        DB_AVAILABLE = True
    except ImportError:
        DB_AVAILABLE = False
        _get_db_session = None

# Security setup
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """
    Get current authenticated user from JWT token.

    Uses equation_auth.verify_token() for JWT validation.
    Falls back to mock user if auth system unavailable.
    """
    if not credentials:
        # Allow anonymous access for development
        return {"id": "anonymous", "role": "user"}

    if not AUTH_AVAILABLE or not verify_token:
        # Auth system not available, return mock admin
        return {"id": "user-1", "role": "admin"}

    # Validate JWT token
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return {
        "id": payload.get("sub", "unknown"),
        "role": payload.get("role", "user"),
        "email": payload.get("email"),
        "permissions": payload.get("permissions", []),
    }


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for sensitive operations."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


# Database dependency
async def get_db() -> AsyncGenerator:
    """
    Get database session.

    Uses backend.database_pool or amos_db_sqlalchemy for session management.
    Falls back to None if database unavailable.
    """
    if not DB_AVAILABLE or not _get_db_session:
        # Database not available
        yield None
        return

    # Get database session from AMOS database system
    async for session in _get_db_session():
        try:
            yield session
        finally:
            # Session cleanup handled by context manager
            pass

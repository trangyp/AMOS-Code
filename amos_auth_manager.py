#!/usr/bin/env python3
from __future__ import annotations

"""AMOS Authentication Manager - Enterprise Security (Phase 13)
==================================================================

Enterprise-grade authentication and authorization system for AMOS.
Implements JWT tokens, API keys, RBAC, rate limiting, and audit logging.

Features:
- JWT Token Authentication (OAuth2 compatible)
- API Key Management (create, revoke, rotate)
- Role-Based Access Control (RBAC)
- Rate Limiting (per-key, per-IP)
- Audit Logging (security events)
- Token Refresh (sliding expiration)

Architecture Pattern: FastAPI OAuth2 + RBAC + RateLimit
Based on: FastAPI Security Best Practices 2024

Owner: Trang
Version: 1.0.0
Phase: 13
"""


import hashlib
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timedelta, timezone

UTC = UTC
from enum import Enum
from functools import wraps
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, HTTPBearer

# Optional imports
try:
    from jose import JWTError, jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("python-jose not installed. JWT features disabled.")

try:
    from passlib.context import CryptContext

    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    print("passlib not installed. Password hashing disabled.")

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False
    print("slowapi not installed. Rate limiting disabled.")

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
API_KEY_PREFIX = "amos_"


class UserRole(Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"
    READONLY = "readonly"


class Permission(Enum):
    """Permissions for fine-grained access control."""

    # Runtime permissions
    RUNTIME_READ = "runtime:read"
    RUNTIME_CONTROL = "runtime:control"

    # Equation permissions
    EQUATION_READ = "equation:read"
    EQUATION_EXECUTE = "equation:execute"

    # Health permissions
    HEALTH_READ = "health:read"
    HEALTH_ADMIN = "health:admin"

    # Self-healing permissions
    SELFHEAL_READ = "selfheal:read"
    SELFHEAL_CONTROL = "selfheal:control"

    # API key management
    APIKEY_CREATE = "apikey:create"
    APIKEY_REVOKE = "apikey:revoke"

    # Admin permissions
    ADMIN_FULL = "admin:full"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.ADMIN_FULL,
        Permission.RUNTIME_CONTROL,
        Permission.EQUATION_EXECUTE,
        Permission.SELFHEAL_CONTROL,
        Permission.APIKEY_CREATE,
        Permission.APIKEY_REVOKE,
    ],
    UserRole.USER: [
        Permission.RUNTIME_READ,
        Permission.EQUATION_READ,
        Permission.EQUATION_EXECUTE,
        Permission.HEALTH_READ,
        Permission.SELFHEAL_READ,
    ],
    UserRole.SERVICE: [
        Permission.RUNTIME_READ,
        Permission.EQUATION_READ,
        Permission.EQUATION_EXECUTE,
        Permission.HEALTH_READ,
    ],
    UserRole.READONLY: [
        Permission.RUNTIME_READ,
        Permission.EQUATION_READ,
        Permission.HEALTH_READ,
        Permission.SELFHEAL_READ,
    ],
}


@dataclass
class APIKey:
    """API key data model."""

    key_id: str
    hashed_key: str
    name: str
    owner: str
    role: UserRole
    created_at: datetime
    expires_at: datetime = None
    last_used: datetime = None
    is_active: bool = True
    rate_limit: int = 1000  # requests per hour
    permissions: list[str] = field(default_factory=list)


@dataclass
class TokenData:
    """JWT token payload."""

    sub: str  # user id
    username: str
    role: str
    permissions: list[str]
    iat: float  # issued at
    exp: float  # expiration
    jti: str  # unique token id


@dataclass
class AuditEvent:
    """Security audit event."""

    event_type: str
    timestamp: datetime
    user_id: str = None
    api_key_id: str = None
    ip_address: str = None
    user_agent: str = None
    resource: str = None
    action: str = None
    success: bool = True
    details: dict[str, Any] = field(default_factory=dict)


class AMOSAuthManager:
    """
    AMOS Authentication and Authorization Manager.

    Handles JWT tokens, API keys, RBAC, and audit logging.
    """

    def __init__(self):
        self._api_keys: dict[str, APIKey] = {}  # key_id -> APIKey
        self._key_lookup: dict[str, str] = {}  # hashed_key -> key_id
        self._audit_log: list[AuditEvent] = []
        self._token_blacklist: Set[str] = set()  # revoked token jtis
        self._rate_limit_store: dict[str, list[float]] = {}  # key -> timestamps

        if PASSLIB_AVAILABLE:
            self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            self._pwd_context = None

        logger.info("AMOS Auth Manager initialized (Phase 13)")

    # ============================================
    # JWT Token Methods
    # ============================================

    def create_access_token(
        self, username: str, user_id: str, role: UserRole, expires_delta: timedelta = None
    ) -> str:
        """Create a JWT access token."""
        if not JWT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="JWT not available. Install python-jose.",
            )

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        permissions = [p.value for p in ROLE_PERMISSIONS.get(role, [])]

        token_data = {
            "sub": user_id,
            "username": username,
            "role": role.value,
            "permissions": permissions,
            "iat": datetime.now(timezone.utc).timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(16),
            "type": "access",
        }

        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        self._log_audit(
            event_type="token_created",
            user_id=user_id,
            details={"token_type": "access", "expires": expire.isoformat()},
        )

        return token

    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token."""
        if not JWT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="JWT not available. Install python-jose.",
            )

        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        token_data = {
            "sub": user_id,
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(16),
            "type": "refresh",
        }

        return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token."""
        if not JWT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="JWT not available. Install python-jose.",
            )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check if token is blacklisted
            if payload.get("jti") in self._token_blacklist:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked"
                )

            return TokenData(
                sub=payload["sub"],
                username=payload["username"],
                role=payload["role"],
                permissions=payload.get("permissions", []),
                iat=payload["iat"],
                exp=payload["exp"],
                jti=payload["jti"],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def revoke_token(self, token: str) -> None:
        """Revoke a JWT token (add to blacklist)."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            self._token_blacklist.add(payload["jti"])

            self._log_audit(
                event_type="token_revoked",
                user_id=payload.get("sub"),
                details={"jti": payload["jti"]},
            )
        except JWTError:
            pass  # Token is already invalid

    # ============================================
    # API Key Methods
    # ============================================

    def create_api_key(
        self,
        name: str,
        owner: str,
        role: UserRole = UserRole.SERVICE,
        expires_days: int = None,
        rate_limit: int = 1000,
    ) -> Tuple[str, APIKey]:
        """
        Create a new API key.

        Returns:
            Tuple of (raw_key, APIKey metadata)
        """
        # Generate key
        raw_key = f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"
        hashed_key = self._hash_key(raw_key)
        key_id = secrets.token_hex(8)

        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

        # Create API key record
        api_key = APIKey(
            key_id=key_id,
            hashed_key=hashed_key,
            name=name,
            owner=owner,
            role=role,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            rate_limit=rate_limit,
            permissions=[p.value for p in ROLE_PERMISSIONS.get(role, [])],
        )

        # Store
        self._api_keys[key_id] = api_key
        self._key_lookup[hashed_key] = key_id

        self._log_audit(
            event_type="apikey_created",
            user_id=owner,
            details={"key_id": key_id, "name": name, "role": role.value},
        )

        return raw_key, api_key

    def verify_api_key(self, raw_key: str) -> APIKey:
        """Verify an API key and return its metadata."""
        hashed_key = self._hash_key(raw_key)
        key_id = self._key_lookup.get(hashed_key)

        if not key_id:
            self._log_audit(event_type="apikey_verify_failed", details={"reason": "key_not_found"})
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

        api_key = self._api_keys[key_id]

        # Check if active
        if not api_key.is_active:
            self._log_audit(
                event_type="apikey_verify_failed",
                api_key_id=key_id,
                details={"reason": "key_inactive"},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="API key has been revoked"
            )

        # Check expiration
        if api_key.expires_at and datetime.now(timezone.utc) > api_key.expires_at:
            self._log_audit(
                event_type="apikey_verify_failed",
                api_key_id=key_id,
                details={"reason": "key_expired"},
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key has expired")

        # Update last used
        api_key.last_used = datetime.now(timezone.utc)

        self._log_audit(
            event_type="apikey_verify_success", api_key_id=key_id, details={"name": api_key.name}
        )

        return api_key

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id not in self._api_keys:
            return False

        api_key = self._api_keys[key_id]
        api_key.is_active = False

        # Remove from lookup
        if api_key.hashed_key in self._key_lookup:
            del self._key_lookup[api_key.hashed_key]

        self._log_audit(
            event_type="apikey_revoked", api_key_id=key_id, details={"name": api_key.name}
        )

        return True

    def list_api_keys(self, owner: str = None) -> list[APIKey]:
        """List API keys, optionally filtered by owner."""
        keys = list(self._api_keys.values())
        if owner:
            keys = [k for k in keys if k.owner == owner]
        return keys

    def _hash_key(self, raw_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    # ============================================
    # RBAC Methods
    # ============================================

    def has_permission(self, token_data: TokenData, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return (
            Permission.ADMIN_FULL.value in token_data.permissions
            or permission.value in token_data.permissions
        )

    def has_role(self, token_data: TokenData, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return token_data.role == role.value

    def require_permission(self, permission: Permission):
        """Dependency to require a specific permission."""

        def checker(token_data: TokenData = Depends(self.get_current_user)):
            if not self.has_permission(token_data, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission.value} required",
                )
            return token_data

        return checker

    # ============================================
    # Rate Limiting
    # ============================================

    def check_rate_limit(self, key: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        window_start = now - window_seconds

        # Get requests in window
        requests = self._rate_limit_store.get(key, [])
        requests = [t for t in requests if t > window_start]

        # Check limit
        if len(requests) >= limit:
            return False

        # Add current request
        requests.append(now)
        self._rate_limit_store[key] = requests

        return True

    def get_rate_limit_status(self, key: str, limit: int, window_seconds: int = 3600) -> dict:
        """Get current rate limit status."""
        now = time.time()
        window_start = now - window_seconds

        requests = self._rate_limit_store.get(key, [])
        requests_in_window = [t for t in requests if t > window_start]

        return {
            "limit": limit,
            "remaining": max(0, limit - len(requests_in_window)),
            "reset": int(window_start + window_seconds),
            "window": window_seconds,
        }

    # ============================================
    # Audit Logging
    # ============================================

    def _log_audit(self, **kwargs) -> None:
        """Log a security audit event."""
        event = AuditEvent(timestamp=datetime.now(timezone.utc), **kwargs)
        self._audit_log.append(event)

        # Log to standard logger
        logger.info(f"Security event: {event.event_type} - {event.details}")

    def get_audit_log(
        self, user_id: str = None, event_type: str = None, since: datetime = None, limit: int = 100
    ) -> list[AuditEvent]:
        """Query audit log with filters."""
        events = self._audit_log

        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]

        # Return most recent first
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    # ============================================
    # FastAPI Dependencies
    # ============================================

    async def get_current_user(self, token: str = Depends(HTTPBearer())) -> TokenData:
        """FastAPI dependency to get current authenticated user."""
        return self.verify_token(token)

    async def get_current_user_optional(
        self, token: str = Depends(HTTPBearer(auto_error=False))
    ) -> TokenData:
        """FastAPI dependency to get current user (optional)."""
        if not token:
            return None
        try:
            return self.verify_token(token)
        except HTTPException:
            return None

    async def verify_api_key_dependency(
        self,
        request: Request,
        api_key: str = Depends(APIKeyHeader(name="X-API-Key", auto_error=False)),
    ) -> APIKey:
        """FastAPI dependency to verify API key."""
        if not api_key:
            return None

        try:
            key_data = self.verify_api_key(api_key)

            # Check rate limit
            if not self.check_rate_limit(key_data.key_id, key_data.rate_limit):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
                )

            # Log request
            self._log_audit(
                event_type="api_request",
                api_key_id=key_data.key_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                resource=str(request.url.path),
                action=request.method,
            )

            return key_data
        except HTTPException:
            return None


# Global auth manager instance
_auth_manager: AMOSAuthManager = None


def get_auth_manager() -> AMOSAuthManager:
    """Get or create global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AMOSAuthManager()
    return _auth_manager


# ============================================
# Convenience decorators
# ============================================


def require_auth(permission: Permission = None):
    """Decorator to require authentication for a route."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            auth_manager = get_auth_manager()

            # Get token from kwargs or args
            token_data = kwargs.get("current_user")
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
                )

            # Check permission if specified
            if permission and not auth_manager.has_permission(token_data, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission.value}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================
# Example usage
# ============================================

if __name__ == "__main__":
    print("AMOS Auth Manager - Phase 13")
    print("=" * 60)

    # Initialize auth manager
    auth = get_auth_manager()

    # Create API key
    raw_key, api_key = auth.create_api_key(
        name="Test Key", owner="admin", role=UserRole.SERVICE, expires_days=30
    )

    print(f"\n✅ Created API key: {raw_key[:20]}...")
    print(f"   Key ID: {api_key.key_id}")
    print(f"   Role: {api_key.role.value}")
    print(f"   Permissions: {len(api_key.permissions)}")

    # Verify API key
    verified = auth.verify_api_key(raw_key)
    print(f"\n✅ Verified API key: {verified.name}")

    # Create JWT token
    if JWT_AVAILABLE:
        token = auth.create_access_token(username="admin", user_id="user_123", role=UserRole.ADMIN)
        print(f"\n✅ Created JWT token: {token[:50]}...")

        # Verify token
        token_data = auth.verify_token(token)
        print(f"   User: {token_data.username}")
        print(f"   Role: {token_data.role}")
        print(f"   Permissions: {len(token_data.permissions)}")

    print("\n" + "=" * 60)
    print("✅ AMOS Auth Manager operational!")

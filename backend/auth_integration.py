"""AMOS Authentication Integration for FastAPI

Integrates the AMOS auth system with FastAPI endpoints.
Provides JWT token validation, RBAC authorization, and OAuth2 flows.

Creator: Trang Phan
Version: 3.0.0
"""

import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access",
    },
)


# Mock user database (replace with database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@amos.local",
        "hashed_password": pwd_context.hash("admin123"),  # Change in production!
        "roles": ["admin"],
        "permissions": ["read", "write", "admin"],
        "disabled": False,
    },
    "user": {
        "username": "user",
        "email": "user@amos.local",
        "hashed_password": pwd_context.hash("user123"),  # Change in production!
        "roles": ["user"],
        "permissions": ["read"],
        "disabled": False,
    },
}


class TokenData:
    """Token data model."""

    def __init__(self, username: str = None, scopes: list[str] = None):
        self.username = username
        self.scopes = scopes or []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def get_user(username: str) -> dict[str, Any]:
    """Get user from database."""
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> dict[str, Any]:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(username: str) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": username, "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception

    if user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get current active user."""
    if current_user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_scope(scope: str):
    """Decorator to require a specific scope/permission."""

    async def check_scope(
        current_user: dict[str, Any] = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        if scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {scope}",
            )
        return current_user

    return check_scope


# Role-based access control
ROLES = {
    "admin": {
        "permissions": ["read", "write", "admin", "delete", "manage_users"],
        "description": "Administrator with full access",
    },
    "user": {
        "permissions": ["read", "write"],
        "description": "Standard user with read/write access",
    },
    "readonly": {"permissions": ["read"], "description": "Read-only access"},
}


def check_permission(user: dict[str, Any], permission: str) -> bool:
    """Check if user has a specific permission."""
    user_permissions = user.get("permissions", [])
    return permission in user_permissions


async def require_admin(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    """Require admin role."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# API Key authentication for service-to-service
API_KEYS = {
    "amos-internal": {
        "key": os.getenv("INTERNAL_API_KEY", "internal-secret-key"),
        "name": "AMOS Internal Service",
        "permissions": ["read", "write", "internal"],
    }
}


def verify_api_key(api_key: str) -> dict[str, Any]:
    """Verify an API key."""
    for service_id, service_data in API_KEYS.items():
        if service_data["key"] == api_key:
            return {
                "service_id": service_id,
                "name": service_data["name"],
                "permissions": service_data["permissions"],
            }
    return None

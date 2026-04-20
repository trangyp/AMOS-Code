"""AMOS Authentication Integration for FastAPI

Integrates the AMOS auth system with FastAPI endpoints.
Provides JWT token validation, RBAC authorization, and OAuth2 flows.
Uses real database-backed authentication via AMOSDatabase.

Creator: Trang Phan
Version: 4.0.0
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import real database
try:
    from amos_db_sqlalchemy import SQLALCHEMY_AVAILABLE, AMOSDatabase, User

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    SQLALCHEMY_AVAILABLE = False

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

# Global database instance
_db_instance: AMOSDatabase = None


def get_database() -> AMOSDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None and DATABASE_AVAILABLE:
        _db_instance = AMOSDatabase()
    return _db_instance


async def init_auth_database() -> bool:
    """Initialize the authentication database."""
    db = get_database()
    if db:
        try:
            await db.initialize()
            return True
        except Exception as e:
            print(f"[Auth] Database initialization failed: {e}")
            return False
    return False


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


async def get_user(username: str) -> dict[str, Any]:
    """Get user from database."""
    db = get_database()
    if db and DATABASE_AVAILABLE:
        try:
            user = await db.get_user_by_username(username)
            if user:
                return {
                    "username": user.username,
                    "email": user.email,
                    "hashed_password": user.hashed_password or "",
                    "roles": ["admin"] if user.is_superuser else [user.role],
                    "permissions": ["read", "write", "admin"]
                    if user.is_superuser
                    else ["read", "write"]
                    if user.role != "readonly"
                    else ["read"],
                    "disabled": not user.is_active,
                }
        except Exception as e:
            print(f"[Auth] Database error getting user: {e}")
    return None


async def authenticate_user(username: str, password: str) -> dict[str, Any]:
    """Authenticate a user."""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    utc = UTC

    if expires_delta:
        expire = datetime.now(utc) + expires_delta
    else:
        expire = datetime.now(utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(username: str) -> str:
    """Create a JWT refresh token."""
    utc = UTC
    expire = datetime.now(utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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

    user = await get_user(token_data.username)
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


# API Key authentication for service-to-service - uses database API keys
async def verify_api_key(api_key: str) -> dict[str, Any]:
    """Verify an API key against database."""
    db = get_database()
    if db and DATABASE_AVAILABLE:
        try:
            # Hash the provided key and look it up
            import hashlib

            from amos_db_sqlalchemy import APIKey

            hashed = hashlib.sha256(api_key.encode()).hexdigest()

            async with db.session() as session:
                from sqlalchemy import select

                result = await session.execute(
                    select(APIKey).where(APIKey.hashed_key == hashed, APIKey.is_active == True)
                )
                key_record = result.scalar_one_or_none()
                if key_record:
                    return {
                        "service_id": key_record.key_id,
                        "name": key_record.name,
                        "permissions": key_record.permissions or ["read", "write"],
                    }
        except Exception as e:
            print(f"[Auth] API key verification error: {e}")

    # Fallback to environment-based key for bootstrapping
    internal_key = os.getenv("INTERNAL_API_KEY")
    if internal_key and api_key == internal_key:
        return {
            "service_id": "amos-internal",
            "name": "AMOS Internal Service",
            "permissions": ["read", "write", "internal"],
        }
    return None

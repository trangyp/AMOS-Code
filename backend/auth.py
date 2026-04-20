"""
AMOS Authentication Module

JWT-based authentication and authorization for the AMOS API.
Implements secure token handling with proper validation.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
UTC = timezone.utc, timedelta, timezone

UTC = UTC
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "amos-development-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str = None


class TokenData(BaseModel):
    """Token payload data."""

    username: str = None
    user_id: str = None
    permissions: list[str] = []


class User(BaseModel):
    """User model."""

    id: str
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = False
    permissions: list[str] = []


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


# In-memory user database (replace with real DB in production)
# Pre-hashed password: "amos-demo-password"
DEMO_USERS = {
    "admin": UserInDB(
        id="user-001",
        username="admin",
        email="admin@amos.dev",
        full_name="AMOS Administrator",
        hashed_password=pwd_context.hash("amos-demo-password"),
        permissions=["read", "write", "admin"],
    ),
    "developer": UserInDB(
        id="user-002",
        username="developer",
        email="dev@amos.dev",
        full_name="AMOS Developer",
        hashed_password=pwd_context.hash("amos-demo-password"),
        permissions=["read", "write"],
    ),
    "viewer": UserInDB(
        id="user-003",
        username="viewer",
        email="viewer@amos.dev",
        full_name="AMOS Viewer",
        hashed_password=pwd_context.hash("amos-demo-password"),
        permissions=["read"],
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB:
    """Retrieve user from database."""
    return DEMO_USERS.get(username)


def authenticate_user(username: str, password: str) -> UserInDB:
    """Authenticate user with username and password."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from token."""
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Check token type
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check expiration
    exp = payload.get("exp")
    if exp is None or datetime.now(timezone.utc) > datetime.fromtimestamp(exp):
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        permissions=user.permissions,
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


class PermissionChecker:
    """Check if user has required permissions."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        for permission in self.required_permissions:
            if permission not in user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}",
                )
        return user


# Permission dependencies
require_admin = PermissionChecker(["admin"])
require_write = PermissionChecker(["write"])
require_read = PermissionChecker(["read"])


# Rate limiting configuration for authenticated users
AUTH_RATE_LIMIT = "100/minute"
ANON_RATE_LIMIT = "20/minute"

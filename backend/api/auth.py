"""AMOS Authentication API Endpoints

Provides OAuth2/JWT authentication endpoints.

Creator: Trang Phan
Version: 3.0.0
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from amos_auth_integration import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    USERS_DB,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    require_admin,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    OAuth2 login endpoint.

    Returns JWT access token and refresh token.

    Example:
    ```
    POST /api/v1/auth/login
    username=admin&password=admin123
    ```
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "scopes": user.get("permissions", []),
            "roles": user.get("roles", []),
        },
        expires_delta=access_token_expires,
    )

    refresh_token = create_refresh_token(user["username"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "roles": user.get("roles", []),
            "permissions": user.get("permissions", []),
        },
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.

    Returns new access token.
    """
    from auth_integration import ALGORITHM, SECRET_KEY, jwt

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "scopes": user.get("permissions", []),
            "roles": user.get("roles", []),
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: Annotated[dict, Depends(get_current_active_user)]):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "roles": current_user.get("roles", []),
        "permissions": current_user.get("permissions", []),
        "disabled": current_user.get("disabled", False),
    }


@router.post("/logout", response_model=dict)
async def logout():
    """
    Logout endpoint.

    Note: JWT tokens cannot be truly revoked server-side without a blacklist.
    Clients should discard their tokens.
    """
    return {"message": "Successfully logged out. Please discard your tokens."}


@router.get("/users", response_model=dict)
async def list_users(current_user: Annotated[dict, Depends(require_admin)]):
    """
    List all users (admin only).
    """
    users = []
    for username, user_data in USERS_DB.items():
        users.append(
            {
                "username": username,
                "email": user_data["email"],
                "roles": user_data.get("roles", []),
                "disabled": user_data.get("disabled", False),
            }
        )

    return {"users": users}


@router.get("/health", response_model=dict)
async def auth_health():
    """
    Authentication service health check.
    """
    return {
        "status": "healthy",
        "auth_type": "JWT/OAuth2",
        "algorithm": "HS256",
        "users_count": len(USERS_DB),
    }

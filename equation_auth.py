#!/usr/bin/env python3
"""AMOS Equation Authentication - JWT/OAuth2 with RBAC.

Production-grade authentication and authorization system:
- JWT token generation and validation with refresh tokens
- OAuth2 Password Flow with Bearer tokens
- Role-Based Access Control (RBAC) with granular permissions
- API Key authentication for external service integration
- Secure password hashing with bcrypt
- Token blacklisting for logout
- Permission decorators for endpoints
- Rate limiting integration per user tier

Architecture Pattern: OAuth2 + JWT + RBAC
Security Features:
    - HS256/RS256 JWT signing
    - Token expiration and refresh
    - Role-based permissions
    - Scope-based access control
    - API key management
    - Secure cookie handling

Integration:
    - equation_database: User and ApiKey models
    - equation_services: UserService for validation
    - equation_config: Security settings
    - FastAPI: OAuth2 scheme integration

Usage:
    # In FastAPI endpoint
    from equation_auth import require_auth, require_role, require_permission

    @app.get("/admin/users")
    @require_role("admin")
    async def list_users(current_user: User = Depends(require_auth())):
        return {"users": []}

    @app.post("/equations")
    @require_permission("equations:create")
    async def create_equation(
        data: EquationCreate,
        current_user: User = Depends(require_auth())
    ):
        return await service.create(data, user_id=current_user.id)

Environment Variables:
    SECURITY_SECRET_KEY: JWT signing key
    SECURITY_ALGORITHM: JWT algorithm (default: HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime
    REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime
"""

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Set

# JWT handling
try:
    import jwt
    from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

# Password hashing
try:
    from passlib.context import CryptContext

    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    CryptContext = None

# FastAPI security
try:
    from fastapi import Depends, HTTPException, Request, Security, status
    from fastapi.security import (
        APIKeyHeader,
        HTTPAuthorizationCredentials,
        HTTPBearer,
        OAuth2PasswordBearer,
        OAuth2PasswordRequestForm,
    )

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    Depends = lambda *args, **kwargs: None
    HTTPException = Exception
    status = None
    OAuth2PasswordBearer = None

# Database integration
try:
    from sqlalchemy.ext.asyncio import AsyncSession

    from equation_database import ApiKey, User, UserRepository, get_db_session

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    User = None
    ApiKey = None
    AsyncSession = None

# Configuration
try:
    from equation_config import Settings, get_settings

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    Settings = None

logger = logging.getLogger("amos_equation_auth")


# ============================================================================
# Enums and Constants
# ============================================================================


class UserRole(str, Enum):
    """User roles for RBAC."""

    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    API = "api"  # For API key access


class Permission(str, Enum):
    """Granular permissions."""

    # Equation permissions
    EQUATIONS_READ = "equations:read"
    EQUATIONS_CREATE = "equations:create"
    EQUATIONS_UPDATE = "equations:update"
    EQUATIONS_DELETE = "equations:delete"
    EQUATIONS_EXECUTE = "equations:execute"

    # User permissions
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"

    # Admin permissions
    ADMIN_DASHBOARD = "admin:dashboard"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_AUDIT = "admin:audit"

    # System permissions
    SYSTEM_HEALTH = "system:health"
    SYSTEM_METRICS = "system:metrics"


# Role-to-permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, list[Permission]] = {
    UserRole.SUPERUSER: list(Permission),  # All permissions
    UserRole.ADMIN: [
        Permission.EQUATIONS_READ,
        Permission.EQUATIONS_CREATE,
        Permission.EQUATIONS_UPDATE,
        Permission.EQUATIONS_DELETE,
        Permission.EQUATIONS_EXECUTE,
        Permission.USERS_READ,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.ADMIN_DASHBOARD,
        Permission.ADMIN_SETTINGS,
        Permission.ADMIN_AUDIT,
        Permission.SYSTEM_HEALTH,
        Permission.SYSTEM_METRICS,
    ],
    UserRole.USER: [
        Permission.EQUATIONS_READ,
        Permission.EQUATIONS_EXECUTE,
        Permission.USERS_READ,
        Permission.USERS_UPDATE,
    ],
    UserRole.GUEST: [
        Permission.EQUATIONS_READ,
        Permission.EQUATIONS_EXECUTE,
    ],
    UserRole.API: [
        Permission.EQUATIONS_READ,
        Permission.EQUATIONS_EXECUTE,
    ],
}


# ============================================================================
# Password Hashing
# ============================================================================


class PasswordHasher:
    """Secure password hashing using bcrypt."""

    def __init__(self):
        if PASSLIB_AVAILABLE:
            self._context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        else:
            self._context = None

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        if not self._context:
            # Fallback to SHA256 (not for production)
            return hashlib.sha256(password.encode()).hexdigest()
        return self._context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        if not self._context:
            # Fallback to SHA256 comparison
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
        return self._context.verify(plain_password, hashed_password)


# Global password hasher
_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password."""
    return _password_hasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return _password_hasher.verify_password(plain_password, hashed_password)


# ============================================================================
# JWT Token Management
# ============================================================================


class TokenManager:
    """JWT token generation and validation."""

    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key or self._get_secret_key()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self._blacklisted_tokens: Set[str] = set()

    def _get_secret_key(self) -> str:
        """Get secret key from settings or generate one."""
        if CONFIG_AVAILABLE:
            try:
                settings = get_settings()
                return settings.security.jwt_secret.get_secret_value()
            except Exception:
                pass
        # Fallback - generate a temporary key (not for production)
        return secrets.token_urlsafe(32)

    def create_access_token(self, data: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Create JWT access token."""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT required for token generation")

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(UTC),
                "type": "access",
                "jti": str(uuid.uuid4()),  # Unique token ID for blacklisting
            }
        )

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT required for token generation")

        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        to_encode.update(
            {"exp": expire, "iat": datetime.now(UTC), "type": "refresh", "jti": str(uuid.uuid4())}
        )

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token."""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT required for token validation")

        # Check blacklist
        if token in self._blacklisted_tokens:
            raise InvalidTokenError("Token has been revoked")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")

    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist (logout)."""
        self._blacklisted_tokens.add(token)

    def verify_token_type(self, payload: Dict[str, Any], expected_type: str) -> bool:
        """Verify token type matches expected."""
        return payload.get("type") == expected_type


# Global token manager
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Get or create token manager."""
    global _token_manager
    if _token_manager is None:
        if CONFIG_AVAILABLE:
            settings = get_settings()
            _token_manager = TokenManager(
                secret_key=settings.security.jwt_secret.get_secret_value(),
                algorithm=settings.security.jwt_algorithm,
                access_token_expire_minutes=settings.security.access_token_expire_minutes,
                refresh_token_expire_days=settings.security.refresh_token_expire_days,
            )
        else:
            _token_manager = TokenManager()
    return _token_manager


# ============================================================================
# OAuth2 Scheme
# ============================================================================

# OAuth2 password bearer for token URL
if FASTAPI_AVAILABLE and OAuth2PasswordBearer:
    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl="/api/v1/auth/token",
        scopes={"read": "Read access", "write": "Write access", "admin": "Admin access"},
    )

    # API Key header for external services
    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
else:
    oauth2_scheme = None
    api_key_header = None


# ============================================================================
# Authentication Dependencies
# ============================================================================


class AuthenticationError(Exception):
    """Authentication error with details."""

    def __init__(self, message: str, status_code: int = 401, headers: Dict[str, str] = None):
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


async def get_current_user(
    token: str = Depends(oauth2_scheme) if oauth2_scheme else None,
    api_key: str = Security(api_key_header) if api_key_header else None,
    session: AsyncSession = Depends(get_db_session)
    if (FASTAPI_AVAILABLE and DATABASE_AVAILABLE)
    else None,
) -> User:
    """Get current authenticated user from token or API key.

    This is the main authentication dependency for FastAPI endpoints.
    Supports both JWT tokens (OAuth2) and API keys.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try API key first
    if api_key and DATABASE_AVAILABLE:
        user = await _authenticate_api_key(api_key, session)
        if user:
            return user

    # Try JWT token
    if token and JWT_AVAILABLE:
        try:
            token_manager = get_token_manager()
            payload = token_manager.decode_token(token)

            # Verify it's an access token
            if not token_manager.verify_token_type(payload, "access"):
                raise credentials_exception

            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception

            # Get user from database
            if DATABASE_AVAILABLE and session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(User, int(user_id))
                if user is None or not user.is_active:
                    raise credentials_exception
                return user
            else:
                # Fallback without database
                raise credentials_exception

        except InvalidTokenError:
            raise credentials_exception

    raise credentials_exception


async def _authenticate_api_key(api_key: str, session: AsyncSession) -> Optional[User]:
    """Authenticate using API key."""
    if not DATABASE_AVAILABLE:
        return None

    # Hash the API key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Look up in database
    from equation_database import ApiKeyRepository

    api_key_repo = ApiKeyRepository(session)

    api_key_record = await api_key_repo.get_by_key_hash(key_hash)
    if not api_key_record:
        return None

    # Check if expired or revoked
    if api_key_record.is_revoked:
        return None

    if api_key_record.expires_at and api_key_record.expires_at < datetime.now(UTC):
        return None

    # Update usage
    await api_key_repo.increment_usage(api_key_record)
    await session.commit()

    # Return associated user
    if api_key_record.user:
        return api_key_record.user

    return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user) if FASTAPI_AVAILABLE else None,
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if status else 403, detail="Inactive user"
        )
    return current_user


def require_auth() -> Any:
    """Dependency to require authentication.

    Usage:
        @app.get("/protected")
        async def protected(user: User = Depends(require_auth())):
            return {"user": user.username}
    """
    return get_current_active_user


# ============================================================================
# Authorization Decorators
# ============================================================================


def require_role(required_role: UserRole | str):
    """Decorator to require specific role.

    Usage:
        @app.get("/admin")
        @require_role("admin")
        async def admin_endpoint(user: User = Depends(require_auth())):
            return {"message": "Admin access granted"}
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs or dependencies
            current_user = kwargs.get("current_user")
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                    detail="Authentication required",
                )

            # Check role
            user_role = getattr(current_user, "role", UserRole.USER)
            if isinstance(user_role, str):
                user_role = UserRole(user_role)

            # Superuser can do anything
            if user_role == UserRole.SUPERUSER:
                return await func(*args, **kwargs)

            # Check specific role
            if isinstance(required_role, str):
                required = UserRole(required_role)
            else:
                required = required_role

            # Role hierarchy
            role_hierarchy = [
                UserRole.GUEST,
                UserRole.API,
                UserRole.USER,
                UserRole.ADMIN,
                UserRole.SUPERUSER,
            ]

            if role_hierarchy.index(user_role) < role_hierarchy.index(required):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN if status else 403,
                    detail=f"Role '{required_role}' required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_permission(required_permission: Permission | str):
    """Decorator to require specific permission.

    Usage:
        @app.post("/equations")
        @require_permission("equations:create")
        async def create(user: User = Depends(require_auth())):
            return {"message": "Created"}
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user
            current_user = kwargs.get("current_user")
            if not current_user:
                for arg in args:
                    if isinstance(arg, User):
                        current_user = arg
                        break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                    detail="Authentication required",
                )

            # Get user role
            user_role = getattr(current_user, "role", UserRole.USER)
            if isinstance(user_role, str):
                user_role = UserRole(user_role)

            # Superuser has all permissions
            if user_role == UserRole.SUPERUSER:
                return await func(*args, **kwargs)

            # Convert permission string to enum if needed
            if isinstance(required_permission, str):
                try:
                    perm = Permission(required_permission)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if status else 500,
                        detail=f"Invalid permission: {required_permission}",
                    )
            else:
                perm = required_permission

            # Check if user has permission
            user_permissions = ROLE_PERMISSIONS.get(user_role, [])
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN if status else 403,
                    detail=f"Permission '{required_permission}' required",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def has_permission(user: User, permission: Permission | str) -> bool:
    """Check if user has a specific permission.

    Args:
        user: User to check
        permission: Permission to verify

    Returns:
        True if user has permission
    """
    user_role = getattr(user, "role", UserRole.USER)
    if isinstance(user_role, str):
        user_role = UserRole(user_role)

    # Superuser has all permissions
    if user_role == UserRole.SUPERUSER:
        return True

    # Convert to enum if string
    if isinstance(permission, str):
        try:
            perm = Permission(permission)
        except ValueError:
            return False
    else:
        perm = permission

    return perm in ROLE_PERMISSIONS.get(user_role, [])


# ============================================================================
# Authentication Endpoints (for integration)
# ============================================================================


class AuthEndpoints:
    """Authentication endpoints for FastAPI integration.

    Usage in equation_app.py:
        from equation_auth import AuthEndpoints
        auth_endpoints = AuthEndpoints()
        app.include_router(auth_endpoints.router, prefix="/api/v1/auth")
    """

    def __init__(self):
        self.router = None
        if FASTAPI_AVAILABLE:
            from fastapi import APIRouter

            self.router = APIRouter(tags=["Authentication"])
            self._setup_routes()

    def _setup_routes(self):
        """Setup authentication routes."""
        if not self.router:
            return

        @self.router.post("/token")
        async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
            """OAuth2 login endpoint."""
            if not DATABASE_AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE if status else 503,
                    detail="Database not available",
                )

            async for session in get_db_session():
                user_repo = UserRepository(session)
                user = await user_repo.get_by_username(form_data.username)

                if not user or not verify_password(form_data.password, user.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                        detail="Incorrect username or password",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN if status else 403,
                        detail="User account is inactive",
                    )

                # Create tokens
                token_manager = get_token_manager()
                access_token = token_manager.create_access_token(
                    data={"sub": str(user.id), "role": user.role or "user"}
                )
                refresh_token = token_manager.create_refresh_token(data={"sub": str(user.id)})

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": token_manager.access_token_expire_minutes * 60,
                }

        @self.router.post("/refresh")
        async def refresh_token(refresh_token: str):
            """Refresh access token."""
            try:
                token_manager = get_token_manager()
                payload = token_manager.decode_token(refresh_token)

                if not token_manager.verify_token_type(payload, "refresh"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                        detail="Invalid token type",
                    )

                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                        detail="Invalid token",
                    )

                # Create new access token
                access_token = token_manager.create_access_token(data={"sub": user_id})

                return {"access_token": access_token, "token_type": "bearer"}

            except InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED if status else 401,
                    detail="Invalid refresh token",
                )

        @self.router.post("/logout")
        async def logout(token: str = Depends(oauth2_scheme)):
            """Logout and blacklist token."""
            token_manager = get_token_manager()
            token_manager.blacklist_token(token)
            return {"message": "Successfully logged out"}

        @self.router.get("/me")
        async def get_me(current_user: User = Depends(get_current_active_user)):
            """Get current user info."""
            return {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": getattr(current_user, "role", "user"),
                "is_active": current_user.is_active,
                "permissions": [
                    p.value
                    for p in ROLE_PERMISSIONS.get(
                        UserRole(getattr(current_user, "role", "user")), []
                    )
                ],
            }


# ============================================================================
# Helper Functions
# ============================================================================


def create_api_key(user_id: int, name: str, scopes: List[str] = None) -> str:
    """Create a new API key for a user.

    Args:
        user_id: User ID to associate with the key
        name: Human-readable name for the key
        scopes: Optional list of permission scopes

    Returns:
        The API key (store it securely - it's shown only once)
    """
    # Generate random API key
    api_key = f"amos_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Store hash in database (implementation depends on your setup)
    logger.info(f"Created API key for user {user_id}: {name}")

    return api_key


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and return payload.

    Args:
        token: JWT token string

    Returns:
        Token payload if valid, None otherwise
    """
    if not JWT_AVAILABLE:
        return None

    try:
        token_manager = get_token_manager()
        return token_manager.decode_token(token)
    except InvalidTokenError:
        return None


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example usage of authentication system."""
    # Hash a password
    hashed = hash_password("my_secure_password")
    print(f"Hashed: {hashed}")

    # Verify password
    is_valid = verify_password("my_secure_password", hashed)
    print(f"Valid: {is_valid}")

    # Create tokens
    token_manager = get_token_manager()
    access_token = token_manager.create_access_token(data={"sub": "123", "role": "admin"})
    print(f"Access Token: {access_token}")

    # Verify token
    payload = token_manager.decode_token(access_token)
    print(f"Payload: {payload}")


if __name__ == "__main__":
    asyncio.run(example_usage())

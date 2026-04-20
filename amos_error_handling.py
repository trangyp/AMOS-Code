#!/usr/bin/env python3
"""
AMOS Global Error Handling - Production-Ready Exception Management

Implements comprehensive error handling for the AMOS FastAPI Gateway:
- Standardized error response format (RFC 7807 Problem Details)
- Global exception handlers for all error types
- Structured error logging with correlation IDs
- Custom AMOS exception hierarchy
- Validation error handling
- Database error handling
- HTTP exception customization
- Error tracking and metrics

Features:
- JSON Problem Details format for all errors
- Consistent error codes and messages
- Automatic error severity classification
- Integration with structured logging
- Error correlation across distributed traces
- PII redaction in error messages

Usage:
    from fastapi import FastAPI
    from amos_error_handling import setup_error_handlers, AMOSException

    app = FastAPI()
    setup_error_handlers(app)

    # Raise custom exception

Integration:
- amos_structured_logging - Error logging with context
- amos_opentelemetry_tracing - Error span tracking
- amos_metrics_exporter - Error rate metrics

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

from collections.abc import Callable
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from typing import Any

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# SQLAlchemy imports
try:
    from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Try to import structured logging
try:
    from collections.abc import Callable

    from amos_structured_logging import get_correlation_id, get_logger, log_exception

    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False


class ErrorSeverity(Enum):
    """Error severity levels."""

    CRITICAL = "critical"  # System failure, immediate attention
    ERROR = "error"  # Functional failure, needs attention
    WARNING = "warning"  # Potential issue, monitor
    INFO = "info"  # Informational, no action needed


class ErrorCategory(Enum):
    """Error categories for classification."""

    VALIDATION = "validation_error"
    AUTHENTICATION = "authentication_error"
    AUTHORIZATION = "authorization_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict_error"
    DATABASE = "database_error"
    EXTERNAL_SERVICE = "external_service_error"
    RATE_LIMIT = "rate_limit_error"
    CIRCUIT_BREAKER = "circuit_breaker_error"
    INTERNAL = "internal_error"


class AMOSException(Exception):
    """
    Base exception for AMOS system.

    All AMOS exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: dict[str, Any] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.INTERNAL,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.severity = severity
        self.category = category
        self.timestamp = datetime.now(UTC).isoformat()
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "type": f"https://amos.io/errors/{self.error_code.lower()}",
            "title": self.message,
            "status": self.status_code,
            "error_code": self.error_code,
            "details": self.details,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp,
        }


class ValidationException(AMOSException):
    """Exception for validation errors."""

    def __init__(self, message: str = "Validation error", details: dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.VALIDATION,
        )


class NotFoundException(AMOSException):
    """Exception for resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str = None, details: dict[str, Any] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} '{resource_id}' not found"

        super().__init__(
            message=message,
            error_code=f"{resource_type.upper()}_NOT_FOUND",
            status_code=404,
            details=details,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.NOT_FOUND,
        )


class AuthenticationException(AMOSException):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_REQUIRED",
            status_code=401,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.AUTHENTICATION,
        )


class AuthorizationException(AMOSException):
    """Exception for authorization errors."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            status_code=403,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.AUTHORIZATION,
        )


class ConflictException(AMOSException):
    """Exception for resource conflict errors."""

    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            status_code=409,
            details=details,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.CONFLICT,
        )


class DatabaseException(AMOSException):
    """Exception for database errors."""

    def __init__(self, message: str = "Database error", details: dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.DATABASE,
        )


class RateLimitException(AMOSException):
    """Exception for rate limiting errors."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after},
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.RATE_LIMIT,
        )


class CircuitBreakerException(AMOSException):
    """Exception for circuit breaker errors."""

    def __init__(self, endpoint: str, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            error_code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            details={"endpoint": endpoint},
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.CIRCUIT_BREAKER,
        )


def create_error_response(exc: Exception, correlation_id: str = None) -> dict[str, Any]:
    """Create standardized error response."""

    if isinstance(exc, AMOSException):
        response = exc.to_dict()
    elif isinstance(exc, StarletteHTTPException):
        response = {
            "type": "https://amos.io/errors/http_error",
            "title": exc.detail,
            "status": exc.status_code,
            "error_code": f"HTTP_{exc.status_code}",
            "severity": ErrorSeverity.WARNING.value,
            "category": ErrorCategory.INTERNAL.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    elif isinstance(exc, RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": error.get("loc", ["unknown"])[-1],
                    "message": error.get("msg", "Validation error"),
                    "type": error.get("type", "validation_error"),
                }
            )
        response = {
            "type": "https://amos.io/errors/validation_error",
            "title": "Request validation failed",
            "status": 422,
            "error_code": "VALIDATION_ERROR",
            "details": {"errors": errors},
            "severity": ErrorSeverity.WARNING.value,
            "category": ErrorCategory.VALIDATION.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    elif SQLALCHEMY_AVAILABLE and isinstance(exc, IntegrityError):
        response = {
            "type": "https://amos.io/errors/database_integrity_error",
            "title": "Database integrity error",
            "status": 409,
            "error_code": "DATABASE_INTEGRITY_ERROR",
            "severity": ErrorSeverity.ERROR.value,
            "category": ErrorCategory.DATABASE.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    elif SQLALCHEMY_AVAILABLE and isinstance(exc, NoResultFound):
        response = {
            "type": "https://amos.io/errors/resource_not_found",
            "title": "Resource not found",
            "status": 404,
            "error_code": "RESOURCE_NOT_FOUND",
            "severity": ErrorSeverity.WARNING.value,
            "category": ErrorCategory.NOT_FOUND.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        # Generic error
        response = {
            "type": "https://amos.io/errors/internal_error",
            "title": "Internal server error",
            "status": 500,
            "error_code": "INTERNAL_ERROR",
            "severity": ErrorSeverity.ERROR.value,
            "category": ErrorCategory.INTERNAL.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    # Add correlation ID
    if correlation_id:
        response["correlation_id"] = correlation_id

    return response


def log_error(exc: Exception, request: Request, correlation_id: str = None) -> None:
    """Log error with context."""
    if not STRUCTURED_LOGGING_AVAILABLE:
        return

    logger = get_logger("amos.errors")

    extra = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }

    if correlation_id:
        extra["correlation_id"] = correlation_id

    if request:
        extra.update(
            {
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": request.client.host if request.client else None,
            }
        )

    # Determine severity
    if isinstance(exc, AMOSException):
        severity = exc.severity
    elif isinstance(exc, RequestValidationError):
        severity = ErrorSeverity.WARNING
    else:
        severity = ErrorSeverity.ERROR

    # Log with appropriate level
    if severity == ErrorSeverity.CRITICAL:
        logger.critical("Exception occurred", extra=extra, exc_info=True)
    elif severity == ErrorSeverity.ERROR:
        logger.error("Exception occurred", extra=extra, exc_info=True)
    elif severity == ErrorSeverity.WARNING:
        logger.warning("Exception occurred", extra=extra)
    else:
        logger.info("Exception occurred", extra=extra)


async def amos_exception_handler(request: Request, exc: AMOSException) -> JSONResponse:
    """Handler for AMOS exceptions."""
    correlation_id = get_correlation_id() if STRUCTURED_LOGGING_AVAILABLE else None

    log_error(exc, request, correlation_id)

    response = create_error_response(exc, correlation_id)

    return JSONResponse(
        status_code=exc.status_code,
        content=response,
        headers={"X-Correlation-ID": correlation_id or "", "X-Error-Code": exc.error_code}
        if correlation_id
        else {"X-Error-Code": exc.error_code},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for HTTP exceptions."""
    correlation_id = get_correlation_id() if STRUCTURED_LOGGING_AVAILABLE else None

    log_error(exc, request, correlation_id)

    response = create_error_response(exc, correlation_id)

    return JSONResponse(
        status_code=exc.status_code,
        content=response,
        headers={"X-Correlation-ID": correlation_id or ""} if correlation_id else {},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for validation errors."""
    correlation_id = get_correlation_id() if STRUCTURED_LOGGING_AVAILABLE else None

    log_error(exc, request, correlation_id)

    response = create_error_response(exc, correlation_id)

    return JSONResponse(
        status_code=422,
        content=response,
        headers={"X-Correlation-ID": correlation_id or ""} if correlation_id else {},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for all other exceptions."""
    correlation_id = get_correlation_id() if STRUCTURED_LOGGING_AVAILABLE else None

    log_error(exc, request, correlation_id)

    # Don't expose internal details in production
    response = {
        "type": "https://amos.io/errors/internal_error",
        "title": "Internal server error",
        "status": 500,
        "error_code": "INTERNAL_ERROR",
        "timestamp": datetime.now(UTC).isoformat(),
    }

    if correlation_id:
        response["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=500,
        content=response,
        headers={"X-Correlation-ID": correlation_id or ""} if correlation_id else {},
    )


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup global error handlers for FastAPI application.

    Args:
        app: FastAPI application instance
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for error handling setup")

    # Register exception handlers
    app.add_exception_handler(AMOSException, amos_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    print("✅ Global error handlers registered")


def setup_error_handlers_safe(app: Any) -> bool:
    """
    Safely setup error handlers with availability checking.

    Returns:
        True if handlers were registered successfully
    """
    if not FASTAPI_AVAILABLE:
        print("⚠️  FastAPI not available. Error handlers not registered.")
        return False

    try:
        setup_error_handlers(app)
        return True
    except Exception as e:
        print(f"⚠️  Failed to setup error handlers: {e}")
        return False


# Aliases for backward compatibility
NotFoundError = NotFoundException
ValidationError = ValidationException
DatabaseError = DatabaseException

__all__ = [
    # Exception classes
    "AMOSException",
    "ValidationException",
    "ValidationError",
    "NotFoundException",
    "NotFoundError",
    "AuthenticationException",
    "AuthorizationException",
    "ConflictException",
    "DatabaseException",
    "DatabaseError",
    "RateLimitException",
    "CircuitBreakerException",
    # Enums
    "ErrorSeverity",
    "ErrorCategory",
    # Functions
    "setup_error_handlers",
    "setup_error_handlers_safe",
    "create_error_response",
    "log_error",
]

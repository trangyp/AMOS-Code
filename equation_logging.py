#!/usr/bin/env python3
"""AMOS Equation Logging - Structured Logging & Audit Trail.

Production-grade logging system:
- Structured JSON logging with correlation IDs
- Request/response middleware logging
- Audit trail for security compliance (SOC2, HIPAA)
- Performance logging and slow query detection
- Error tracking and stack trace capture
- Log sampling and filtering
- Integration with ELK/Loki/Splunk
- Sensitive data masking
- Log retention and rotation
- Distributed tracing correlation

Architecture Pattern: Structured logging with context propagation
Logging Features:
    - JSON format for machine parsing
    - Correlation ID tracking across requests
    - Automatic request/response logging
    - Audit events for data access
    - Performance metrics logging
    - PII/sensitive data masking
    - Log level configuration

Compliance Features:
    - User action audit trail
    - Data access logging
    - Failed authentication attempts
    - Permission changes
    - Configuration changes
    - Export/backup operations

Integration:
    - equation_app: Middleware integration
    - equation_auth: User context for audit
    - equation_database: Query logging
    - equation_tracing: Trace ID correlation

Usage:
    # In endpoint
    from equation_logging import get_logger, audit_log

    logger = get_logger("equations")
    logger.info("equation_created", equation_id=1, user_id=123)

    # Audit logging
    audit_log(
        action="equation_deleted",
        user_id=123,
        resource_type="equation",
        resource_id=1,
        details={"reason": "user_request"}
    )

Environment Variables:
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
    LOG_FORMAT: json or console (default: json in production)
    LOG_CORRELATION_ID: Enable correlation ID tracking (default: true)
    LOG_AUDIT_ENABLED: Enable audit logging (default: true)
    LOG_SENSITIVE_MASK: Mask sensitive fields (default: true)
    LOG_REQUEST_BODY: Log request bodies (default: false)
    LOG_RESPONSE_BODY: Log response bodies (default: false)
"""

import hashlib
import json
import logging
import re
import sys
import traceback
import uuid
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from collections.abc import Callable
from contextvars import ContextVar
from enum import Enum
from functools import wraps
from typing import Any

# FastAPI integration
try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    Request = None
    Response = None
    BaseHTTPMiddleware = None

# Tracing integration for correlation
try:
    from equation_tracing import get_current_trace_id

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

try:
    from equation_auth import get_current_user_id

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

logger = logging.getLogger("amos_equation_logging")


# ============================================================================
# Context Variables
# ============================================================================

# Context variables for request tracking
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default=None)
user_id_var: ContextVar[int] = ContextVar("user_id", default=None)
request_path_var: ContextVar[str] = ContextVar("request_path", default=None)


# ============================================================================
# Enums and Constants
# ============================================================================


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditAction(str, Enum):
    """Audit trail actions."""

    # Equation actions
    EQUATION_CREATED = "equation_created"
    EQUATION_READ = "equation_read"
    EQUATION_UPDATED = "equation_updated"
    EQUATION_DELETED = "equation_deleted"
    EQUATION_EXECUTED = "equation_executed"

    # User actions
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"

    # Authentication actions
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"

    # Admin actions
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    SETTINGS_CHANGED = "settings_changed"

    # Data actions
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    BACKUP_CREATED = "backup_created"
    CACHE_CLEARED = "cache_cleared"


# Sensitive fields to mask
SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "token",
    "api_key",
    "secret",
    "authorization",
    "cookie",
    "session",
    "credit_card",
    "ssn",
    "email",
    "phone",
    "address",
    "jwt",
    "refresh_token",
    "access_token",
}

# Field patterns to mask (regex)
SENSITIVE_PATTERNS = [
    re.compile(r"password[=:]\s*[^\s&]+", re.IGNORECASE),
    re.compile(r"token[=:]\s*[^\s&]+", re.IGNORECASE),
    re.compile(r"api_key[=:]\s*[^\s&]+", re.IGNORECASE),
    re.compile(r"secret[=:]\s*[^\s&]+", re.IGNORECASE),
]


# ============================================================================
# JSON Formatter
# ============================================================================


class JSONFormatter(logging.Formatter):
    """JSON structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }

        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add user ID if available
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # Add request path if available
        request_path = request_path_var.get()
        if request_path:
            log_data["request_path"] = request_path

        # Add trace ID if tracing available
        if TRACING_AVAILABLE:
            trace_id = get_current_trace_id()
            if trace_id:
                log_data["trace_id"] = trace_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stacktrace": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "asctime",
                "correlation_id",
                "user_id",
                "request_path",
            ]:
                log_data[key] = value

        return json.dumps(log_data, default=str)


# ============================================================================
# Console Formatter (for development)
# ============================================================================


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        correlation_id = correlation_id_var.get()
        cid_str = f"[{correlation_id[:8]}] " if correlation_id else ""

        return f"{color}{record.levelname:8}{reset} {cid_str}{record.getMessage()}"


# ============================================================================
# Logging Configuration
# ============================================================================


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    enable_console: bool = True,
    enable_file: bool = False,
    file_path: str = None,
) -> None:
    """Configure structured logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: json or console
        enable_console: Enable console output
        enable_file: Enable file output
        file_path: Path to log file
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if format_type == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(ColoredFormatter())
        root_logger.addHandler(console_handler)

    # File handler
    if enable_file and file_path:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# ============================================================================
# Logger Factory
# ============================================================================


class StructuredLogger:
    """Structured logger with context support."""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(self, level: int, event: str, **kwargs: Any) -> None:
        """Internal log method with context."""
        extra = {
            "event": event,
            "correlation_id": correlation_id_var.get(),
            "user_id": user_id_var.get(),
            "request_path": request_path_var.get(),
            **kwargs,
        }
        self._logger.log(level, event, extra=extra)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(logging.ERROR, event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._logger.exception(event, extra=kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger.

    Args:
        name: Logger name (e.g., 'equations', 'auth', 'database')

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# ============================================================================
# Data Masking
# ============================================================================


def mask_sensitive_data(data: Any) -> Any:
    """Mask sensitive fields in data.

    Args:
        data: Data to mask (dict, list, str)

    Returns:
        Masked data
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                masked[key] = "***MASKED***"
            elif isinstance(value, (dict, list)):
                masked[key] = mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked

    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    elif isinstance(data, str):
        # Apply regex patterns
        masked = data
        for pattern in SENSITIVE_PATTERNS:
            masked = pattern.sub(lambda m: f"{m.group(0).split('=')[0]}=***MASKED***", masked)
        return masked

    return data


def hash_identifier(identifier: str) -> str:
    """Hash an identifier for logging (e.g., email, user ID).

    Args:
        identifier: String to hash

    Returns:
        SHA256 hash truncated to 16 chars
    """
    return hashlib.sha256(identifier.encode()).hexdigest()[:16]


# ============================================================================
# Audit Trail
# ============================================================================


class AuditLogger:
    """Audit trail logger for compliance."""

    def __init__(self):
        self._logger = logging.getLogger("amos_audit")
        self._enabled = True

    def log(
        self,
        action: Union[AuditAction, str],
        user_id: int = None,
        resource_type: str = None,
        resource_id: Union[int, str] = None,
        details: dict[str, Any] = None,
        success: bool = True,
        ip_address: str = None,
        user_agent: str = None,
    ) -> None:
        """Log an audit event.

        Args:
            action: Audit action type
            user_id: User performing the action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details
            success: Whether the action succeeded
            ip_address: Client IP address
            user_agent: Client user agent
        """
        if not self._enabled:
            return

        if isinstance(action, AuditAction):
            action = action.value

        audit_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "audit",
            "action": action,
            "user_id": user_id or user_id_var.get(),
            "correlation_id": correlation_id_var.get(),
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "details": mask_sensitive_data(details or {}),
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        self._logger.info(json.dumps(audit_record, default=str))

    def enable(self) -> None:
        """Enable audit logging."""
        self._enabled = True

    def disable(self) -> None:
        """Disable audit logging."""
        self._enabled = False


# Global audit logger
_audit_logger = AuditLogger()


def audit_log(
    action: Union[AuditAction, str],
    user_id: int = None,
    resource_type: str = None,
    resource_id: Union[int, str] = None,
    details: dict[str, Any] = None,
    success: bool = True,
    ip_address: str = None,
    user_agent: str = None,
) -> None:
    """Log an audit event.

    Args:
        action: Audit action (e.g., 'equation_created')
        user_id: User performing the action
        resource_type: Type of resource (e.g., 'equation')
        resource_id: Resource identifier
        details: Additional context
        success: Whether action succeeded
        ip_address: Client IP
        user_agent: Client user agent
    """
    _audit_logger.log(
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# ============================================================================
# Performance Logging
# ============================================================================


def log_performance(
    operation: str, duration_ms: float, success: bool = True, metadata: dict[str, Any] = None
) -> None:
    """Log performance metric.

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        success: Whether operation succeeded
        metadata: Additional metadata
    """
    logger = get_logger("performance")

    log_data = {
        "event": "performance_metric",
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
        **(metadata or {}),
    }

    # Log slow operations as warnings
    if duration_ms > 1000:  # 1 second
        logger.warning("slow_operation_detected", **log_data)
    else:
        logger.info("performance_metric", **log_data)


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, operation: str, metadata: dict[str, Any] = None):
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time: datetime = None
        self.duration_ms: float = 0.0

    def __enter__(self) -> PerformanceTimer:
        self.start_time = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.start_time:
            end_time = datetime.now(timezone.utc)
            self.duration_ms = (end_time - self.start_time).total_seconds() * 1000
            log_performance(
                operation=self.operation,
                duration_ms=self.duration_ms,
                success=exc_type is None,
                metadata=self.metadata,
            )


def timed(operation: str, **metadata: Any) -> Callable:
    """Decorator to time function execution.

    Args:
        operation: Operation name for logging
        **metadata: Additional metadata

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with PerformanceTimer(operation, metadata):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            with PerformanceTimer(operation, metadata):
                return func(*args, **kwargs)

        return async_wrapper if func.__code__.co_flags & 0x80 else sync_wrapper

    return decorator


# ============================================================================
# Request Logging Middleware
# ============================================================================

if FASTAPI_AVAILABLE and BaseHTTPMiddleware:

    class LoggingMiddleware(BaseHTTPMiddleware):
        """Middleware for request/response logging."""

        def __init__(
            self,
            app: Any,
            log_request_body: bool = False,
            log_response_body: bool = False,
            exclude_paths: list[str] = None,
        ):
            super().__init__(app)
            self.log_request_body = log_request_body
            self.log_response_body = log_response_body
            self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs"]
            self.logger = get_logger("requests")

        async def dispatch(self, request: Request, call_next: Any) -> Response:
            """Process request and log details."""
            # Skip excluded paths
            path = request.url.path
            if any(path.startswith(excluded) for excluded in self.exclude_paths):
                return await call_next(request)

            # Generate correlation ID
            correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
            correlation_id_var.set(correlation_id)
            request_path_var.set(path)

            # Extract user info if available
            user_id = None
            if AUTH_AVAILABLE:
                try:
                    user_id = await get_current_user_id()
                    user_id_var.set(user_id)
                except Exception:
                    pass

            # Log request
            request_data = {
                "event": "request_started",
                "method": request.method,
                "path": path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "correlation_id": correlation_id,
                "user_id": user_id,
            }

            if self.log_request_body:
                try:
                    body = await request.body()
                    if body:
                        request_data["body_size"] = len(body)
                except Exception:
                    pass

            self.logger.info("request_started", **request_data)

            # Process request
            start_time = datetime.now(timezone.utc)
            try:
                response = await call_next(request)

                # Calculate duration
                end_time = datetime.now(timezone.utc)
                duration_ms = (end_time - start_time).total_seconds() * 1000

                # Log response
                response_data = {
                    "event": "request_completed",
                    "method": request.method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                }

                if self.log_response_body:
                    try:
                        # Note: This requires response body to be read
                        # In practice, you might need a custom response wrapper
                        pass
                    except Exception:
                        pass

                # Log level based on status code
                if response.status_code >= 500:
                    self.logger.error("request_failed", **response_data)
                elif response.status_code >= 400:
                    self.logger.warning("request_error", **response_data)
                else:
                    self.logger.info("request_completed", **response_data)

                # Add correlation ID to response headers
                response.headers["X-Correlation-ID"] = correlation_id

                return response

            except Exception as e:
                # Log exception
                end_time = datetime.now(timezone.utc)
                duration_ms = (end_time - start_time).total_seconds() * 1000

                self.logger.exception(
                    "request_exception",
                    method=request.method,
                    path=path,
                    duration_ms=duration_ms,
                    correlation_id=correlation_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise

            finally:
                # Clear context
                correlation_id_var.set(None)
                user_id_var.set(None)
                request_path_var.set(None)


# ============================================================================
# Error Tracking
# ============================================================================


def log_error(error: Exception, context: dict[str, Any] = None, level: str = "error") -> None:
    """Log an error with full context.

    Args:
        error: Exception to log
        context: Additional context
        level: Log level (error, warning, critical)
    """
    logger = get_logger("errors")

    error_data = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "error_hash": hashlib.sha256(str(error).encode()).hexdigest()[:16],
        "correlation_id": correlation_id_var.get(),
        "user_id": user_id_var.get(),
        "request_path": request_path_var.get(),
        **(context or {}),
    }

    # Log with appropriate level
    log_method = getattr(logger, level.lower(), logger.error)

    # Include traceback
    try:
        tb = traceback.format_exc()
        if tb and tb != "NoneType: None\n":
            error_data["traceback"] = tb
    except Exception:
        pass

    log_method("error_occurred", **error_data)


# ============================================================================
# Business Event Logging
# ============================================================================


class BusinessEventLogger:
    """Logger for business events and analytics."""

    def __init__(self):
        self.logger = get_logger("business")

    def log_event(
        self, event_name: str, user_id: int = None, properties: dict[str, Any] = None
    ) -> None:
        """Log a business event.

        Args:
            event_name: Event name (e.g., 'equation_created')
            user_id: User ID
            properties: Event properties
        """
        event_data = {
            "event_type": "business",
            "event_name": event_name,
            "user_id": user_id or user_id_var.get(),
            "correlation_id": correlation_id_var.get(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "properties": mask_sensitive_data(properties or {}),
        }

        self.logger.info("business_event", **event_data)

    def equation_created(self, equation_id: int, user_id: int, domain: str) -> None:
        """Log equation creation."""
        self.log_event(
            "equation_created",
            user_id=user_id,
            properties={"equation_id": equation_id, "domain": domain},
        )

    def equation_executed(
        self, equation_id: int, user_id: int, execution_time_ms: float, success: bool
    ) -> None:
        """Log equation execution."""
        self.log_event(
            "equation_executed",
            user_id=user_id,
            properties={
                "equation_id": equation_id,
                "execution_time_ms": execution_time_ms,
                "success": success,
            },
        )

    def user_registered(self, user_id: int, registration_method: str) -> None:
        """Log user registration."""
        self.log_event(
            "user_registered",
            user_id=user_id,
            properties={"registration_method": registration_method},
        )


# Global business event logger
business_events = BusinessEventLogger()


# ============================================================================
# Utility Functions
# ============================================================================


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


def get_current_user_id() -> int:
    """Get current user ID from context."""
    return user_id_var.get()


def set_user_id(user_id: int) -> None:
    """Set user ID for current context."""
    user_id_var.set(user_id)


# ============================================================================
# Example Usage
# ============================================================================


async def example_usage():
    """Example usage of logging system."""
    # Configure logging
    configure_logging(level="INFO", format_type="console")

    # Get logger
    logger = get_logger("equations")

    # Set correlation ID
    correlation_id_var.set("corr-12345")
    user_id_var.set(42)

    # Log structured messages
    logger.info("equation_created", equation_id=1, name="Linear Equation", domain="mathematics")

    logger.warning("high_memory_usage", memory_percent=85.5)

    # Audit logging
    audit_log(
        action=AuditAction.EQUATION_CREATED,
        user_id=42,
        resource_type="equation",
        resource_id=1,
        details={"formula": "y = 2*x + 3"},
        success=True,
    )

    # Business event
    business_events.equation_created(equation_id=1, user_id=42, domain="mathematics")

    # Performance timing
    with PerformanceTimer("database_query", {"table": "equations"}):
        import asyncio

        await asyncio.sleep(0.1)

    # Decorator timing
    @timed("expensive_operation", category="math")
    async def expensive_operation() -> str:
        await asyncio.sleep(0.05)
        return "result"

    await expensive_operation()

    print("\nLogging examples completed!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())

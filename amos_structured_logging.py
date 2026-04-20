#!/usr/bin/env python3
"""AMOS Structured Logging - Production-Ready JSON Logging with Correlation IDs

Implements enterprise logging standards:
- JSON structured logging for machine parsing
- Correlation IDs for distributed tracing
- Request/response context propagation
- Automatic PII redaction
- Log level configuration per environment
- Integration with OpenTelemetry trace IDs
- FastAPI middleware for automatic context injection

Architecture:
- Correlation ID propagation through request lifecycle
- Structured context for all log entries
- Integration with existing tracing (OpenTelemetry)
- Compatible with ELK/Loki/Grafana log aggregation

Usage:
    from fastapi import FastAPI
    from amos_structured_logging import StructuredLoggingMiddleware, get_logger

    app = FastAPI()
    app.add_middleware(StructuredLoggingMiddleware)

    logger = get_logger()
    logger.info("User login", extra={"user_id": "123", "tenant": "ws-456"})

Integration:
- amos_opentelemetry_tracing - Uses trace IDs as correlation IDs
- amos_fastapi_gateway - Auto-injects request context
- amos_metrics_exporter - Correlates metrics with logs

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Optional

# FastAPI imports
try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# OpenTelemetry integration
try:
    from opentelemetry import trace

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


# Context variables for correlation tracking
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)
_request_id: ContextVar[str] = ContextVar("request_id", default=None)
_tenant_id: ContextVar[str] = ContextVar("tenant_id", default=None)
_user_id: ContextVar[str] = ContextVar("user_id", default=None)


@dataclass
class LoggingConfig:
    """Configuration for structured logging."""

    level: str = "INFO"
    format: str = "json"  # json or text
    include_timestamp: bool = True
    include_correlation_id: bool = True
    include_trace_id: bool = True
    redact_pii: bool = True
    pii_fields: list = None
    output: Any = sys.stdout

    def __post_init__(self):
        if self.pii_fields is None:
            self.pii_fields = [
                "password",
                "token",
                "api_key",
                "secret",
                "credit_card",
                "ssn",
                "email",
                "phone",
                "address",
            ]


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, config: Optional[LoggingConfig] = None):
        super().__init__()
        self.config = config or LoggingConfig()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add timestamp
        if self.config.include_timestamp:
            log_data["timestamp"] = self.formatTime(record)

        # Add correlation ID from context
        if self.config.include_correlation_id:
            corr_id = _correlation_id.get()
            if corr_id:
                log_data["correlation_id"] = corr_id

        # Add OpenTelemetry trace ID
        if self.config.include_trace_id and OTEL_AVAILABLE:
            try:
                current_span = trace.get_current_span()
                if current_span:
                    trace_id = format(current_span.get_span_context().trace_id, "032x")
                    log_data["trace_id"] = trace_id
                    span_id = format(current_span.get_span_context().span_id, "016x")
                    log_data["span_id"] = span_id
            except Exception:
                pass

        # Add request context
        tenant = _tenant_id.get()
        if tenant:
            log_data["tenant_id"] = tenant

        user = _user_id.get()
        if user:
            log_data["user_id"] = user

        # Add extra fields from record
        if hasattr(record, "extra"):
            extra = record.extra
            if self.config.redact_pii:
                extra = self._redact_pii(extra)
            log_data.update(extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)

    def _redact_pii(self, data: dict[str, Any]) -> dict[str, Any]:
        """Redact PII fields from log data."""
        redacted = {}
        for key, value in data.items():
            lower_key = key.lower()
            if any(pii in lower_key for pii in self.config.pii_fields):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = value
        return redacted


class StructuredLogger:
    """Structured logger with correlation ID support."""

    def __init__(self, name: str, config: Optional[LoggingConfig] = None):
        self.name = name
        self.config = config or LoggingConfig()
        self._logger = logging.getLogger(name)
        self._setup_handler()

    def _setup_handler(self) -> None:
        """Setup JSON handler."""
        # Remove existing handlers
        self._logger.handlers = []

        # Create JSON handler
        handler = logging.StreamHandler(self.config.output)
        handler.setFormatter(JSONFormatter(self.config))
        self._logger.addHandler(handler)

        # Set level
        self._logger.setLevel(getattr(logging, self.config.level.upper()))

    def _log(self, level: int, message: str, extra: dict = None, exc_info: bool = False) -> None:
        """Internal log method."""
        extra_dict = extra or {}

        # Create log record with extra data
        record = self._logger.makeRecord(self.name, level, "", 0, message, (), None)
        record.extra = extra_dict  # type: ignore

        if exc_info:
            record.exc_info = sys.exc_info()

        self._logger.handle(record)

    def debug(self, message: str, extra: dict = None) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: dict = None) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: dict = None) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: dict = None, exc_info: bool = True) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, extra, exc_info)

    def critical(self, message: str, extra: dict = None, exc_info: bool = True) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra, exc_info)


def get_logger(name: str = "amos", config: Optional[LoggingConfig] = None) -> StructuredLogger:
    """Get structured logger instance."""
    return StructuredLogger(name, config)


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    _correlation_id.set(correlation_id)


def get_request_id() -> str:
    """Get current request ID."""
    return _request_id.get()


def set_request_id(request_id: str) -> None:
    """Set request ID for current context."""
    _request_id.set(request_id)


def get_context() -> dict[str, Any]:
    """Get current logging context."""
    return {
        "correlation_id": _correlation_id.get(),
        "request_id": _request_id.get(),
        "tenant_id": _tenant_id.get(),
        "user_id": _user_id.get(),
    }


def set_context(
    correlation_id: str = None, request_id: str = None, tenant_id: str = None, user_id: str = None
) -> None:
    """Set multiple context values at once."""
    if correlation_id:
        _correlation_id.set(correlation_id)
    if request_id:
        _request_id.set(request_id)
    if tenant_id:
        _tenant_id.set(tenant_id)
    if user_id:
        _user_id.set(user_id)


def clear_context() -> None:
    """Clear all context variables."""
    _correlation_id.set(None)
    _request_id.set(None)
    _tenant_id.set(None)
    _user_id.set(None)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic structured logging.

    Injects correlation IDs and logs request/response details.
    """

    def __init__(
        self,
        app: ASGIApp,
        log_requests: bool = True,
        log_responses: bool = True,
        correlation_id_header: str = "X-Correlation-ID",
        request_id_header: str = "X-Request-ID",
    ):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.correlation_id_header = correlation_id_header
        self.request_id_header = request_id_header
        self.logger = get_logger("amos.http")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with structured logging."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get(self.correlation_id_header)
        if not correlation_id:
            # Try to use OpenTelemetry trace ID
            if OTEL_AVAILABLE:
                try:
                    current_span = trace.get_current_span()
                    if current_span:
                        correlation_id = format(current_span.get_span_context().trace_id, "032x")
                except Exception:
                    pass

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Generate request ID
        request_id = request.headers.get(self.request_id_header) or str(uuid.uuid4())

        # Set context
        set_context(
            correlation_id=correlation_id,
            request_id=request_id,
            tenant_id=request.headers.get("X-Tenant-ID"),
            user_id=request.headers.get("X-User-ID"),
        )

        # Log request
        start_time = time.time()
        if self.log_requests:
            self.logger.info(
                "HTTP request started",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "query_params": str(request.query_params),
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
            )

        # Process request
        try:
            response = await call_next(request)

            # Add correlation ID to response
            response.headers[self.correlation_id_header] = correlation_id
            response.headers[self.request_id_header] = request_id

            # Log response
            duration_ms = (time.time() - start_time) * 1000
            if self.log_responses:
                self.logger.info(
                    "HTTP request completed",
                    extra={
                        "method": request.method,
                        "path": str(request.url.path),
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                    },
                )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "HTTP request failed",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
            )
            raise

        finally:
            # Clear context
            clear_context()


def add_structured_logging_middleware(
    app: Any, log_requests: bool = True, log_responses: bool = True
) -> bool:
    """
    Add structured logging middleware to FastAPI application.

    Args:
        app: FastAPI application
        log_requests: Log incoming requests
        log_responses: Log outgoing responses

    Returns:
        True if middleware added successfully
    """
    if not FASTAPI_AVAILABLE:
        print("⚠️  FastAPI not available. Cannot add structured logging middleware.")
        return False

    app.add_middleware(
        StructuredLoggingMiddleware, log_requests=log_requests, log_responses=log_responses
    )
    print("✅ Structured logging middleware added to FastAPI app")
    return True


# Convenience function for logging exceptions with full context
def log_exception(
    logger: StructuredLogger, message: str, exception: Exception, extra: dict = None
) -> None:
    """Log exception with full context."""
    context = get_context()
    context.update(extra or {})
    context["exception_type"] = type(exception).__name__
    context["exception_message"] = str(exception)

    logger.error(message, extra=context)


__all__ = [
    "StructuredLogger",
    "StructuredLoggingMiddleware",
    "LoggingConfig",
    "JSONFormatter",
    "get_logger",
    "get_correlation_id",
    "set_correlation_id",
    "get_request_id",
    "set_request_id",
    "get_context",
    "set_context",
    "clear_context",
    "add_structured_logging_middleware",
    "log_exception",
]

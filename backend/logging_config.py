"""
AMOS Logging Configuration

Structured logging with JSON output for production observability.
Implements the three pillars: logs, metrics, and traces.

Creator: Trang Phan
Version: 3.0.0
"""

import logging
import sys
import structlog
from typing import Any
import os

# Environment-based configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or console
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def configure_logging() -> None:
    """Configure structured logging for AMOS."""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL),
    )

    # Configure structlog
    shared_processors: List[Any] = [
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Format exceptions
        structlog.processors.format_exc_info,
    ]

    if LOG_FORMAT == "json":
        # Production: JSON format for log aggregation
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, LOG_LEVEL)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Development: Console format
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    pad_level=True,
                )
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, LOG_LEVEL)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Request logging middleware
class RequestLoggingMiddleware:
    """Middleware to log all requests with structured data."""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("amos.api.requests")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time
from typing import Set
from typing import Dict, List
        start_time = time.time()

        request_id = scope.get("headers", {}).get(b"x-request-id", b"").decode()
        method = scope["method"]
        path = scope["path"]
        client = scope.get("client")

        # Log request start
        self.logger.info(
            "request_started",
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client[0] if client else None,
        )

        # Capture response
        response_status = 200

        async def wrapped_send(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)

            duration = time.time() - start_time

            # Log request completion
            self.logger.info(
                "request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response_status,
                duration_ms=round(duration * 1000, 2),
            )

        except Exception as e:
            duration = time.time() - start_time

            # Log request error
            self.logger.error(
                "request_failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                exc_info=True,
            )
            raise


# Metrics collection
class MetricsCollector:
    """Collect application metrics for observability."""

    def __init__(self):
        self.logger = get_logger("amos.metrics")
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}

    def increment(self, metric_name: str, value: int = 1, tags: dict = None):
        """Increment a counter metric."""
        key = f"{metric_name}:{self._tags_to_str(tags)}"
        self._counters[key] = self._counters.get(key, 0) + value

        self.logger.info(
            "metric_counter",
            metric_name=metric_name,
            value=self._counters[key],
            tags=tags or {},
        )

    def gauge(self, metric_name: str, value: float, tags: dict = None):
        """Set a gauge metric."""
        key = f"{metric_name}:{self._tags_to_str(tags)}"
        self._gauges[key] = value

        self.logger.info(
            "metric_gauge",
            metric_name=metric_name,
            value=value,
            tags=tags or {},
        )

    def _tags_to_str(self, tags: dict) -> str:
        """Convert tags dict to string."""
        if not tags:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))


# Global metrics instance
metrics = MetricsCollector()


def log_system_event(event_type: str, data: dict) -> None:
    """Log a system event with structured data."""
    logger = get_logger("amos.system")
    logger.info(
        event_type,
        environment=ENVIRONMENT,
        **data
    )


def log_security_event(event_type: str, details: dict) -> None:
    """Log a security-related event."""
    logger = get_logger("amos.security")
    logger.warning(
        event_type,
        environment=ENVIRONMENT,
        **details
    )

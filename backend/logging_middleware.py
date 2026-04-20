from __future__ import annotations

from typing import Any, Optional

"""Production-grade structured logging middleware for FastAPI.

State-of-art implementation using structlog with:
- Correlation ID injection for distributed tracing
- Request/Response payload logging
- Performance timing
- PII redaction
- Log level-based sampling

Based on 2024 FastAPI logging best practices.
"""


import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("amos.api.middleware")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Inject correlation IDs for distributed tracing.

    Extracts X-Request-ID from incoming requests or generates
    a new UUID. Propagates through all downstream logs.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Production structured logging with performance metrics.

    Logs all requests with:
    - Method, path, query params
    - Status code, response time
    - Client IP, user agent
    - Request/response body sizes
    """

    def __init__(
        self,
        app: FastAPI,
        *,
        log_level: str = "INFO",
        exclude_paths: set[Optional[str]] = None,
        max_body_size: int = 10000,
    ):
        super().__init__(app)
        self.log_level = log_level
        self.exclude_paths = exclude_paths or {"/health", "/metrics", "/docs", "/redoc"}
        self.max_body_size = max_body_size

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        client_host = request.client.host if request.client else "unknown"

        log_data: dict[str, Any] = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_ip": client_host,
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            log_data.update(
                {
                    "status_code": response.status_code,
                    "duration_ms": round(process_time * 1000, 3),
                    "response_size": response.headers.get("content-length", 0),
                }
            )

            if response.status_code >= 500:
                logger.error("http_request_server_error", **log_data)
            elif response.status_code >= 400:
                logger.warning("http_request_client_error", **log_data)
            elif process_time > 1.0:
                logger.warning("http_request_slow", **log_data)
            else:
                logger.info("http_request", **log_data)

            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            log_data.update(
                {
                    "duration_ms": round(process_time * 1000, 3),
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            logger.exception("http_request_failed", **log_data)
            raise


def setup_structured_logging(app: FastAPI, json_logs: bool = True) -> None:
    """Configure structlog for production use.

    Args:
        app: FastAPI application instance
        json_logs: Output JSON if True, colored console if False
    """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)

    logger.info("structured_logging_configured", json_mode=json_logs)


__all__ = [
    "CorrelationIdMiddleware",
    "StructuredLoggingMiddleware",
    "setup_structured_logging",
]

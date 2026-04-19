"""FastAPI middleware for observability."""

import time
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, Request

from .logging import set_correlation_id
from .metrics import PerformanceMetrics


class ObservabilityMiddleware:
    """FastAPI middleware for automatic observability."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.metrics = PerformanceMetrics()

    async def __call__(
        self, scope: Any, receive: Callable[..., Any], send: Callable[..., Any]
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        correlation_id = request.headers.get("X-Correlation-ID", "")
        if correlation_id:
            set_correlation_id(correlation_id)

        self.metrics.start_request()
        start_time = time.perf_counter()

        response_sent = False
        status_code = 200

        async def wrapped_send(message: Any) -> None:  # type: ignore[misc]
            nonlocal response_sent, status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                response_sent = True
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception:
            status_code = 500
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.end_request(duration_ms, status_code)


def add_observability(app: FastAPI) -> None:
    """Add observability middleware to FastAPI app."""
    middleware = ObservabilityMiddleware(app)
    # Store original
    app.middleware_stack = middleware  # type: ignore

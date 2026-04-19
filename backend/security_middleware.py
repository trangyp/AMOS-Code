from typing import Any

"""Production Security Middleware for AMOS Backend.

Implements rate limiting, security headers, and request validation.
"""

import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiting middleware."""

    def __init__(self, app: Any, requests_per_minute: int = 60, burst_size: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        if client_ip in self.requests:
            self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        self.requests[client_ip].append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests for common attack patterns."""

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB
    SUSPICIOUS_PATTERNS = [
        "<script",
        "javascript:",
        "onerror=",
        "onload=",
        "eval(",
        "SELECT * FROM",
        "DROP TABLE",
        "DELETE FROM",
        ";--",
        "' OR '1'='1",
    ]

    async def dispatch(self, request: Request, call_next):
        # Check body size
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > self.MAX_BODY_SIZE:
                return JSONResponse(status_code=413, content={"detail": "Payload too large"})

        # Check for suspicious patterns in query params
        query_string = str(request.query_params)
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in query_string.lower():
                return JSONResponse(status_code=400, content={"detail": "Invalid input detected"})

        return await call_next(request)


def setup_security_middleware(app: FastAPI) -> None:
    """Apply all security middleware to the app."""

    # CORS - restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        max_age=600,
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)

    # Input validation
    app.add_middleware(InputValidationMiddleware)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    import structlog

    logger = structlog.get_logger("amos.api")

    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
        client=request.client.host if request.client else "unknown",
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with logging."""
    logger = structlog.get_logger("amos.api")

    logger.warning(
        "HTTP exception", status_code=exc.status_code, detail=exc.detail, path=request.url.path
    )

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

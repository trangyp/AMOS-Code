#!/usr/bin/env python3
"""AMOS Equation Application - Unified FastAPI Application Factory.

Production-grade FastAPI application integrating all middleware components:
- Security headers (CSP, HSTS, X-Frame-Options)
- Prometheus metrics with business tracking
- Rate limiting with Redis backend
- CORS configuration
- OpenTelemetry tracing
- Health checks (liveness, readiness, startup)
- API versioning (URL and header-based)
- Pydantic validation models
- Exception handling
- Request logging
- Graceful shutdown

Architecture Pattern: Application Factory with Lifespan Management
Middleware Stack (order matters - first added = first executed):
    1. CORS (outermost - handles preflight)
    2. Security Headers
    3. Request ID / Tracing
    4. Rate Limiting
    5. Metrics Collection
    6. Exception Handling (innermost - catches all)

Usage:
    from equation_app import create_app
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

Environment Variables:
    APP_ENV: Environment (development, staging, production)
    APP_DEBUG: Enable debug mode (default: false)
    APP_HOST: Bind host (default: 0.0.0.0)
    APP_PORT: Bind port (default: 8000)
    ENABLE_SECURITY: Enable security headers (default: true)
    ENABLE_METRICS: Enable Prometheus metrics (default: true)
    ENABLE_RATE_LIMIT: Enable rate limiting (default: true)
    ENABLE_TRACING: Enable OpenTelemetry tracing (default: true)
    REDIS_URL: Redis connection URL for rate limiting/cache
    API_VERSION_DEFAULT: Default API version (default: v1)
"""

import logging
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("amos_equation_app")

# FastAPI imports with graceful fallback
try:
    from fastapi import FastAPI, HTTPException, Request, Response, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, PlainTextResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore
    Request = None  # type: ignore
    Response = None  # type: ignore
    HTTPException = None  # type: ignore

# Import our production modules (with graceful degradation)
try:
    from equation_security import SecurityMiddleware, setup_cors

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    SecurityMiddleware = None  # type: ignore

try:
    from equation_metrics import MetricsMiddleware, instrument_app

    METRICS_AVAILABLE = False  # Note: instrument_app handles this
except ImportError:
    METRICS_AVAILABLE = False

try:
    from amos_rate_limiting import RateLimiter, RateLimitMiddleware

    RATE_LIMIT_AVAILABLE = True
except ImportError:
    RATE_LIMIT_AVAILABLE = False
    RateLimitMiddleware = None  # type: ignore

try:
    from equation_health import HealthCheckService, get_health_router

    HEALTH_AVAILABLE = True
except ImportError:
    HEALTH_AVAILABLE = False

try:
    from equation_tracing import get_tracer, setup_tracing

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

try:
    from equation_versioning import VersionRouter, setup_versioning

    VERSIONING_AVAILABLE = True
except ImportError:
    VERSIONING_AVAILABLE = False

try:
    from equation_schemas import (
        PYDANTIC_AVAILABLE,
        ErrorResponse,
        create_error_response,
    )

    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False

try:
    from equation_graphql import create_graphql_router, graphql_endpoint

    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

try:
    from equation_notifications import notification_router

    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Configuration from environment
_APP_ENV = os.getenv("APP_ENV", "production")
_APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"
_ENABLE_SECURITY = os.getenv("ENABLE_SECURITY", "true").lower() == "true"
_ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
_ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
_ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
_ENABLE_GRAPHQL = os.getenv("ENABLE_GRAPHQL", "true").lower() == "true"
_API_VERSION = os.getenv("API_VERSION_DEFAULT", "v1")


class ApplicationState:
    """Shared application state for lifespan management."""

    def __init__(self) -> None:
        self.started_at: float = 0.0
        self.health_service: Any = None
        self.rate_limiter: Any = None
        self.tracer: Any = None
        self.metrics_collector: Any = None

    def is_ready(self) -> bool:
        """Check if application is ready to serve requests."""
        return self.started_at > 0


# Global state instance
app_state = ApplicationState()


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown.

    Handles initialization and cleanup of all services.
    """
    # Startup
    logger.info("Starting AMOS Equation Application...")
    app_state.started_at = time.time()

    # Initialize health service
    if HEALTH_AVAILABLE:
        app_state.health_service = HealthCheckService()
        app_state.health_service.set_startup_complete()
        logger.info("Health check service initialized")

    # Initialize rate limiter
    if RATE_LIMIT_AVAILABLE and _ENABLE_RATE_LIMIT:
        app_state.rate_limiter = RateLimiter()
        logger.info("Rate limiter initialized")

    # Initialize tracing
    if TRACING_AVAILABLE and _ENABLE_TRACING:
        setup_tracing()
        logger.info("OpenTelemetry tracing initialized")

    # Initialize metrics
    if METRICS_AVAILABLE and _ENABLE_METRICS:
        logger.info("Prometheus metrics initialized")

    startup_time = time.time() - app_state.started_at
    logger.info(f"Application startup complete in {startup_time:.3f}s")

    yield

    # Shutdown
    logger.info("Shutting down AMOS Equation Application...")

    # Mark health service for shutdown
    if app_state.health_service:
        app_state.health_service.request_shutdown()
        logger.info("Health service marked for shutdown")

    # Wait for in-flight requests (configurable delay)
    await asyncio.sleep(2)

    logger.info("Application shutdown complete")


def create_app(
    title: str = "AMOS Equation API",
    description: str = "Unified Equation System with 1608+ mathematical functions",
    version: str = "2.0.0",
    debug: bool = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        title: API title for documentation
        description: API description
        version: API version
        debug: Enable debug mode (overrides env var)

    Returns:
        Configured FastAPI application
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required to create the application")

    # Determine debug mode
    is_debug = debug if debug is not None else _APP_DEBUG

    # Create app with lifespan
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        debug=is_debug,
        docs_url="/docs" if is_debug else None,
        redoc_url="/redoc" if is_debug else None,
        openapi_url="/openapi.json" if is_debug else None,
        lifespan=app_lifespan,
    )

    # Add middleware in correct order (reverse of execution)
    # 1. Exception handler (innermost - catches everything)
    _add_exception_handlers(app)

    # 2. CORS (outermost)
    _add_cors_middleware(app)

    # 3. Security headers
    if SECURITY_AVAILABLE and _ENABLE_SECURITY:
        app.add_middleware(SecurityMiddleware)
        logger.info("Security middleware added")

    # 4. Request ID / Tracing
    if TRACING_AVAILABLE and _ENABLE_TRACING:
        _add_tracing_middleware(app)

    # 5. Rate limiting
    if RATE_LIMIT_AVAILABLE and _ENABLE_RATE_LIMIT:
        _add_rate_limiting(app)

    # 6. Metrics (innermost before exception handler)
    if METRICS_AVAILABLE and _ENABLE_METRICS:
        _add_metrics(app)

    # Add routers
    _add_routers(app)

    # Setup versioning
    if VERSIONING_AVAILABLE:
        setup_versioning(app, default_version=_API_VERSION)
        logger.info("API versioning configured")

    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint with API information."""
        return {
            "name": title,
            "version": version,
            "description": description,
            "environment": _APP_ENV,
            "docs_url": "/docs" if is_debug else None,
            "health_url": "/health/live",
            "metrics_url": "/metrics" if _ENABLE_METRICS else None,
            "api_version": _API_VERSION,
            "features": {
                "security": _ENABLE_SECURITY and SECURITY_AVAILABLE,
                "metrics": _ENABLE_METRICS and METRICS_AVAILABLE,
                "rate_limiting": _ENABLE_RATE_LIMIT and RATE_LIMIT_AVAILABLE,
                "tracing": _ENABLE_TRACING and TRACING_AVAILABLE,
                "graphql": _ENABLE_GRAPHQL and GRAPHQL_AVAILABLE,
            },
        }

    # Add status endpoint
    @app.get("/status", tags=["Status"])
    async def status_endpoint() -> Dict[str, Any]:
        """Application status endpoint."""
        uptime = time.time() - app_state.started_at if app_state.started_at else 0
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "environment": _APP_ENV,
            "debug": is_debug,
        }

    logger.info(f"FastAPI application created: {title} v{version}")
    return app


def _add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware with secure defaults."""
    # Default CORS configuration
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*" if _APP_DEBUG else "").split(",")
    allowed_origins = [o.strip() for o in allowed_origins if o.strip()]

    if not allowed_origins:
        allowed_origins = ["*"] if _APP_DEBUG else []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "*",
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Version",
            "X-Client-Version",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-API-Version",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "Deprecation",
            "Sunset",
        ],
        max_age=600,  # 10 minutes
    )
    logger.info(f"CORS middleware added with origins: {allowed_origins}")


def _add_tracing_middleware(app: FastAPI) -> None:
    """Add OpenTelemetry tracing middleware."""
    if not TRACING_AVAILABLE:
        return

    @app.middleware("http")
    async def tracing_middleware(request: Request, call_next: Any) -> Response:
        """Add tracing to requests."""
        tracer = get_tracer()
        if tracer:
            with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", str(request.url))
                span.set_attribute("http.route", request.url.path)

                response = await call_next(request)

                span.set_attribute("http.status_code", response.status_code)
                return response
        else:
            return await call_next(request)

    logger.info("Tracing middleware added")


def _add_rate_limiting(app: FastAPI) -> None:
    """Add rate limiting middleware."""
    if not RATE_LIMIT_AVAILABLE:
        return

    # Default rate limits
    default_limit = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    verify_limit = int(os.getenv("RATE_LIMIT_VERIFY", "30"))

    app.add_middleware(
        RateLimitMiddleware,
        default_limit=default_limit,
        verify_limit=verify_limit,
    )
    logger.info(f"Rate limiting added: {default_limit}/min default, " f"{verify_limit}/min verify")


def _add_metrics(app: FastAPI) -> None:
    """Add Prometheus metrics instrumentation."""
    if not METRICS_AVAILABLE:
        return

    # Use the metrics module's instrument_app
    instrument_app(app)
    logger.info("Prometheus metrics instrumentation added")


def _add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc}")

        if SCHEMAS_AVAILABLE:
            error = create_error_response(
                error_code="VALIDATION_ERROR",
                error_message="Request validation failed",
                validation_error=exc,
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error.model_dump(),
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Request validation failed",
                    "detail": exc.errors(),
                },
            )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": f"HTTP_{exc.status_code}",
                "error_message": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions."""
        logger.exception(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_ERROR",
                "error_message": ("An internal error occurred" if not _APP_DEBUG else str(exc)),
            },
        )

    logger.info("Exception handlers added")


def _add_routers(app: FastAPI) -> None:
    """Add API routers for different endpoints."""
    # Health check router
    if HEALTH_AVAILABLE:
        health_router = get_health_router()
        app.include_router(health_router, prefix="/health", tags=["Health"])
        logger.info("Health router added at /health")

    # GraphQL router
    if GRAPHQL_AVAILABLE and _ENABLE_GRAPHQL:
        graphql_router = create_graphql_router()
        if graphql_router:
            app.include_router(
                graphql_router,
                prefix="/graphql",
                tags=["GraphQL"],
            )
            logger.info("GraphQL router added at /graphql")

    # WebSocket notification router
    if NOTIFICATIONS_AVAILABLE:
        app.include_router(
            notification_router,
            prefix="/ws",
            tags=["WebSocket"],
        )
        logger.info("Notification router added at /ws")

    # Equation API router (v1)
    _add_equation_routers(app)


def _add_equation_routers(app: FastAPI) -> None:
    """Add equation-specific API routers."""
    from fastapi import APIRouter

    router = APIRouter(prefix="/api/v1/equations", tags=["Equations"])

    @router.get("/")
    async def list_equations() -> Dict[str, Any]:
        """List available equations."""
        return {
            "equations": [],
            "count": 0,
            "note": "Integration with amos_superbrain_equation_bridge pending",
        }

    @router.post("/solve")
    async def solve_equation(request: Request) -> Dict[str, Any]:
        """Solve an equation."""
        return {"status": "pending", "note": "Integration pending"}

    @router.post("/verify")
    async def verify_equation(request: Request) -> Dict[str, Any]:
        """Verify an equation."""
        return {"status": "pending", "note": "Integration pending"}

    app.include_router(router)
    logger.info("Equation router added at /api/v1/equations")


# Import asyncio for lifespan
import asyncio


def main() -> None:
    """Main entry point for running the application."""

    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = _APP_DEBUG
    workers = 1 if reload else int(os.getenv("APP_WORKERS", "4"))

    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {_APP_DEBUG}")
    logger.info(f"Workers: {workers}")

    app = create_app()

    uvicorn.run(
        "equation_app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info",
    )


if __name__ == "__main__":
    main()

"""
AMOS Integrated FastAPI Application

Complete API with all components:
- REST API endpoints (/api/v1/...)
- WebSocket real-time communication
- LLM provider integration
- Agent task management
- System monitoring

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import secrets
from contextlib import asynccontextmanager

# Import API routers
from api import api_router

# Import configuration
from config import settings
from fastapi import Depends, FastAPI, HTTPException, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from websocket_handler import broadcast_system_metrics, websocket_agents, websocket_dashboard

# Security for API docs
security = HTTPBasic()


def verify_docs_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify API docs access credentials in production."""
    if not settings.docs_auth_required:
        return True

    is_correct_username = secrets.compare_digest(credentials.username, settings.DOCS_USERNAME or "")
    is_correct_password = secrets.compare_digest(credentials.password, settings.DOCS_PASSWORD or "")

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    env_mode = "PRODUCTION" if settings.is_production else "development"
    print(f"[AMOS] Starting up in {env_mode} mode...")
    print(f"[AMOS] API Docs: {'Protected' if settings.docs_auth_required else 'Open'}")
    print(f"[AMOS] CORS Origins: {settings.CORS_ORIGINS}")

    # Start background metrics broadcaster
    metrics_task = asyncio.create_task(broadcast_system_metrics())

    yield

    # Shutdown
    print("[AMOS] Shutting down...")
    metrics_task.cancel()


# Create FastAPI app with conditional docs
app = FastAPI(
    title="AMOS Brain API",
    description="Autonomous Multi-Agent Orchestration System",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)

# Protect API docs in production
if settings.docs_auth_required and settings.DOCS_ENABLED:
    # Re-add docs with authentication
    from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html(auth: bool = Depends(verify_docs_auth)):
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html(auth: bool = Depends(verify_docs_auth)):
        return get_redoc_html(openapi_url="/openapi.json", title=f"{app.title} - ReDoc")


# Import rate limiter
from rate_limiter import RateLimitMiddleware

# Rate limiting middleware (must be before CORS)
app.add_middleware(
    RateLimitMiddleware,
    exclude_paths=[
        "/health",
        "/health/live",
        "/health/ready",
        "/health/startup",
        "/health/full",
        "/docs",
        "/redoc",
        "/openapi.json",
    ],
)

# CORS middleware with environment-based config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)


# WebSocket endpoints
@app.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket):
    """Dashboard real-time WebSocket."""
    await websocket_dashboard(websocket)


@app.websocket("/ws/agents")
async def ws_agents(websocket: WebSocket):
    """Agent task real-time WebSocket."""
    await websocket_agents(websocket)


# Import health checks
from health_checks import (
    init_default_checks,
    run_full_health_check,
    run_liveness_check,
    run_readiness_check,
    run_startup_check,
)

# Initialize health checks on startup
init_default_checks(redis_url=settings.REDIS_URL)


# Health check endpoints
@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy", "version": "3.0.0"}


@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe - is the app running?"""
    return await run_liveness_check()


@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe - is the app ready for traffic?"""
    result = await run_readiness_check()

    # Return 503 if not ready
    if result["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=result)

    return result


@app.get("/health/startup")
async def startup():
    """Kubernetes startup probe - has the app finished starting?"""
    result = await run_startup_check()

    if result["status"] != "healthy":
        raise HTTPException(status_code=503, detail=result)

    return result


@app.get("/health/full")
async def full_health():
    """Comprehensive health check with all probes."""
    return await run_full_health_check()


# Root endpoint
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "AMOS Brain API",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api/v1",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_integrated:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS if settings.is_production else 1,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )

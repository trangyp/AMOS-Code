"""AMOS Integrated Main Application - Full Stack Orchestration.

The production-ready entry point that integrates all AMOS subsystems into a
unified FastAPI application with lifecycle management, monitoring, and API endpoints.

Features:
- Unified subsystem initialization
- Graceful startup and shutdown
- Comprehensive health monitoring
- API endpoint aggregation
- Background task orchestration
- Error handling and recovery

Architecture:
- Layer 1: FastAPI application core
- Layer 2: AI Systems Router (api_ai_systems)
- Layer 3: Brain Orchestrator (amos_brain)
- Layer 4: All AI subsystems (governance, cost, knowledge, etc.)

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations


import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import FastAPI components
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("⚠️  FastAPI not installed. Install with: pip install fastapi uvicorn")

# Import AI Systems Router
try:
    from api_ai_systems import ai_router, ai_systems_lifespan

    HAS_AI_SYSTEMS = True
except ImportError as e:
    HAS_AI_SYSTEMS = False
    print(f"⚠️  AI Systems not available: {e}")

# Import configuration

from config import get_settings


def create_amos_app() -> Any | None:
    """Create and configure the AMOS FastAPI application."""

    if not HAS_FASTAPI:
        return None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifecycle management."""
        print("\n" + "=" * 60)
        print("🚀 AMOS v3.0.0 - Cognitive Operating System Starting...")
        print("=" * 60)

        # Load settings
        settings = get_settings()
        app.state.settings = settings

        # Initialize AI systems if available
        if HAS_AI_SYSTEMS:
            try:
                async with ai_systems_lifespan(app):
                    print("✅ AI Systems initialized")
                    app.state.ai_initialized = True
            except Exception as e:
                print(f"⚠️  AI Systems initialization failed: {e}")
                app.state.ai_initialized = False
        else:
            print("⚠️  AI Systems not available")
            app.state.ai_initialized = False

        print("=" * 60)
        print("✅ AMOS Startup Complete")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Debug Mode: {settings.DEBUG}")
        print(f"   AI Systems: {'Active' if app.state.ai_initialized else 'Inactive'}")
        print("=" * 60 + "\n")

        yield

        # Shutdown
        print("\n" + "=" * 60)
        print("🛑 AMOS Shutting Down...")
        print("=" * 60)
        print("✅ Shutdown Complete\n")

    # Create FastAPI application
    app = FastAPI(
        title="AMOS - AI Cognitive Operating System",
        description="""
        AMOS v3.0.0 - Enterprise AI Agent Infrastructure

        **Features:**
        - AI Agent Management & Orchestration
        - Knowledge & Memory (RAG)
        - Reasoning & Planning (ReAct, CoT)
        - Multi-Agent Messaging
        - AI Governance & Safety
        - Cost Management & Budget Control
        - Plugin System
        - Observability & Tracing
        """,
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def configure_routes(app: FastAPI):
    """Configure all API routes."""

    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """AMOS root endpoint."""
        return {
            "name": "AMOS - AI Cognitive Operating System",
            "version": "3.0.0",
            "status": "operational",
            "creator": "Trang Phan",
            "year": 2026,
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "ai_systems": "/ai/*",
                "metrics": "/metrics",
            },
            "ai_systems": "active" if getattr(app.state, "ai_initialized", False) else "inactive",
        }

    # Health check
    @app.get("/health", tags=["System"])
    async def health_check():
        """System health check endpoint."""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "3.0.0",
            "subsystems": {},
        }

        # AI Systems health
        if HAS_AI_SYSTEMS and getattr(app.state, "ai_initialized", False):
            try:
                from amos_brain_orchestrator import get_health

                ai_health = await get_health()
                health["subsystems"]["ai_systems"] = ai_health
            except Exception as e:
                health["subsystems"]["ai_systems"] = {"status": "error", "error": str(e)}

        # Check overall status
        for subsystem, status in health["subsystems"].items():
            if isinstance(status, dict) and status.get("status") == "error":
                health["status"] = "degraded"
                break

        return health

    # Metrics endpoint
    @app.get("/metrics", tags=["System"])
    async def metrics():
        """System metrics endpoint."""
        metrics = {
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "3.0.0",
            "runtime": {"python_version": sys.version, "platform": sys.platform},
        }

        # AI metrics
        if HAS_AI_SYSTEMS and getattr(app.state, "ai_initialized", False):
            try:
                from amos_brain_orchestrator import amos_brain

                metrics["ai_systems"] = {
                    "agents": len(amos_brain.agents),
                    "tasks_queued": amos_brain.task_queue.qsize(),
                    "tasks_running": len(amos_brain.running_tasks),
                }
            except Exception as e:
                metrics["ai_systems"] = {"error": str(e)}

        return metrics

    # System info
    @app.get("/system/info", tags=["System"])
    async def system_info():
        """Detailed system information."""
        info = {
            "name": "AMOS",
            "full_name": "AI Cognitive Operating System",
            "version": "3.0.0",
            "creator": "Trang Phan",
            "year": 2026,
            "architecture": {
                "layers": 10,
                "subsystems": 11,
                "total_lines": "30,000+",
                "api_endpoints": "60+",
            },
            "capabilities": [
                "AI Agent Management",
                "Knowledge & Memory (RAG)",
                "Reasoning & Planning (ReAct, CoT)",
                "Multi-Agent Messaging",
                "AI Governance & Safety",
                "Cost Management & Budget Control",
                "Plugin System",
                "Observability & Tracing",
                "Kubernetes Orchestration",
                "DevOps & CI/CD",
            ],
            "technologies": [
                "Python 3.11+",
                "FastAPI",
                "React + TypeScript",
                "Kubernetes",
                "PostgreSQL",
                "Redis",
                "OpenTelemetry",
                "Ollama",
                "Sentence Transformers",
            ],
        }

        return info

    # AI Systems Router
    if HAS_AI_SYSTEMS:
        app.include_router(ai_router, prefix="/ai")
        print("✅ AI Systems Router mounted at /ai")

    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc),
                "path": str(request.url),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )


def main():
    """Main entry point."""

    # Create application
    app = create_amos_app()

    if app is None:
        print("❌ Failed to create AMOS application")
        return None

    # Configure routes
    configure_routes(app)

    return app


# Create application instance
amos_app = main()

if __name__ == "__main__":
    if HAS_FASTAPI and amos_app:
        import uvicorn

        # Get port from environment or default
        port = int(os.getenv("AMOS_PORT", 8000))
        host = os.getenv("AMOS_HOST", "0.0.0.0")
        reload = os.getenv("AMOS_RELOAD", "false").lower() == "true"

        print(f"\n🚀 Starting AMOS Server on {host}:{port}")
        print(f"   Docs: http://localhost:{port}/docs")
        print(f"   Health: http://localhost:{port}/health\n")

        uvicorn.run(
            "main_amos_integrated:amos_app", host=host, port=port, reload=reload, log_level="info"
        )
    else:
        print("❌ Cannot start server - FastAPI not available")
        sys.exit(1)

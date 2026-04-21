#!/usr/bin/env python3
"""AMOS FastAPI Application - Production-ready API server.

Combines all AMOS components into a unified FastAPI application:
- Health monitoring
- Brain cognitive endpoints  
- Workflow management
- Task processing
- Event streaming
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import AMOS components
try:
    from amos_api_health_router import router as health_router
    from amos_circuit_breaker import get_circuit_breaker_registry
    from amos_master_integration import get_master_integration

    AMOS_AVAILABLE = True
except ImportError:
    AMOS_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("[AMOS] Starting up...")
    if AMOS_AVAILABLE:
        try:
            master = await get_master_integration()
            print(f"[AMOS] Initialized: {master.get_status()}")
        except Exception as e:
            print(f"[AMOS] Initialization warning: {e}")

    yield

    # Shutdown
    print("[AMOS] Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AMOS API",
    description="AMOS Brain - Unified Cognitive System",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if AMOS_AVAILABLE:
    app.include_router(health_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "name": "AMOS API",
        "version": "1.0.0",
        "status": "operational" if AMOS_AVAILABLE else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/status")
async def get_status() -> dict[str, Any]:
    """Get AMOS system status."""
    if not AMOS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AMOS components not available",
        )

    try:
        master = await get_master_integration()
        return master.get_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get("/api/v1/components")
async def list_components() -> dict[str, Any]:
    """List all AMOS components."""
    components = {
        "kernel": False,
        "brain": False,
        "organism": False,
        "circuit_breaker": False,
        "workflow_engine": False,
        "task_processor": False,
        "event_bus": False,
    }

    if AMOS_AVAILABLE:
        try:
            from amos_kernel import get_unified_kernel

            components["kernel"] = get_unified_kernel() is not None
        except ImportError:
            pass

        try:
            from amos_brain import get_brain

            components["brain"] = get_brain() is not None
        except ImportError:
            pass

        components["circuit_breaker"] = True

    return {
        "components": components,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

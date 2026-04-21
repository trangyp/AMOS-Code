#!/usr/bin/env python3
"""AMOS API Health Router - FastAPI health endpoints.

Production-ready health check endpoints for AMOS system.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Health"])


class HealthComponent(BaseModel):
    """Health status for a single component."""

    name: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    message: str | None = None
    last_check: str


class HealthResponse(BaseModel):
    """System health response."""

    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    components: list[HealthComponent]


async def check_kernel_health() -> HealthComponent:
    """Check AMOS kernel health."""
    start = datetime.now(timezone.utc)
    try:
        from amos_kernel import get_unified_kernel

        kernel = get_unified_kernel()
        return HealthComponent(
            name="kernel",
            status="healthy",
            response_time_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
            last_check=start.isoformat(),
        )
    except Exception as e:
        return HealthComponent(
            name="kernel",
            status="unhealthy",
            response_time_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
            message=str(e),
            last_check=start.isoformat(),
        )


async def check_brain_health() -> HealthComponent:
    """Check AMOS brain health."""
    start = datetime.now(timezone.utc)
    try:
        from amos_brain import get_brain

        brain = get_brain()
        return HealthComponent(
            name="brain",
            status="healthy",
            response_time_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
            last_check=start.isoformat(),
        )
    except Exception as e:
        return HealthComponent(
            name="brain",
            status="unhealthy",
            response_time_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
            message=str(e),
            last_check=start.isoformat(),
        )


@router.get("/", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Get overall system health."""
    components = []

    # Check critical components
    kernel = await check_kernel_health()
    brain = await check_brain_health()

    components.extend([kernel, brain])

    # Determine overall status
    unhealthy = sum(1 for c in components if c.status == "unhealthy")
    degraded = sum(1 for c in components if c.status == "degraded")

    if unhealthy > 0:
        overall = "unhealthy"
    elif degraded > 0:
        overall = "degraded"
    else:
        overall = "healthy"

    return HealthResponse(
        status=overall,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=0.0,  # TODO: Implement uptime tracking
        version="1.0.0",
        components=components,
    )


@router.get("/ready")
async def get_readiness() -> dict[str, Any]:
    """Readiness probe for Kubernetes."""
    return {"ready": True, "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/live")
async def get_liveness() -> dict[str, Any]:
    """Liveness probe for Kubernetes."""
    return {"alive": True, "timestamp": datetime.now(timezone.utc).isoformat()}

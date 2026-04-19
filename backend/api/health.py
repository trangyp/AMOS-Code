"""
AMOS Health API Endpoints - SuperBrain Governance Monitoring
Exposes health checks for CloudWatch and external monitoring systems

Version: 3.1.0
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Any, Dict

from backend.health_checks import (
    init_default_checks,
    run_readiness_check,
    run_liveness_check,
    get_health_checks,
)

router = APIRouter(prefix="/health", tags=["health"])


@router.on_event("startup")
async def startup_event():
    """Initialize health checks on startup."""
    init_default_checks()


@router.get("/live")
async def liveness_probe() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is running.
    """
    result = await run_liveness_check()
    return result


@router.get("/ready")
async def readiness_probe() -> JSONResponse:
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if all dependencies are ready, 503 otherwise.
    """
    result = await run_readiness_check()

    # Check if any critical checks failed
    critical_checks = [c for c in result.get("checks", []) if c.get("critical")]
    failed_critical = [c for c in critical_checks if c.get("status") != "healthy"]

    if failed_critical:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "failed_checks": [c["name"] for c in failed_critical],
                "details": result,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "checks": result,
        },
    )


@router.get("/superbrain")
async def superbrain_health() -> JSONResponse:
    """
    SuperBrain governance health endpoint.
    Monitored by CloudWatch for 4,644 features status.
    """
    checks = get_health_checks()

    # Find SuperBrain governance check
    superbrain_check = None
    for check in checks:
        if check.name == "superbrain_governance":
            superbrain_check = check
            break

    if not superbrain_check:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "component": "superbrain_governance",
                "message": "SuperBrain governance check not registered",
                "governed_systems": 0,
            },
        )

    # Run the check
    result = await superbrain_check.run()

    # Return appropriate status code
    if result["status"] == "healthy":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "component": "superbrain_governance",
                "version": "2.0.0",
                "message": result["message"],
                "governed_systems": len(superbrain_check.integrated_systems),
                "systems": superbrain_check.integrated_systems,
                "response_time_ms": result["response_time_ms"],
                "last_check": result["last_check"],
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "component": "superbrain_governance",
                "message": result["message"],
                "governed_systems": 0,
                "response_time_ms": result.get("response_time_ms"),
                "last_check": result.get("last_check"),
            },
        )


@router.get("")
async def full_health_check() -> JSONResponse:
    """
    Comprehensive health check endpoint.
    Returns status of all registered health checks.
    """
    from backend.health_checks import run_all_checks

    results = await run_all_checks()

    # Determine overall status
    unhealthy_critical = [
        c for c in results.get("checks", []) if c.get("critical") and c.get("status") != "healthy"
    ]

    if unhealthy_critical:
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif any(c.get("status") != "healthy" for c in results.get("checks", [])):
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK

    return JSONResponse(
        status_code=http_status,
        content={
            "status": overall_status,
            "timestamp": results.get("timestamp"),
            "uptime_seconds": results.get("uptime_seconds"),
            "total_checks": len(results.get("checks", [])),
            "failed_critical": len(unhealthy_critical),
            "checks": results.get("checks", []),
        },
    )

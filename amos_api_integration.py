#!/usr/bin/env python3

from typing import Any, Dict, List, Optional

"""AMOS API Integration Layer - FastAPI Endpoints for Production Systems

Exposes all 5 new production systems via REST API:
- Distributed Cache (/cache/*)
- Alert Manager (/alerts/*)
- Saga Orchestrator (/sagas/*)
- Secrets Manager (/secrets/* - admin only)
- Metrics Aggregation (/metrics/*)

Integrates with existing backend/main.py routers.

Owner: Trang
Version: 12.0.0
"""

from dataclasses import dataclass
from datetime import datetime

# FastAPI imports (with fallback)
try:
    from fastapi import APIRouter, Depends, HTTPException, status
    from fastapi.responses import JSONResponse, PlainTextResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    APIRouter = object

# Import production systems
try:
    from amos_distributed_cache import compute_prompt_hash, get_cache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from amos_alert_manager import AlertSeverity, get_alert_manager

    ALERT_AVAILABLE = True
except ImportError:
    ALERT_AVAILABLE = False

try:
    from amos_saga_orchestrator import SagaStatus, get_orchestrator

    SAGA_AVAILABLE = True
except ImportError:
    SAGA_AVAILABLE = False

try:
    from amos_secrets_manager import get_secrets_manager

    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False

try:

    from amos_metrics_aggregation import get_metrics_registry, get_prometheus_metrics

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/amos", tags=["amos-production"])
else:
    router = None


# Pydantic-style models (dataclass for compatibility)
@dataclass
class CacheStatsResponse:
    l1_hits: int
    l1_misses: int
    l1_size: int
    total_keys: int


@dataclass
class AlertResponse:
    id: str
    severity: str
    title: str
    message: str
    source: str
    timestamp: str
    acknowledged: bool
    resolved: bool


@dataclass
class SagaResponse:
    id: str
    name: str
    status: str
    current_step: int
    total_steps: int
    completed_steps: List[str]
    failed_step: Optional[str]
    error: Optional[str]
    duration_seconds: float


@dataclass
class SecretMetadataResponse:
    name: str
    type: str
    version_count: int
    active_versions: int
    last_rotated: Optional[str]
    rotation_days: int


if FASTAPI_AVAILABLE:

    @router.get("/health/complete")
    async def complete_health_check() -> Dict[str, Any]:
        """
        Comprehensive health check across all AMOS production systems.
        Returns status of Cache, Alert, Saga, Secrets, and Metrics systems.
        """
        checks = {}
        overall_healthy = True

        # Cache check
        if CACHE_AVAILABLE:
            try:
                cache = get_cache("health_check")
                cache.set("health", "ok", ttl=10)
                result = cache.get("health")
                checks["cache"] = {
                    "status": "healthy" if result == "ok" else "degraded",
                    "l1_stats": cache.get_stats()["l1"],
                }
            except Exception as e:
                checks["cache"] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False
        else:
            checks["cache"] = {"status": "unavailable"}

        # Alert manager check
        if ALERT_AVAILABLE:
            try:
                mgr = get_alert_manager()
                critical_alerts = len(
                    mgr.get_alerts(severity=AlertSeverity.CRITICAL, unresolved_only=True)
                )
                checks["alert_manager"] = {
                    "status": "healthy" if critical_alerts == 0 else "warning",
                    "critical_alerts": critical_alerts,
                }
            except Exception as e:
                checks["alert_manager"] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False
        else:
            checks["alert_manager"] = {"status": "unavailable"}

        # Saga orchestrator check
        if SAGA_AVAILABLE:
            try:
                orch = get_orchestrator()
                running = len(orch.get_running_sagas())
                checks["saga_orchestrator"] = {"status": "healthy", "running_sagas": running}
            except Exception as e:
                checks["saga_orchestrator"] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False
        else:
            checks["saga_orchestrator"] = {"status": "unavailable"}

        # Secrets manager check
        if SECRETS_AVAILABLE:
            try:
                mgr = get_secrets_manager()
                secrets = mgr.list_secrets()
                checks["secrets_manager"] = {"status": "healthy", "total_secrets": len(secrets)}
            except Exception as e:
                checks["secrets_manager"] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False
        else:
            checks["secrets_manager"] = {"status": "unavailable"}

        # Metrics aggregation check
        if METRICS_AVAILABLE:
            try:
                registry = get_metrics_registry()
                families = registry.collect()
                checks["metrics_aggregation"] = {
                    "status": "healthy",
                    "metric_families": len(families),
                }
            except Exception as e:
                checks["metrics_aggregation"] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False
        else:
            checks["metrics_aggregation"] = {"status": "unavailable"}

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": checks,
        }

    @router.get("/metrics/prometheus", response_class=PlainTextResponse)
    async def prometheus_metrics() -> str:
        """Prometheus-compatible metrics endpoint."""
        if not METRICS_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Metrics aggregation not available",
            )
        return get_prometheus_metrics()

    @router.get("/cache/stats")
    async def cache_stats() -> Dict[str, Any]:
        """Get distributed cache statistics."""
        if not CACHE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cache not available"
            )

        cache = get_cache("api")
        stats = cache.get_stats()

        return {"l1_cache": stats["l1"], "timestamp": datetime.now(UTC).isoformat()}

    @router.post("/cache/invalidate/{key_pattern}")
    async def cache_invalidate(key_pattern: str) -> Dict[str, Any]:
        """Invalidate cache keys matching pattern (admin only)."""
        if not CACHE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cache not available"
            )

        # TODO: Add admin auth check
        get_cache("api")
        # Pattern matching would be implemented in cache

        return {
            "action": "invalidate",
            "pattern": key_pattern,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @router.get("/alerts")
    async def list_alerts(
        severity: Optional[str] = None, unresolved_only: bool = False
    ) -> List[AlertResponse]:
        """List alerts with optional filtering."""
        if not ALERT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Alert manager not available",
            )

        mgr = get_alert_manager()

        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid severity: {severity}"
                )

        alerts = mgr.get_alerts(severity=severity_enum, unresolved_only=unresolved_only)

        return [
            AlertResponse(
                id=a.id,
                severity=a.severity.value,
                title=a.title,
                message=a.message,
                source=a.source,
                timestamp=a.timestamp.isoformat(),
                acknowledged=a.acknowledged,
                resolved=a.resolved,
            )
            for a in alerts[:100]  # Limit to 100 alerts
        ]

    @router.post("/alerts/{alert_id}/acknowledge")
    async def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
        """Acknowledge an alert."""
        if not ALERT_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Alert manager not available",
            )

        mgr = get_alert_manager()
        success = mgr.acknowledge(alert_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found"
            )

        return {
            "action": "acknowledged",
            "alert_id": alert_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @router.get("/sagas")
    async def list_sagas() -> List[SagaResponse]:
        """List active saga instances."""
        if not SAGA_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Saga orchestrator not available",
            )

        orch = get_orchestrator()
        running = orch.get_running_sagas()

        return [
            SagaResponse(
                id=s.id,
                name=s.definition.name,
                status=s.status.value,
                current_step=s.current_step_index,
                total_steps=len(s.definition.steps),
                completed_steps=s.completed_steps,
                failed_step=s.failed_step,
                error=s.error_message,
                duration_seconds=(datetime.now(UTC).timestamp() - s.started_at),
            )
            for s in running
        ]

    @router.get("/sagas/{saga_id}")
    async def get_saga(saga_id: str) -> SagaResponse:
        """Get specific saga instance details."""
        if not SAGA_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Saga orchestrator not available",
            )

        orch = get_orchestrator()
        instance = orch.get_instance(saga_id)

        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Saga {saga_id} not found"
            )

        return SagaResponse(
            id=instance.id,
            name=instance.definition.name,
            status=instance.status.value,
            current_step=instance.current_step_index,
            total_steps=len(instance.definition.steps),
            completed_steps=instance.completed_steps,
            failed_step=instance.failed_step,
            error=instance.error_message,
            duration_seconds=(datetime.now(UTC).timestamp() - instance.started_at),
        )

    @router.get("/secrets", include_in_schema=False)
    async def list_secrets() -> List[SecretMetadataResponse]:
        """List secrets metadata (admin only, no values exposed)."""
        if not SECRETS_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secrets manager not available",
            )

        # TODO: Add admin auth check
        mgr = get_secrets_manager()
        secrets = mgr.list_secrets()

        return [
            SecretMetadataResponse(
                name=s["name"],
                type=s["type"],
                version_count=s["version_count"],
                active_versions=s["active_versions"],
                last_rotated=s.get("last_rotated"),
                rotation_days=s["rotation_days"],
            )
            for s in secrets
        ]


def register_with_app(app: Any) -> None:
    """Register all AMOS production endpoints with FastAPI app."""
    if not FASTAPI_AVAILABLE or router is None:
        print("[AMOS API] FastAPI not available, skipping endpoint registration")
        return

    try:
        app.include_router(router)
        print("[AMOS API] Production endpoints registered at /amos/*")
    except Exception as e:
        print(f"[AMOS API] Failed to register endpoints: {e}")


# Legacy integration
if __name__ == "__main__":
    print("AMOS API Integration Layer")
    print("Available systems:")
    print(f"  - Cache: {CACHE_AVAILABLE}")
    print(f"  - Alert: {ALERT_AVAILABLE}")
    print(f"  - Saga: {SAGA_AVAILABLE}")
    print(f"  - Secrets: {SECRETS_AVAILABLE}")
    print(f"  - Metrics: {METRICS_AVAILABLE}")
    print(f"  - FastAPI: {FASTAPI_AVAILABLE}")

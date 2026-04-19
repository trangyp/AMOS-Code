from typing import Any

"""Brain Dashboard API - Real-time analytics and control for AMOS Brain.

Provides endpoints for:
- Reasoning history and analytics
- Cognitive cycle monitoring
- Brain health metrics
- Real-time dashboard data
"""
from __future__ import annotations


import sys
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "clawspring" / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

router = APIRouter(prefix="/api/v1/brain-dashboard", tags=["Brain Dashboard"])

# Lazy imports
_brain_available: bool | None = None
_dashboard_class: Any = None


def _check_brain() -> bool:
    """Check if brain dashboard is available."""
    global _brain_available, _dashboard_class
    if _brain_available is not None:
        return _brain_available

    try:
        from amos_brain.dashboard import BrainDashboard

        _dashboard_class = BrainDashboard
        _brain_available = True
        return True
    except ImportError:
        _brain_available = False
        return False


# ============================================================================
# Response Models
# ============================================================================


class BrainHealthMetrics(BaseModel):
    """Brain system health metrics."""

    status: str
    kernel_available: bool
    memory_entries: int
    last_activity: str | None
    cognitive_cycles_today: int
    avg_response_time_ms: float


class ReasoningSummary(BaseModel):
    """Summary of reasoning activity."""

    total_decisions: int
    rule_of_two_applied: int
    rule_of_four_applied: int
    avg_confidence: float
    compliance_rate: float


class CognitiveCycleEntry(BaseModel):
    """Single cognitive cycle entry."""

    timestamp: str
    observation_type: str
    goal_type: str
    status: str
    legality_score: float
    sigma: float
    latency_ms: float


class DomainPattern(BaseModel):
    """Domain usage pattern."""

    domain: str
    count: int
    avg_confidence: float
    trend: str


class BrainDashboardResponse(BaseModel):
    """Full dashboard response."""

    timestamp: str
    health: BrainHealthMetrics
    summary: ReasoningSummary
    recent_cycles: list[CognitiveCycleEntry]
    domain_patterns: list[DomainPattern]
    insights: list[str]


class AnalyticsRequest(BaseModel):
    """Request for analytics data."""

    days: int = Field(default=7, ge=1, le=90)
    include_charts: bool = True


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/health", response_model=BrainHealthMetrics)
async def get_brain_health() -> BrainHealthMetrics:
    """Get current brain health metrics."""
    if not _check_brain():
        return BrainHealthMetrics(
            status="unavailable",
            kernel_available=False,
            memory_entries=0,
            last_activity=None,
            cognitive_cycles_today=0,
            avg_response_time_ms=0.0,
        )

    try:
        # Try to get real metrics from brain
        from amos_brain.memory import get_brain_memory

        memory = get_brain_memory()
        history = memory.get_reasoning_history(limit=100)

        # Calculate metrics
        today = datetime.now(UTC).date()
        today_count = sum(
            1
            for h in history
            if datetime.fromisoformat(h.get("timestamp", "1970-01-01")).date() == today
        )

        return BrainHealthMetrics(
            status="healthy",
            kernel_available=True,
            memory_entries=len(history),
            last_activity=history[0].get("timestamp") if history else None,
            cognitive_cycles_today=today_count,
            avg_response_time_ms=45.0,  # Placeholder
        )
    except Exception:
        return BrainHealthMetrics(
            status="degraded",
            kernel_available=True,
            memory_entries=0,
            last_activity=None,
            cognitive_cycles_today=0,
            avg_response_time_ms=0.0,
        )


@router.get("/summary", response_model=ReasoningSummary)
async def get_reasoning_summary(days: int = Query(default=7, ge=1, le=90)) -> ReasoningSummary:
    """Get reasoning summary for the specified period."""
    if not _check_brain():
        return ReasoningSummary(
            total_decisions=0,
            rule_of_two_applied=0,
            rule_of_four_applied=0,
            avg_confidence=0.0,
            compliance_rate=0.0,
        )

    try:
        dashboard = _dashboard_class()
        report = dashboard.generate_report(days=days, include_charts=False)
        summary = report.get("summary", {})

        return ReasoningSummary(
            total_decisions=summary.get("total_decisions", 0),
            rule_of_two_applied=summary.get("rule_of_two_compliance", {}).get("count", 0),
            rule_of_four_applied=summary.get("rule_of_four_compliance", {}).get("count", 0),
            avg_confidence=summary.get("avg_confidence", 0.0),
            compliance_rate=summary.get("compliance_rate", 0.0),
        )
    except Exception:
        return ReasoningSummary(
            total_decisions=0,
            rule_of_two_applied=0,
            rule_of_four_applied=0,
            avg_confidence=0.0,
            compliance_rate=0.0,
        )


@router.get("/recent-cycles", response_model=list[CognitiveCycleEntry])
async def get_recent_cycles(
    limit: int = Query(default=10, ge=1, le=100),
) -> list[CognitiveCycleEntry]:
    """Get recent cognitive cycle entries."""
    if not _check_brain():
        return []

    try:
        memory = get_brain_memory()
        history = memory.get_reasoning_history(limit=limit)

        cycles = []
        for h in history:
            cycles.append(
                CognitiveCycleEntry(
                    timestamp=h.get("timestamp", datetime.now(UTC).isoformat()),
                    observation_type=h.get("observation_type", "unknown"),
                    goal_type=h.get("goal_type", "unknown"),
                    status=h.get("status", "unknown"),
                    legality_score=h.get("legality_score", 0.0),
                    sigma=h.get("sigma", 0.0),
                    latency_ms=h.get("latency_ms", 0.0),
                )
            )
        return cycles
    except Exception:
        return []


@router.get("/domain-patterns", response_model=list[DomainPattern])
async def get_domain_patterns(days: int = Query(default=7, ge=1, le=90)) -> list[DomainPattern]:
    """Get domain usage patterns."""
    if not _check_brain():
        return []

    try:
        dashboard = _dashboard_class()
        report = dashboard.generate_report(days=days, include_charts=False)
        patterns = report.get("domain_patterns", {})

        result = []
        for domain, data in patterns.items():
            result.append(
                DomainPattern(
                    domain=domain,
                    count=data.get("count", 0),
                    avg_confidence=data.get("avg_confidence", 0.0),
                    trend=data.get("trend", "stable"),
                )
            )
        return sorted(result, key=lambda x: x.count, reverse=True)
    except Exception:
        return []


@router.get("/insights")
async def get_insights(days: int = Query(default=7, ge=1, le=90)) -> dict[str, Any]:
    """Get AI-generated insights from brain activity."""
    if not _check_brain():
        return {"insights": [], "status": "brain_unavailable"}

    try:
        dashboard = _dashboard_class()
        report = dashboard.generate_report(days=days, include_charts=False)
        insights = report.get("insights", [])

        return {
            "insights": insights,
            "generated_at": datetime.now(UTC).isoformat(),
            "period_days": days,
            "status": "success",
        }
    except Exception as e:
        return {
            "insights": [],
            "status": "error",
            "error": str(e),
        }


@router.get("/full", response_model=BrainDashboardResponse)
async def get_full_dashboard(days: int = Query(default=7, ge=1, le=90)) -> BrainDashboardResponse:
    """Get complete dashboard data in one request."""
    health = await get_brain_health()
    summary = await get_reasoning_summary(days=days)
    cycles = await get_recent_cycles(limit=10)
    domains = await get_domain_patterns(days=days)
    insights_data = await get_insights(days=days)

    return BrainDashboardResponse(
        timestamp=datetime.now(UTC).isoformat(),
        health=health,
        summary=summary,
        recent_cycles=cycles,
        domain_patterns=domains,
        insights=insights_data.get("insights", []),
    )


@router.post("/analytics")
async def get_analytics(request: AnalyticsRequest) -> dict[str, Any]:
    """Get detailed analytics report."""
    if not _check_brain():
        raise HTTPException(status_code=503, detail="Brain dashboard not available")

    try:
        dashboard = _dashboard_class()
        report = dashboard.generate_report(days=request.days, include_charts=request.include_charts)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@router.get("/realtime")
async def get_realtime_data() -> dict[str, Any]:
    """Get real-time brain metrics for live dashboard updates."""
    if not _check_brain():
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "unavailable",
            "metrics": {},
        }

    try:
        memory = get_brain_memory()
        history = memory.get_reasoning_history(limit=1)

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "active",
            "metrics": {
                "last_activity": history[0].get("timestamp") if history else None,
                "memory_size": len(memory.get_reasoning_history(limit=1000)),
                "cycle_rate": "calculating",  # Would need time-series data
            },
        }
    except Exception as e:
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "error",
            "error": str(e),
        }

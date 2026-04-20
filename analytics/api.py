"""AMOS Analytics API Endpoints.

REST API for business intelligence and reporting.

Author: AMOS Analytics Team
Version: 2.0.0
"""

from datetime import datetime, timezone
UTC = timezone.utc, timedelta, timezone
from typing import Any

UTC = UTC

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from analytics.warehouse import AnalyticsWarehouse, MetricType

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Pydantic Models
class TimeSeriesResponse(BaseModel):
    metric_type: str
    granularity: str
    points: list[dict[str, Any]]
    start_time: datetime
    end_time: datetime


class DashboardMetrics(BaseModel):
    period: str
    api_requests: list[dict[str, Any]]
    active_users: dict[str, Any]
    equations_summary: dict[str, int]
    performance: dict[str, Any]
    generated_at: datetime


class WeeklyReport(BaseModel):
    period: str
    summary: dict[str, Any]
    metrics: DashboardMetrics
    week_over_week_change: dict[str, Any]


# Dependency injection
def get_warehouse() -> AnalyticsWarehouse:
    """Get analytics warehouse instance."""
    from config import settings

    return AnalyticsWarehouse(settings.ANALYTICS_DATABASE_URL)


# API Endpoints
@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard(
    days: int = Query(default=7, ge=1, le=90),
    warehouse: AnalyticsWarehouse = Depends(get_warehouse),
) -> DashboardMetrics:
    """Get dashboard metrics for specified period."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    metrics = await warehouse.get_dashboard_metrics(start, end)

    return DashboardMetrics(
        period=f"last_{days}_days",
        api_requests=[asdict(p) for p in metrics["api_requests"]],
        active_users=metrics["active_users"],
        equations_summary=metrics["equations_created"],
        performance={
            "latency": metrics["avg_latency"],
            "error_rate": metrics["error_rate"],
        },
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/timeseries/{metric_type}", response_model=TimeSeriesResponse)
async def get_time_series(
    metric_type: str,
    hours: int = Query(default=24, ge=1, le=168),
    granularity: str = Query(default="hour", regex="^(hour|day)$"),
    warehouse: AnalyticsWarehouse = Depends(get_warehouse),
) -> TimeSeriesResponse:
    """Get time series data for a metric."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    metric_enum = MetricType(metric_type)
    points = await warehouse.get_time_series(metric_enum, start, end, granularity)

    return TimeSeriesResponse(
        metric_type=metric_type,
        granularity=granularity,
        points=[{"timestamp": p.timestamp, "value": p.value, "label": p.label} for p in points],
        start_time=start,
        end_time=end,
    )


@router.get("/aggregations/{metric_type}")
async def get_aggregations(
    metric_type: str,
    period: str = Query(default="day", regex="^(day|week|month)$"),
    lookback_days: int = Query(default=30, ge=7, le=365),
    warehouse: AnalyticsWarehouse = Depends(get_warehouse),
) -> dict[str, Any]:
    """Get aggregated metrics."""
    metric_enum = MetricType(metric_type)
    aggregations = await warehouse.get_aggregated_metrics(metric_enum, period, lookback_days)

    return {
        "metric_type": metric_type,
        "period": period,
        "lookback_days": lookback_days,
        "data": [asdict(a) for a in aggregations],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/report/weekly", response_model=WeeklyReport)
async def get_weekly_report(
    warehouse: AnalyticsWarehouse = Depends(get_warehouse),
) -> WeeklyReport:
    """Generate weekly business report."""
    from analytics.warehouse import AnalyticsReporter

    reporter = AnalyticsReporter(warehouse)
    report = await reporter.generate_weekly_report()

    return WeeklyReport(
        period=report["period"],
        summary={
            "active_users": report["metrics"]["active_users"],
            "equations": report["metrics"]["equations_created"],
        },
        metrics=DashboardMetrics(
            period="last_7_days",
            api_requests=[],
            active_users=report["metrics"]["active_users"],
            equations_summary=report["metrics"]["equations_created"],
            performance=report["metrics"].get("avg_latency", {}),
            generated_at=datetime.now(timezone.utc),
        ),
        week_over_week_change=report["comparison"],
    )


@router.get("/health")
async def analytics_health(
    warehouse: AnalyticsWarehouse = Depends(get_warehouse),
) -> dict[str, Any]:
    """Health check for analytics system."""
    try:
        # Try to get recent events count
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)

        metrics = await warehouse.get_dashboard_metrics(start, end)

        return {
            "status": "healthy",
            "recent_events": len(metrics.get("api_requests", [])),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def asdict(obj):
    """Convert dataclass to dict."""

    return dc_asdict(obj)

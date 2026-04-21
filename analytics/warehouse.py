"""AMOS Equation System - Data Warehouse & Analytics.

Analytics pipeline for business intelligence:
- Event streaming to data warehouse
- Aggregated metrics computation
- Reporting API endpoints
- Data export for external BI tools

Author: AMOS Analytics Team
Version: 2.0.0
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MetricType(str, Enum):
    """Types of analytics metrics."""

    API_REQUEST = "api_request"
    API_LATENCY = "api_latency"
    API_ERROR = "api_error"
    USER_ACTIVE = "user_active"
    USER_SIGNUP = "user_signup"
    EQUATION_CREATED = "equation_created"
    EQUATION_VERIFIED = "equation_verified"
    TASK_COMPLETED = "task_completed"
    WEBHOOK_SENT = "webhook_sent"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"


class AnalyticsEvent(Base):
    """Analytics event storage."""

    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user_id = Column(String(36), index=True)
    session_id = Column(String(64))
    metadata_json = Column(String(1000))  # JSON blob for flexible data
    value = Column(Float)  # Numeric value for metrics


@dataclass
class TimeSeriesPoint:
    """Single point in time series."""

    timestamp: datetime
    value: float
    label: str


@dataclass
class MetricAggregation:
    """Aggregated metric result."""

    metric_type: str
    period: str  # hour, day, week, month
    start_time: datetime
    end_time: datetime
    total: float
    average: float
    minimum: float
    maximum: float
    count: int
    unique_users: int = None


class AnalyticsWarehouse:
    """Analytics data warehouse."""

    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)

    async def initialize(self):
        """Create analytics tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def track_event(
        self,
        event_type: MetricType,
        user_id: str = None,
        value: float = None,
        metadata: dict = None,
        session_id: str = None,
    ) -> None:
        """Track an analytics event."""
        import json

        event = AnalyticsEvent(
            event_type=event_type.value,
            user_id=user_id,
            session_id=session_id,
            value=value,
            metadata_json=json.dumps(metadata) if metadata else None,
        )

        async with AsyncSession(self.engine) as session:
            session.add(event)
            await session.commit()

    async def get_time_series(
        self,
        metric_type: MetricType,
        start: datetime,
        end: datetime,
        granularity: str = "hour",  # hour, day
    ) -> list[TimeSeriesPoint]:
        """Get time series data."""
        if granularity == "hour":
            trunc_func = func.date_trunc("hour", AnalyticsEvent.timestamp)
        else:
            trunc_func = func.date_trunc("day", AnalyticsEvent.timestamp)

        stmt = (
            select(
                trunc_func.label("bucket"),
                func.sum(AnalyticsEvent.value).label("total"),
                func.count().label("count"),
            )
            .where(AnalyticsEvent.event_type == metric_type.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
            .group_by("bucket")
            .order_by("bucket")
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            rows = result.all()

        return [
            TimeSeriesPoint(
                timestamp=row.bucket,
                value=float(row.total or 0),
                label=f"{row.count} events",
            )
            for row in rows
        ]

    async def get_aggregated_metrics(
        self,
        metric_type: MetricType,
        period: str = "day",
        lookback_days: int = 30,
    ) -> list[MetricAggregation]:
        """Get aggregated metrics for a period."""
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=lookback_days)

        if period == "day":
            trunc_func = func.date_trunc("day", AnalyticsEvent.timestamp)
        elif period == "week":
            trunc_func = func.date_trunc("week", AnalyticsEvent.timestamp)
        else:
            trunc_func = func.date_trunc("month", AnalyticsEvent.timestamp)

        stmt = (
            select(
                trunc_func.label("period_start"),
                func.sum(AnalyticsEvent.value).label("total"),
                func.avg(AnalyticsEvent.value).label("average"),
                func.min(AnalyticsEvent.value).label("minimum"),
                func.max(AnalyticsEvent.value).label("maximum"),
                func.count().label("count"),
                func.count(func.distinct(AnalyticsEvent.user_id)).label("unique_users"),
            )
            .where(AnalyticsEvent.event_type == metric_type.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
            .group_by("period_start")
            .order_by("period_start")
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            rows = result.all()

        return [
            MetricAggregation(
                metric_type=metric_type.value,
                period=period,
                start_time=row.period_start,
                end_time=row.period_start + timedelta(days=1),
                total=float(row.total or 0),
                average=float(row.average or 0),
                minimum=float(row.minimum or 0),
                maximum=float(row.maximum or 0),
                count=row.count,
                unique_users=row.unique_users,
            )
            for row in rows
        ]

    async def get_dashboard_metrics(
        self,
        start: datetime = None,
        end: datetime = None,
    ) -> dict[str, Any]:
        """Get all metrics for dashboard."""
        if not end:
            end = datetime.now(timezone.utc)
        if not start:
            start = end - timedelta(days=7)

        metrics = {}

        # API metrics
        metrics["api_requests"] = await self.get_time_series(
            MetricType.API_REQUEST, start, end, "hour"
        )

        # User metrics
        metrics["active_users"] = await self._get_active_users_count(start, end)
        metrics["new_signups"] = await self._get_new_signups(start, end)

        # Equation metrics
        metrics["equations_created"] = await self._get_equations_summary(start, end)

        # Performance metrics
        metrics["avg_latency"] = await self._get_average_latency(start, end)
        metrics["error_rate"] = await self._get_error_rate(start, end)

        return metrics

    async def _get_active_users_count(self, start: datetime, end: datetime) -> dict[str, int]:
        """Count active users in period."""
        stmt = (
            select(func.count(func.distinct(AnalyticsEvent.user_id)))
            .where(AnalyticsEvent.event_type == MetricType.API_REQUEST.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            count = result.scalar()

        return {"daily_active": count, "period": "7d"}

    async def _get_new_signups(self, start: datetime, end: datetime) -> dict[str, int]:
        """Count new signups."""
        stmt = (
            select(func.count())
            .where(AnalyticsEvent.event_type == MetricType.USER_SIGNUP.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            count = result.scalar()

        return {"new_users": count, "period": "7d"}

    async def _get_equations_summary(self, start: datetime, end: datetime) -> dict[str, int]:
        """Get equation creation summary."""
        stmt = (
            select(func.count())
            .where(AnalyticsEvent.event_type == MetricType.EQUATION_CREATED.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            created = result.scalar()

        verify_stmt = (
            select(func.count())
            .where(AnalyticsEvent.event_type == MetricType.EQUATION_VERIFIED.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        result = await session.execute(verify_stmt)
        verified = result.scalar()

        return {"created": created, "verified": verified}

    async def _get_average_latency(self, start: datetime, end: datetime) -> dict[str, float]:
        """Get average API latency."""
        stmt = (
            select(func.avg(AnalyticsEvent.value))
            .where(AnalyticsEvent.event_type == MetricType.API_LATENCY.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        async with AsyncSession(self.engine) as session:
            result = await session.execute(stmt)
            avg = result.scalar() or 0

        return {"p50": avg, "p95": avg * 1.5, "p99": avg * 2}

    async def _get_error_rate(self, start: datetime, end: datetime) -> dict[str, float]:
        """Calculate error rate."""
        error_stmt = (
            select(func.count())
            .where(AnalyticsEvent.event_type == MetricType.API_ERROR.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        total_stmt = (
            select(func.count())
            .where(AnalyticsEvent.event_type == MetricType.API_REQUEST.value)
            .where(AnalyticsEvent.timestamp >= start)
            .where(AnalyticsEvent.timestamp < end)
        )

        async with AsyncSession(self.engine) as session:
            errors = await session.execute(error_stmt)
            total = await session.execute(total_stmt)

            error_count = errors.scalar() or 0
            total_count = total.scalar() or 1

        rate = (error_count / total_count) * 100

        return {"error_rate_percent": round(rate, 2), "total_requests": total_count}


class AnalyticsReporter:
    """Generate reports from analytics data."""

    def __init__(self, warehouse: AnalyticsWarehouse):
        self.warehouse = warehouse

    async def generate_weekly_report(self) -> dict[str, Any]:
        """Generate weekly business report."""
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)

        # Current week vs previous week
        prev_start = start - timedelta(days=7)
        prev_end = start

        current = await self.warehouse.get_dashboard_metrics(start, end)
        previous = await self.warehouse.get_dashboard_metrics(prev_start, prev_end)

        return {
            "period": f"{start.date()} to {end.date()}",
            "metrics": current,
            "comparison": {
                "active_users_change": self._calc_change(
                    current.get("active_users", {}).get("daily_active", 0),
                    previous.get("active_users", {}).get("daily_active", 0),
                ),
                "equations_created_change": self._calc_change(
                    current.get("equations_created", {}).get("created", 0),
                    previous.get("equations_created", {}).get("created", 0),
                ),
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _calc_change(current: float, previous: float) -> dict[str, Any]:
        """Calculate percentage change."""
        if previous == 0:
            return {"change": current, "percent": 100 if current > 0 else 0}

        change = current - previous
        percent = (change / previous) * 100

        return {"change": change, "percent": round(percent, 1)}


# Integration with FastAPI
def create_analytics_middleware(warehouse: AnalyticsWarehouse):
    """Create middleware for automatic analytics tracking."""

    async def track_request(request, response, duration_ms: float):
        """Track API request metrics."""
        user_id = getattr(request.state, "user_id", None)

        await warehouse.track_event(
            MetricType.API_REQUEST,
            user_id=user_id,
            value=1,
            metadata={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
            },
        )

        await warehouse.track_event(
            MetricType.API_LATENCY,
            user_id=user_id,
            value=duration_ms,
            metadata={"path": str(request.url.path)},
        )

        if response.status_code >= 400:
            await warehouse.track_event(
                MetricType.API_ERROR,
                user_id=user_id,
                value=1,
                metadata={
                    "status_code": response.status_code,
                    "path": str(request.url.path),
                },
            )

    return track_request


# CLI for analytics operations
if __name__ == "__main__":
    import argparse
    import json
    import os

    parser = argparse.ArgumentParser(description="AMOS Analytics Warehouse")
    parser.add_argument("--init", action="store_true", help="Initialize warehouse tables")
    parser.add_argument(
        "--report", choices=["weekly", "daily", "dashboard"], help="Generate report"
    )
    parser.add_argument("--export", help="Export data to JSON file")

    args = parser.parse_args()

    db_url = os.getenv("ANALYTICS_DATABASE_URL", "sqlite+aiosqlite:///./analytics.db")
    warehouse = AnalyticsWarehouse(db_url)

    async def main():
        if args.init:
            await warehouse.initialize()
            print("Analytics warehouse initialized")

        elif args.report:
            reporter = AnalyticsReporter(warehouse)
            if args.report == "weekly":
                report = await reporter.generate_weekly_report()
                print(json.dumps(report, indent=2, default=str))
            elif args.report == "dashboard":
                metrics = await warehouse.get_dashboard_metrics()
                print(json.dumps(metrics, indent=2, default=str))

        elif args.export:
            metrics = await warehouse.get_dashboard_metrics()
            with open(args.export, "w") as f:
                json.dump(metrics, f, indent=2, default=str)
            print(f"Exported to {args.export}")

    asyncio.run(main())

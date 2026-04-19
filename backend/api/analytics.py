from typing import Any

"""AMOS Real-time Analytics API - Time-Series Metrics & Anomaly Detection

Production-ready analytics endpoints for metrics collection,
time-series queries, and anomaly detection.

Owner: Trang Phan
Version: 2.0.0
"""
from __future__ import annotations


import time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.analytics import (
    AnalyticsService,
    analytics_service,
)
from backend.auth import User, get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


class MetricRecordRequest(BaseModel):
    """Request to record a metric."""

    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: str = Field(default="gauge", description="Metric type: counter, gauge, histogram")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels/tags")


class MetricQueryRequest(BaseModel):
    """Request to query metrics."""

    metric_name: str = Field(..., description="Metric name to query")
    start_time: float | None = Field(None, description="Start timestamp (epoch)")
    end_time: float | None = Field(None, description="End timestamp (epoch)")
    labels: dict[str, str] = Field(default_factory=dict, description="Label filters")
    aggregation: str | None = Field(None, description="Aggregation: avg, sum, min, max, count")
    bucket_seconds: int = Field(default=60, ge=1, description="Aggregation bucket size")


class AnomalyDetectRequest(BaseModel):
    """Request to detect anomalies."""

    metric_name: str = Field(..., description="Metric to analyze")
    current_value: float = Field(..., description="Current value to check")
    labels: dict[str, str] = Field(default_factory=dict, description="Label filters")
    sensitivity: float = Field(default=2.0, ge=0.5, le=5.0, description="Z-score threshold")


class MetricPointResponse(BaseModel):
    """Single metric data point."""

    timestamp: float
    value: float
    labels: dict[str, str]


class MetricStatsResponse(BaseModel):
    """Metric statistics."""

    metric_name: str
    count: float
    min: float
    max: float
    avg: float
    std: float


class AnomalyResponse(BaseModel):
    """Anomaly detection result."""

    is_anomaly: bool
    z_score: float
    mean: float
    std: float
    threshold: float
    current_value: float
    reason: str | None = None


class SpikeDetectResponse(BaseModel):
    """Spike detection result."""

    is_spike: bool
    spike_ratio: float
    threshold: float
    recent_avg: float
    historical_avg: float


def get_analytics_service() -> AnalyticsService:
    """Dependency injection for analytics service."""
    return analytics_service


@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_metric_endpoint(
    request: MetricRecordRequest,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Record a metric value.

    Supports counter, gauge, and histogram metric types.
    """
    success = service.record_metric(
        name=request.name,
        value=request.value,
        metric_type=request.metric_type,
        labels=request.labels,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record metric"
        )

    return {
        "recorded": True,
        "metric": request.name,
        "value": request.value,
        "type": request.metric_type,
        "timestamp": time.time(),
    }


@router.post("/query", response_model=list[MetricPointResponse])
async def query_metrics_endpoint(
    request: MetricQueryRequest,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user),
) -> list[MetricPointResponse]:
    """Query time-series metrics.

    Returns metric points with optional aggregation.
    """
    start = request.start_time or (time.time() - 3600)
    end = request.end_time or time.time()

    points = service.query_metrics(
        metric_name=request.metric_name,
        start_time=start,
        end_time=end,
        labels=request.labels,
        aggregation=request.aggregation,
    )

    return [
        MetricPointResponse(timestamp=p.timestamp, value=p.value, labels=p.labels) for p in points
    ]


@router.get("/stats/{metric_name}", response_model=MetricStatsResponse)
async def get_metric_stats(
    metric_name: str,
    labels: str | None = Query(None, description="Labels as JSON string"),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user),
) -> MetricStatsResponse:
    """Get statistics for a metric."""
    import json

    label_dict = {}
    if labels:
        try:
            label_dict = json.loads(labels)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid labels JSON"
            )

    stats = service.get_stats(metric_name, label_dict)

    return MetricStatsResponse(
        metric_name=metric_name,
        count=stats["count"],
        min=stats["min"],
        max=stats["max"],
        avg=stats["avg"],
        std=stats["std"],
    )


@router.post("/detect/anomaly", response_model=AnomalyResponse)
async def detect_anomaly_endpoint(
    request: AnomalyDetectRequest,
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_user),
) -> AnomalyResponse:
    """Detect if current value is anomalous.

    Uses statistical z-score analysis based on historical data.
    """
    is_anomaly, info = service.detect_anomalies(
        metric_name=request.metric_name,
        current_value=request.current_value,
        labels=request.labels,
        sensitivity=request.sensitivity,
    )

    return AnomalyResponse(
        is_anomaly=is_anomaly,
        z_score=info.get("z_score", 0.0),
        mean=info.get("mean", 0.0),
        std=info.get("std", 0.0),
        threshold=info.get("threshold", request.sensitivity),
        current_value=info.get("current_value", request.current_value),
        reason=info.get("reason"),
    )


@router.post("/counter/increment")
async def increment_counter(
    name: str,
    value: float = 1.0,
    labels: str | None = Query(None, description="Labels as JSON string"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """Increment a counter metric."""

    label_dict = json.loads(labels) if labels else {}
    service.increment_counter(name, value, label_dict)

    return {"metric": name, "increment": value, "labels": label_dict, "timestamp": time.time()}


@router.post("/timing/record")
async def record_timing(
    name: str,
    duration_seconds: float,
    labels: str | None = Query(None, description="Labels as JSON string"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """Record a timing measurement."""
    label_dict = json.loads(labels) if labels else {}
    service.record_timing(name, duration_seconds, label_dict)

    return {
        "metric": name,
        "duration_seconds": duration_seconds,
        "labels": label_dict,
        "timestamp": time.time(),
    }

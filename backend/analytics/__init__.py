"""AMOS Real-time Analytics Service."""

from .analytics_service import (
    AnalyticsService,
    AnomalyDetector,
    MetricsCollector,
    TimeSeriesDB,
    analytics_service,
    detect_anomalies,
    query_metrics,
    record_metric,
)

__all__ = [
    "AnalyticsService",
    "TimeSeriesDB",
    "MetricsCollector",
    "AnomalyDetector",
    "analytics_service",
    "record_metric",
    "query_metrics",
    "detect_anomalies",
]

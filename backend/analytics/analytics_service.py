"""
AMOS Real-time Analytics & Time-Series Layer v2.0.0

Time-series metrics, materialized views, and anomaly detection.
Supports Redis TimeSeries, windowed aggregations, and statistical monitoring.

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations

import json
import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from backend.data_pipeline.streaming import publish_event

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


@dataclass
class MetricPoint:
    """Single time-series data point."""

    timestamp: float
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time-series metric with retention."""

    name: str
    metric_type: str  # counter, gauge, histogram, summary
    retention_seconds: int = 86400  # 24h default
    data: deque[MetricPoint] = field(default_factory=lambda: deque(maxlen=10000))
    aggregations: dict[str, float] = field(default_factory=dict)


class TimeSeriesDB:
    """Time-series database with Redis backend."""

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or "redis://localhost:6379/10"
        self._redis: redis.Optional[Redis] = None
        self._series: dict[str, MetricSeries] = {}

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

    def _get_ts_key(self, metric_name: str, labels: dict[str, str]) -> str:
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"ts:{metric_name}:{hash(label_str) % 10000}"

    def record(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        labels: dict[str, Optional[str]] = None,
        timestamp: float = None,
    ) -> bool:
        """Record a metric point."""
        ts = timestamp or time.time()
        labels = labels or {}

        # In-memory storage
        key = f"{metric_name}:{json.dumps(labels, sort_keys=True)}"
        if key not in self._series:
            self._series[key] = MetricSeries(
                name=metric_name, metric_type=metric_type, data=deque(maxlen=10000)
            )

        point = MetricPoint(timestamp=ts, value=value, labels=labels)
        self._series[key].data.append(point)

        # Redis persistence
        if self._redis:
            try:
                redis_key = self._get_ts_key(metric_name, labels)
                self._redis.ts().add(
                    redis_key,
                    int(ts * 1000),  # milliseconds
                    value,
                    retention_msecs=self._series[key].retention_seconds * 1000,
                    labels={"metric": metric_name, **labels},
                )
            except Exception:
                # Fallback to regular Redis if TimeSeries not available
                try:
                    self._redis.zadd(
                        f"metric:{metric_name}",
                        {json.dumps({"ts": ts, "val": value, "labels": labels}): ts},
                    )
                    self._redis.expire(f"metric:{metric_name}", 86400)
                except Exception:
                    pass

        return True

    def query(
        self,
        metric_name: str,
        start_time: float = None,
        end_time: float = None,
        labels: dict[str, Optional[str]] = None,
        aggregation: str = None,
        bucket_seconds: int = 60,
    ) -> list[MetricPoint]:
        """Query time-series data with optional aggregation."""
        start_time = start_time or (time.time() - 3600)
        end_time = end_time or time.time()
        labels = labels or {}

        results = []

        # Query from in-memory
        key = f"{metric_name}:{json.dumps(labels, sort_keys=True)}"
        if key in self._series:
            series = self._series[key]
            filtered = [p for p in series.data if start_time <= p.timestamp <= end_time]
            results.extend(filtered)

        # Query from Redis
        if self._redis:
            try:
                redis_key = self._get_ts_key(metric_name, labels)
                raw_data = self._redis.zrangebyscore(f"metric:{metric_name}", start_time, end_time)
                for item in raw_data:
                    try:
                        data = json.loads(item)
                        if all(data.get("labels", {}).get(k) == v for k, v in labels.items()):
                            results.append(
                                MetricPoint(
                                    timestamp=data["ts"],
                                    value=data["val"],
                                    labels=data.get("labels", {}),
                                )
                            )
                    except Exception:
                        continue
            except Exception:
                pass

        # Apply aggregation
        if aggregation and results:
            return self._aggregate(results, aggregation, bucket_seconds)

        return sorted(results, key=lambda x: x.timestamp)

    def _aggregate(
        self, points: list[MetricPoint], aggregation: str, bucket_seconds: int
    ) -> list[MetricPoint]:
        """Aggregate points into buckets."""
        buckets: dict[int, list[float]] = {}

        for point in points:
            bucket_ts = int(point.timestamp / bucket_seconds) * bucket_seconds
            if bucket_ts not in buckets:
                buckets[bucket_ts] = []
            buckets[bucket_ts].append(point.value)

        aggregated = []
        for ts, values in sorted(buckets.items()):
            if aggregation == "avg":
                val = sum(values) / len(values)
            elif aggregation == "sum":
                val = sum(values)
            elif aggregation == "min":
                val = min(values)
            elif aggregation == "max":
                val = max(values)
            elif aggregation == "count":
                val = len(values)
            else:
                val = sum(values) / len(values)

            aggregated.append(MetricPoint(timestamp=ts, value=val))

        return aggregated

    def get_stats(
        self, metric_name: str, labels: dict[str, Optional[str]] = None
    ) -> dict[str, float]:
        """Get statistics for a metric."""
        labels = labels or {}
        key = f"{metric_name}:{json.dumps(labels, sort_keys=True)}"

        if key not in self._series or not self._series[key].data:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "std": 0}

        values = [p.value for p in self._series[key].data]
        count = len(values)
        min_val = min(values)
        max_val = max(values)
        avg = sum(values) / count
        variance = sum((v - avg) ** 2 for v in values) / count
        std = math.sqrt(variance)

        return {"count": float(count), "min": min_val, "max": max_val, "avg": avg, "std": std}


class MetricsCollector:
    """Collect and aggregate system metrics."""

    def __init__(self, tsdb: TimeSeriesDB = None):
        self._tsdb = tsdb or TimeSeriesDB()
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}

    def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, Optional[str]] = None
    ) -> None:
        """Increment a counter metric."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self._counters[key] = self._counters.get(key, 0) + value
        self._tsdb.record(name, self._counters[key], "counter", labels)

    def record_gauge(
        self, name: str, value: float, labels: dict[str, Optional[str]] = None
    ) -> None:
        """Record a gauge metric."""
        self._gauges[name] = value
        self._tsdb.record(name, value, "gauge", labels)

    def record_histogram(
        self, name: str, value: float, buckets: list[float], labels: dict[str, Optional[str]] = None
    ) -> None:
        """Record a histogram metric."""
        for bucket in buckets:
            bucket_labels = {**(labels or {}), "le": str(bucket)}
            if value <= bucket:
                self._tsdb.record(f"{name}_bucket", 1, "counter", bucket_labels)

        # Record +Inf bucket
        inf_labels = {**(labels or {}), "le": "+Inf"}
        self._tsdb.record(f"{name}_bucket", 1, "counter", inf_labels)
        self._tsdb.record(f"{name}_sum", value, "counter", labels)
        self._tsdb.record(f"{name}_count", 1, "counter", labels)

    def record_timing(
        self, name: str, duration_seconds: float, labels: dict[str, Optional[str]] = None
    ) -> None:
        """Record a timing metric."""
        self._tsdb.record(name, duration_seconds, "gauge", labels)


class AnomalyDetector:
    """Statistical anomaly detection."""

    def __init__(self, tsdb: TimeSeriesDB = None):
        self._tsdb = tsdb or TimeSeriesDB()
        self._baselines: dict[str, dict[str, float]] = {}

    def detect(
        self,
        metric_name: str,
        current_value: float,
        labels: dict[str, Optional[str]] = None,
        sensitivity: float = 2.0,
    ) -> tuple[bool, dict[str, Any]]:
        """Detect if current value is anomalous."""
        labels = labels or {}
        stats = self._tsdb.get_stats(metric_name, labels)

        if stats["count"] < 10:
            return False, {"reason": "insufficient_data", "samples": stats["count"]}

        mean = stats["avg"]
        std = stats["std"]

        if std == 0:
            return False, {"reason": "no_variance"}

        z_score = (current_value - mean) / std
        is_anomaly = abs(z_score) > sensitivity

        info = {
            "is_anomaly": is_anomaly,
            "z_score": z_score,
            "mean": mean,
            "std": std,
            "threshold": sensitivity,
            "current_value": current_value,
        }

        if is_anomaly and STREAMING_AVAILABLE:
            try:
                publish_event(
                    event_type="anomaly_detected",
                    source_system="analytics",
                    payload={
                        "metric": metric_name,
                        "value": current_value,
                        "z_score": z_score,
                        "labels": labels,
                    },
                    requires_governance=True,
                )
            except Exception:
                pass

        return is_anomaly, info

    def detect_spike(
        self,
        metric_name: str,
        window_seconds: int = 300,
        spike_factor: float = 3.0,
        labels: dict[str, Optional[str]] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Detect sudden spikes in metric."""
        labels = labels or {}
        end_time = time.time()
        start_time = end_time - window_seconds

        recent_data = self._tsdb.query(
            metric_name, start_time=start_time, end_time=end_time, labels=labels
        )

        if len(recent_data) < 2:
            return False, {"reason": "insufficient_recent_data"}

        values = [p.value for p in recent_data]
        recent_avg = sum(values[-5:]) / min(5, len(values[-5:]))
        historical_avg = sum(values[:-5]) / max(1, len(values[:-5]))

        if historical_avg == 0:
            return False, {"reason": "zero_baseline"}

        spike_ratio = recent_avg / historical_avg
        is_spike = spike_ratio > spike_factor

        return is_spike, {
            "is_spike": is_spike,
            "spike_ratio": spike_ratio,
            "threshold": spike_factor,
            "recent_avg": recent_avg,
            "historical_avg": historical_avg,
        }


class AnalyticsService:
    """Main analytics service facade."""

    def __init__(self, redis_url: str = None):
        self._tsdb = TimeSeriesDB(redis_url)
        self._collector = MetricsCollector(self._tsdb)
        self._detector = AnomalyDetector(self._tsdb)

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: str = "gauge",
        labels: dict[str, Optional[str]] = None,
    ) -> bool:
        """Record a metric."""
        return self._tsdb.record(name, value, metric_type, labels)

    def query_metrics(
        self,
        metric_name: str,
        start_time: float = None,
        end_time: float = None,
        labels: dict[str, Optional[str]] = None,
        aggregation: str = None,
    ) -> list[MetricPoint]:
        """Query metrics."""
        return self._tsdb.query(metric_name, start_time, end_time, labels, aggregation)

    def detect_anomalies(
        self,
        metric_name: str,
        current_value: float,
        labels: dict[str, Optional[str]] = None,
        sensitivity: float = 2.0,
    ) -> tuple[bool, dict[str, Any]]:
        """Detect anomalies."""
        return self._detector.detect(metric_name, current_value, labels, sensitivity)

    def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, Optional[str]] = None
    ) -> None:
        """Increment counter."""
        self._collector.increment_counter(name, value, labels)

    def record_timing(
        self, name: str, duration_seconds: float, labels: dict[str, Optional[str]] = None
    ) -> None:
        """Record timing."""
        self._collector.record_timing(name, duration_seconds, labels)

    def get_stats(
        self, metric_name: str, labels: dict[str, Optional[str]] = None
    ) -> dict[str, float]:
        """Get metric statistics."""
        return self._tsdb.get_stats(metric_name, labels)


# Global service
analytics_service = AnalyticsService()


def record_metric(
    name: str, value: float, metric_type: str = "gauge", labels: dict[str, Optional[str]] = None
) -> bool:
    """Record a metric (convenience function)."""
    return analytics_service.record_metric(name, value, metric_type, labels)


def query_metrics(
    metric_name: str,
    start_time: float = None,
    end_time: float = None,
    labels: dict[str, Optional[str]] = None,
    aggregation: str = None,
) -> list[MetricPoint]:
    """Query metrics (convenience function)."""
    return analytics_service.query_metrics(metric_name, start_time, end_time, labels, aggregation)


def detect_anomalies(
    metric_name: str,
    current_value: float,
    labels: dict[str, Optional[str]] = None,
    sensitivity: float = 2.0,
) -> tuple[bool, dict[str, Any]]:
    """Detect anomalies (convenience function)."""
    return analytics_service.detect_anomalies(metric_name, current_value, labels, sensitivity)

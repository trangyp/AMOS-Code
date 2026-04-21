"""Brain Pattern Recognition API - AMOS brain-powered pattern detection.

Provides pattern recognition capabilities:
- Anomaly detection in brain operations
- Pattern mining from memory
- Trend analysis
- Predictive insights
- Behavioral clustering
"""

from __future__ import annotations

import asyncio
import sys
from collections import Counter
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import brain components
try:
    from cognitive_engine import get_cognitive_engine

    from memory import BrainMemory

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/patterns", tags=["Brain Pattern Recognition"])


class PatternType(str, Enum):
    """Types of patterns that can be detected."""

    SEQUENTIAL = "sequential"
    FREQUENCY = "frequency"
    ANOMALY = "anomaly"
    CLUSTER = "cluster"
    TREND = "trend"
    ASSOCIATION = "association"


class DetectedPattern(BaseModel):
    """A detected pattern."""

    pattern_id: str
    pattern_type: PatternType
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    items: list[str] = Field(default_factory=list)
    frequency: int = 0
    support: float = Field(ge=0.0, le=1.0)
    first_seen: datetime
    last_seen: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnomalyReport(BaseModel):
    """Anomaly detection report."""

    anomaly_id: str
    severity: str  # low, medium, high, critical
    category: str
    description: str
    detected_at:datetime
    expected_value: Optional[float] =None
    actual_value: Optional[float] = None
    deviation_score: float = Field(ge=0.0)
    related_patterns: list[str] = Field(default_factory=list)


class TrendAnalysis(BaseModel):
    """Trend analysis result."""

    trend_id: str
    metric: str
    direction: str  # increasing, decreasing, stable
    slope: float
    confidence: float = Field(ge=0.0, le=1.0)
    start_date: datetime
    end_date: datetime
    data_points:int
    prediction_7d: Optional[float] =None
    prediction_30d: Optional[float] = None


class PatternQuery(BaseModel):
    """Query for pattern detection."""

    source_data: str = Field(..., description="Data source to analyze")
    pattern_types: list[PatternType] = Field(default_factory=list)
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    time_range_days: int = Field(default=30, ge=1, le=365)
    max_patterns: int = Field(default=20, ge=1, le=100)


class PatternRecognitionEngine:
    """Engine for detecting patterns in brain data."""

    def __init__(self) -> None:
        self._detected_patterns: list[DetectedPattern] = []
        self._anomalies: list[AnomalyReport] = []
        self._trends: list[TrendAnalysis] = []
        self._cognitive_engine = None
        self._memory = None
        self._lock = asyncio.Lock()

    async def _get_cognitive_engine(self) -> Any:
        """Get cognitive engine."""
        if _BRAIN_AVAILABLE and self._cognitive_engine is None:
            try:
                self._cognitive_engine = get_cognitive_engine()
            except Exception:
                pass
        return self._cognitive_engine

    async def _get_memory(self) -> Any:
        """Get brain memory."""
        if _BRAIN_AVAILABLE and self._memory is None:
            try:
                self._memory = BrainMemory()
            except Exception:
                pass
        return self._memory

    async def detect_frequent_patterns(
        self, data_source: str, min_support: float = 0.1
    ) -> list[DetectedPattern]:
        """Detect frequently occurring patterns."""
        async with self._lock:
            patterns: list[DetectedPattern] = []

            # Get data from memory
            memory = await self._get_memory()
            if memory and hasattr(memory, "_local_cache"):
                entries = list(memory._local_cache.values())

                # Extract tags and find frequent combinations
                tag_counter: Counter[str] = Counter()
                for entry in entries:
                    tags = entry.get("tags", [])
                    for tag in tags:
                        tag_counter[tag] += 1

                # Create patterns from frequent tags
                total_entries = len(entries)
                for tag, count in tag_counter.most_common(20):
                    support = count / total_entries if total_entries > 0 else 0
                    if support >= min_support:
                        patterns.append(
                            DetectedPattern(
                                pattern_id=f"freq-{tag}",
                                pattern_type=PatternType.FREQUENCY,
                                confidence=min(1.0, support * 2),
                                description=f"Frequent tag: {tag}",
                                items=[tag],
                                frequency=count,
                                support=support,
                                first_seen=datetime.now(UTC) - timedelta(days=30),
                                last_seen=datetime.now(UTC),
                                metadata={"source": data_source, "tag": tag},
                            )
                        )

            return patterns

    async def detect_anomalies(
        self, data_source: str, sensitivity: float = 2.0
    ) -> list[AnomalyReport]:
        """Detect anomalies in brain data."""
        async with self._lock:
            anomalies: list[AnomalyReport] = []

            memory = await self._get_memory()
            if memory and hasattr(memory, "_local_cache"):
                entries = list(memory._local_cache.values())

                # Check for confidence score anomalies
                confidences: list[float] = []
                for entry in entries:
                    conf = entry.get("confidence_score")
                    if conf is not None:
                        confidences.append(conf)

                if confidences:
                    mean_conf = sum(confidences) / len(confidences)
                    std_conf = (
                        sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
                    ) ** 0.5

                    # Find entries with anomalous confidence
                    for i, entry in enumerate(entries):
                        conf = entry.get("confidence_score")
                        if conf is not None:
                            deviation = abs(conf - mean_conf)
                            if std_conf > 0 and deviation > sensitivity * std_conf:
                                severity = "high" if deviation > 3 * std_conf else "medium"
                                anomalies.append(
                                    AnomalyReport(
                                        anomaly_id=f"anom-conf-{i}",
                                        severity=severity,
                                        category="confidence",
                                        description="Unusual confidence score in entry",
                                        detected_at=datetime.now(UTC),
                                        expected_value=mean_conf,
                                        actual_value=conf,
                                        deviation_score=deviation / std_conf if std_conf > 0 else 0,
                                    )
                                )

            return anomalies

    async def analyze_trends(self, metric: str, days: int = 30) -> list[TrendAnalysis]:
        """Analyze trends in brain metrics."""
        async with self._lock:
            trends: list[TrendAnalysis] = []

            # Simulate trend analysis
            memory = await self._get_memory()
            if memory and hasattr(memory, "_local_cache"):
                entries = list(memory._local_cache.values())

                # Group by date
                daily_counts: dict[str, int] = {}
                for entry in entries:
                    ts = entry.get("timestamp", "")
                    if ts:
                        date = ts[:10]  # YYYY-MM-DD
                        daily_counts[date] = daily_counts.get(date, 0) + 1

                if len(daily_counts) >= 3:
                    dates = sorted(daily_counts.keys())
                    values = [daily_counts[d] for d in dates]

                    # Simple linear trend
                    n = len(values)
                    x_mean = (n - 1) / 2
                    y_mean = sum(values) / n

                    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
                    denominator = sum((i - x_mean) ** 2 for i in range(n))

                    slope = numerator / denominator if denominator > 0 else 0

                    # Determine direction
                    if slope > 0.1:
                        direction = "increasing"
                    elif slope < -0.1:
                        direction = "decreasing"
                    else:
                        direction = "stable"

                    # Predictions
                    last_value = values[-1]
                    prediction_7d = last_value + slope * 7
                    prediction_30d = last_value + slope * 30

                    trends.append(
                        TrendAnalysis(
                            trend_id=f"trend-{metric}",
                            metric=metric,
                            direction=direction,
                            slope=slope,
                            confidence=min(1.0, n / 30),
                            start_date=datetime.fromisoformat(dates[0])
                            if dates
                            else datetime.now(UTC),
                            end_date=datetime.fromisoformat(dates[-1])
                            if dates
                            else datetime.now(UTC),
                            data_points=n,
                            prediction_7d=max(0, prediction_7d),
                            prediction_30d=max(0, prediction_30d),
                        )
                    )

            return trends

    async def find_associations(
        self, item: str, min_confidence: float = 0.5
    ) -> list[DetectedPattern]:
        """Find items associated with given item."""
        async with self._lock:
            associations: list[DetectedPattern] = []

            memory = await self._get_memory()
            if memory and hasattr(memory, "_local_cache"):
                entries = list(memory._local_cache.values())

                # Find entries containing the item
                related_entries = [e for e in entries if item.lower() in str(e).lower()]

                # Find co-occurring tags
                cooccurring: Counter[str] = Counter()
                for entry in related_entries:
                    for tag in entry.get("tags", []):
                        if tag != item:
                            cooccurring[tag] += 1

                total = len(related_entries)
                for tag, count in cooccurring.most_common(10):
                    confidence = count / total if total > 0 else 0
                    if confidence >= min_confidence:
                        associations.append(
                            DetectedPattern(
                                pattern_id=f"assoc-{item}-{tag}",
                                pattern_type=PatternType.ASSOCIATION,
                                confidence=confidence,
                                description=f"{item} frequently associated with {tag}",
                                items=[item, tag],
                                frequency=count,
                                support=count / len(entries) if entries else 0,
                                first_seen=datetime.now(UTC) - timedelta(days=30),
                                last_seen=datetime.now(UTC),
                                metadata={"association_type": "tag_cooccurrence"},
                            )
                        )

            return associations

    async def stream_patterns(self, query: PatternQuery) -> AsyncIterator[DetectedPattern]:
        """Stream detected patterns."""
        # Yield frequent patterns
        freq_patterns = await self.detect_frequent_patterns(query.source_data, min_support=0.05)
        for pattern in freq_patterns:
            if pattern.confidence >= query.min_confidence:
                yield pattern

        # Yield associations
        if PatternType.ASSOCIATION in query.pattern_types:
            assoc_patterns = await self.find_associations(
                query.source_data, min_confidence=query.min_confidence
            )
            for pattern in assoc_patterns:
                yield pattern

    async def get_insights(self) -> dict[str, Any]:
        """Get overall pattern insights."""
        insights = {
            "total_patterns_detected": len(self._detected_patterns),
            "total_anomalies": len(self._anomalies),
            "total_trends": len(self._trends),
            "pattern_types": {},
            "brain_available": _BRAIN_AVAILABLE,
        }

        # Count by type
        for pattern in self._detected_patterns:
            t = pattern.pattern_type.value
            insights["pattern_types"][t] = insights["pattern_types"].get(t, 0) + 1

        # Recent anomalies
        recent_anomalies = [
            a for a in self._anomalies if (datetime.now(UTC) - a.detected_at).days <= 7
        ]
        insights["recent_anomalies"] = len(recent_anomalies)

        return insights


#Global engine
_pattern_engine: Optional[PatternRecognitionEngine] = None


def get_pattern_engine() -> PatternRecognitionEngine:
    """Get or create pattern recognition engine."""
    global _pattern_engine
    if _pattern_engine is None:
        _pattern_engine = PatternRecognitionEngine()
    return _pattern_engine


@router.post("/detect/frequent", response_model=list[DetectedPattern])
async def detect_frequent_patterns(
    data_source: str, min_support: float = Query(default=0.1, ge=0.01, le=1.0)
) -> list[DetectedPattern]:
    """Detect frequently occurring patterns in brain data."""
    engine = get_pattern_engine()
    return await engine.detect_frequent_patterns(data_source, min_support)


@router.post("/detect/anomalies", response_model=list[AnomalyReport])
async def detect_anomalies(
    data_source: str, sensitivity: float = Query(default=2.0, ge=0.5, le=5.0)
) -> list[AnomalyReport]:
    """Detect anomalies in brain operations."""
    engine = get_pattern_engine()
    return await engine.detect_anomalies(data_source, sensitivity)


@router.get("/trends/{metric}", response_model=list[TrendAnalysis])
async def analyze_trends(
    metric: str, days: int = Query(default=30, ge=7, le=365)
) -> list[TrendAnalysis]:
    """Analyze trends in brain metrics."""
    engine = get_pattern_engine()
    return await engine.analyze_trends(metric, days)


@router.get("/associations/{item}", response_model=list[DetectedPattern])
async def find_associations(
    item: str, min_confidence: float = Query(default=0.5, ge=0.0, le=1.0)
) -> list[DetectedPattern]:
    """Find items associated with given item."""
    engine = get_pattern_engine()
    return await engine.find_associations(item, min_confidence)


@router.post("/stream")
async def stream_patterns(query: PatternQuery) -> StreamingResponse:
    """Stream detected patterns as Server-Sent Events."""
    engine = get_pattern_engine()

    async def event_generator():
        async for pattern in engine.stream_patterns(query):
            yield f"data: {pattern.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/insights")
async def get_insights() -> dict[str, Any]:
    """Get overall pattern recognition insights."""
    engine = get_pattern_engine()
    return await engine.get_insights()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check for pattern recognition."""
    engine = get_pattern_engine()
    insights = await engine.get_insights()

    return {
        "status": "healthy" if _BRAIN_AVAILABLE else "degraded",
        "brain_available": _BRAIN_AVAILABLE,
        "patterns_detected": insights["total_patterns_detected"],
        "anomalies_detected": insights["total_anomalies"],
        "engine": "active",
    }

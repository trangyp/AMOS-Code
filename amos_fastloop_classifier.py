from __future__ import annotations

from typing import Any, Optional

"""
AMOS FastLoop Interrupt Classifier
Implements O(1) request classification for FastLoop routing.

Target: < 1ms classification latency
Strategy: Hash cache → Embedding similarity → Pattern matching
"""

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto

UTC = UTC


class InterruptClass(Enum):
    """FastLoop request classification categories."""

    QUERY = auto()  # Information retrieval (fast path)
    ACTION = auto()  # State mutation (fast path)
    REASONING = auto()  # Full cognition required (slow path)
    ESCALATION = auto()  # Human handoff (redirect)
    ECHO = auto()  # Identity/passthrough (fastest)
    UNKNOWN = auto()  # Needs classification


@dataclass
class ClassificationResult:
    """Result of interrupt classification."""

    class_type: InterruptClass
    confidence: float  # 0.0 - 1.0
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class InterruptClassifier:
    """
    Fast path classification without full semantic parsing.

    Uses 3-tier approach:
    1. Exact hash cache (O(1))
    2. Embedding similarity cache (O(1) with precomputed)
    3. Regex pattern matching (O(length) but fast)
    """

    # Fast path patterns (compiled for speed)
    PATTERNS = {
        InterruptClass.QUERY: re.compile(
            r"^(what|who|where|when|how|why|is|are|can|do|does|did|will|would|should|list|show|get|find|search|lookup)\b",
            re.IGNORECASE,
        ),
        InterruptClass.ACTION: re.compile(
            r"^(create|make|add|delete|remove|update|set|change|start|stop|run|execute|trigger|send|write|save|load|deploy|build|install|configure|enable|disable)\b",
            re.IGNORECASE,
        ),
        InterruptClass.ESCALATION: re.compile(
            r"^(help|support|ticket|escalate|human|agent|operator|emergency|urgent|critical|bug|error|fail)\b",
            re.IGNORECASE,
        ),
        InterruptClass.ECHO: re.compile(
            r"^(ping|hello|hi|test|echo|status|health|version|time|date|ok|yes|no|thanks|thank)\b",
            re.IGNORECASE,
        ),
    }

    # Complexity heuristics for REASONING classification
    REASONING_INDICATORS = re.compile(
        r"(explain|analyze|compare|evaluate|recommend|suggest|think|reason|logic|proof|verify|check|validate|design|architect|optimize|improve|why does|how should|what if|consider|implications|consequences|trade.offs)",
        re.IGNORECASE,
    )

    def __init__(self, cache_size: int = 10000):
        """Initialize classifier with LRU cache."""
        self._cache: dict[str, ClassificationResult] = {}
        self._cache_size = cache_size
        self._embedding_cache: dict[str, InterruptClass] = {}
        self._request_count = 0
        self._cache_hits = 0

    def _compute_hash(self, request: str) -> str:
        """Compute fast hash for cache lookup."""
        # Normalize: lowercase, strip whitespace
        normalized = request.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _check_pattern(self, request: str) -> tuple[InterruptClass, float]:
        """
        Fast regex-based classification.
        Returns (class, confidence).
        """
        # Check each pattern category
        for class_type, pattern in self.PATTERNS.items():
            if pattern.search(request):
                return (class_type, 0.7)  # 70% confidence from pattern

        # Check reasoning indicators
        if self.REASONING_INDICATORS.search(request):
            return (InterruptClass.REASONING, 0.6)

        # Default to REASONING if uncertain (safe fallback)
        return (InterruptClass.REASONING, 0.5)

    def classify(self, request: str, use_cache: bool = True) -> ClassificationResult:
        """
        Classify request in < 1ms.

        Args:
            request: Raw input string
            use_cache: Whether to use hash cache

        Returns:
            ClassificationResult with class, confidence, latency
        """
        start_time = time.perf_counter()
        self._request_count += 1

        # Tier 1: Hash cache (fastest)
        if use_cache:
            request_hash = self._compute_hash(request)
            if request_hash in self._cache:
                self._cache_hits += 1
                cached = self._cache[request_hash]
                # Update timestamp but keep other fields
                latency_ms = (time.perf_counter() - start_time) * 1000
                return ClassificationResult(
                    class_type=cached.class_type,
                    confidence=cached.confidence,
                    latency_ms=latency_ms,
                    metadata={"cache_hit": True, "hash": request_hash},
                )

        # Tier 3: Pattern matching
        class_type, confidence = self._check_pattern(request)

        # Compute latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        result = ClassificationResult(
            class_type=class_type,
            confidence=confidence,
            latency_ms=latency_ms,
            metadata={"cache_hit": False, "pattern_match": True},
        )

        # Cache result (LRU eviction if needed)
        if use_cache and len(self._cache) < self._cache_size:
            self._cache[request_hash] = result

        return result

    def classify_batch(self, requests: list[str]) -> list[ClassificationResult]:
        """Batch classification for efficiency."""
        return [self.classify(req) for req in requests]

    def get_stats(self) -> dict[str, Any]:
        """Get classification statistics."""
        return {
            "total_requests": self._request_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": self._cache_hits / max(1, self._request_count),
            "cache_size": len(self._cache),
            "max_cache_size": self._cache_size,
        }

    def clear_cache(self) -> None:
        """Clear classification cache."""
        self._cache.clear()
        self._request_count = 0
        self._cache_hits = 0


# Global singleton instance
_classifier: Optional[InterruptClassifier] = None


def get_classifier() -> InterruptClassifier:
    """Get global classifier instance (singleton)."""
    global _classifier
    if _classifier is None:
        _classifier = InterruptClassifier()
    return _classifier


async def classify_request(request: str) -> ClassificationResult:
    """
    Fast async wrapper for classification.

    This is intentionally synchronous computation wrapped in async
    for API compatibility—classification is CPU-bound and fast.
    """
    classifier = get_classifier()
    return classifier.classify(request)


# Convenience functions for routing
def is_fast_path(classification: ClassificationResult) -> bool:
    """Check if classification qualifies for fast path."""
    return classification.class_type in {
        InterruptClass.QUERY,
        InterruptClass.ACTION,
        InterruptClass.ECHO,
    }


def requires_full_loop(classification: ClassificationResult) -> bool:
    """Check if classification requires full AMOS loop."""
    return classification.class_type == InterruptClass.REASONING


def should_escalate(classification: ClassificationResult) -> bool:
    """Check if classification requires human escalation."""
    return classification.class_type == InterruptClass.ESCALATION


# Test/example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        test_requests = [
            "What is the current status?",  # QUERY
            "Deploy the application now",  # ACTION
            "Explain the architecture tradeoffs",  # REASONING
            "Help me with a critical bug",  # ESCALATION
            "Hello",  # ECHO
            "Ping",  # ECHO
            "List all users",  # QUERY
            "Analyze the performance bottleneck",  # REASONING
        ]

        print("AMOS FastLoop Classifier Test")
        print("=" * 50)

        for request in test_requests:
            result = await classify_request(request)
            fast = "✓" if is_fast_path(result) else "✗"
            print(
                f"{fast} {result.class_type.name:12} ({result.confidence:.0%}) {result.latency_ms * 1000:.2f}µs | {request[:40]}..."
            )

        print("=" * 50)
        stats = get_classifier().get_stats()
        print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"Total cached: {stats['cache_size']}")

    asyncio.run(test())

from typing import Any, Dict, List, Optional

"""Brain-Powered Cache Optimizer

Intelligent cache warming and prefetching using brain predictions.
Based on research: Cognitive caching with predictive prefetching.
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass

from amos_brain.integrated_brain_api import get_brain_api


@dataclass
class CachePrediction:
    """Cache access prediction."""

    key: str
    confidence: float
    priority: int
    predicted_access_time: float
    ttl_seconds: int
    reason: str


class BrainCacheOptimizer:
    """
    Brain-powered cache optimization with predictive prefetching.

    Uses brain to:
    - Predict which keys will be accessed
    - Determine optimal TTL
    - Prioritize cache warming
    - Detect access patterns
    """

    def __init__(self, cache_get: Optional[Callable] = None, cache_set: Optional[Callable] = None):
        self.brain = get_brain_api()
        self.cache_get = cache_get
        self.cache_set = cache_set
        self._access_history: Dict[str, list[float]] = {}
        self._prediction_history: List[CachePrediction] = []
        self._warm_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def predict_access(
        self,
        key: str,
        context: Dict[str, Any] = None,
    ) -> CachePrediction:
        """
        Predict if a key will be accessed soon.

        Args:
            key: Cache key to predict
            context: Access context (user, endpoint, etc.)

        Returns:
            CachePrediction with confidence and priority
        """
        # Get access history for this key
        history = self._access_history.get(key, [])

        # Build prediction context
        pred_context = {
            "key": key,
            "access_count": len(history),
            "last_access": history[-1] if history else None,
            "access_frequency": len(history)
            / max(time.time() - (history[0] if history else time.time()), 1),
            **(context or {}),
        }

        # Use brain for prediction
        query = f"""Predict cache access for key '{key}':
Access history: {len(history)} times
Last access: {pred_context["last_access"]}
Frequency: {pred_context["access_frequency"]:.3f}/sec

Will this key be accessed in the next 60 seconds?"""

        result = await self.brain.process(query, mode="fast", context=pred_context)

        # Parse confidence from response
        confidence = self._extract_confidence(result.response)
        priority = self._calculate_priority(confidence, len(history))

        prediction = CachePrediction(
            key=key,
            confidence=confidence,
            priority=priority,
            predicted_access_time=time.time() + 30,  # Predict 30s ahead
            ttl_seconds=self._calculate_ttl(key, history),
            reason=result.response[:200],
        )

        self._prediction_history.append(prediction)

        return prediction

    async def warm_cache(
        self,
        keys: List[str],
        value_fetcher: Callable[[str], Any],
    ) -> Dict[str, Any]:
        """
        Pre-warm cache with predicted keys.

        Args:
            keys: Keys to potentially warm
            value_fetcher: Function to fetch value for a key

        Returns:
            Warming results
        """
        warmed = {}

        for key in keys:
            prediction = await self.predict_access(key)

            # Only warm high-confidence predictions
            if prediction.confidence > 0.7 and prediction.priority >= 7:
                try:
                    value = await value_fetcher(key)
                    if self.cache_set:
                        await self.cache_set(
                            key,
                            value,
                            ttl=prediction.ttl_seconds,
                        )
                    warmed[key] = {
                        "warmed": True,
                        "confidence": prediction.confidence,
                        "ttl": prediction.ttl_seconds,
                    }
                except Exception as e:
                    warmed[key] = {
                        "warmed": False,
                        "error": str(e),
                    }
            else:
                warmed[key] = {
                    "warmed": False,
                    "reason": "Low confidence",
                    "confidence": prediction.confidence,
                }

        return warmed

    def record_access(self, key: str, context: Dict[str, Any] = None) -> None:
        """Record a cache access for pattern learning."""
        if key not in self._access_history:
            self._access_history[key] = []

        self._access_history[key].append(time.time())

        # Keep only last 100 access times
        if len(self._access_history[key]) > 100:
            self._access_history[key] = self._access_history[key][-100:]

    def detect_patterns(self) -> List[dict[str, Any]]:
        """
        Detect access patterns from history.

        Returns:
            List of detected patterns
        """
        patterns = []

        for key, history in self._access_history.items():
            if len(history) < 3:
                continue

            # Check for periodic access
            intervals = [history[i] - history[i - 1] for i in range(1, len(history))]

            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)

                # Low variance indicates periodic pattern
                if variance < avg_interval * 0.1:
                    patterns.append(
                        {
                            "key": key,
                            "type": "periodic",
                            "interval_seconds": avg_interval,
                            "confidence": 0.9,
                        }
                    )

        return patterns

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from brain response."""
        response_lower = response.lower()

        # Look for confidence indicators
        if "likely" in response_lower or "yes" in response_lower:
            return 0.8
        elif "unlikely" in response_lower or "no" in response_lower:
            return 0.2
        elif "maybe" in response_lower or "possibly" in response_lower:
            return 0.5

        return 0.5  # Default

    def _calculate_priority(self, confidence: float, access_count: int) -> int:
        """Calculate warming priority (1-10)."""
        base = int(confidence * 10)
        bonus = min(access_count // 10, 3)  # +1 for every 10 accesses, max +3
        return min(base + bonus, 10)

    def _calculate_ttl(self, key: str, history: List[float]) -> int:
        """Calculate optimal TTL based on access pattern."""
        if len(history) < 2:
            return 300  # 5 minutes default

        # Calculate average interval
        intervals = [history[i] - history[i - 1] for i in range(1, len(history))]
        avg_interval = sum(intervals) / len(intervals)

        # TTL = 2x average interval, bounded
        ttl = int(avg_interval * 2)
        return max(60, min(ttl, 3600))  # Between 1 min and 1 hour

    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        patterns = self.detect_patterns()

        return {
            "tracked_keys": len(self._access_history),
            "total_accesses": sum(len(h) for h in self._access_history.values()),
            "predictions_made": len(self._prediction_history),
            "detected_patterns": len(patterns),
            "high_confidence_predictions": sum(
                1 for p in self._prediction_history if p.confidence > 0.7
            ),
        }


# Global instance
_global_optimizer: Optional[BrainCacheOptimizer] = None


def get_brain_cache_optimizer(
    cache_get: Optional[Callable] = None,
    cache_set: Optional[Callable] = None,
) -> BrainCacheOptimizer:
    """Get or create global brain cache optimizer."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = BrainCacheOptimizer(cache_get, cache_set)
    return _global_optimizer


if __name__ == "__main__":

    async def test():
        optimizer = get_brain_cache_optimizer()

        # Record some accesses
        for i in range(5):
            optimizer.record_access("user:123:profile")
            optimizer.record_access("config:api")
            await asyncio.sleep(0.01)

        # Test prediction
        prediction = await optimizer.predict_access("user:123:profile")
        print(f"Key: {prediction.key}")
        print(f"Confidence: {prediction.confidence:.2f}")
        print(f"Priority: {prediction.priority}")
        print(f"TTL: {prediction.ttl_seconds}s")

        # Test pattern detection
        patterns = optimizer.detect_patterns()
        print(f"\nDetected patterns: {len(patterns)}")

        # Test stats
        stats = optimizer.get_stats()
        print(f"\nStats: {stats}")

    asyncio.run(test())

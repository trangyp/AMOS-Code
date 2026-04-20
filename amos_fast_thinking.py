"""AMOS Fast Thinking (System 1) - Dual-Process Architecture.

Based on research: "Agents Thinking Fast and Slow:
A Talker-Reasoner Architecture"

System 1 (Fast): Pattern matching via vector search, cached responses
System 2 (Slow): Deep deliberative thinking via ThinkingKernel

This module provides the Fast Thinking path for <100ms responses.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FastThinkingResult:
    """Result from fast thinking path."""

    response: Optional[str]
    confidence: float
    source: str  # cache, vector_search, pattern_match, fallback_to_slow
    latency_ms: float
    matched_pattern: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class FastThinkingEngine:
    """
    System 1: Fast, intuitive, pattern-based thinking.

    Completes in <100ms using:
    1. L1 cache (exact match)
    2. L2 cache (semantic hash)
    3. Vector search (pattern matching)
    4. Rule-based shortcuts
    """

    def __init__(self, latency_budget_ms: float = 100.0):
        self.latency_budget_ms = latency_budget_ms
        self._l1_cache: dict[str, FastThinkingResult] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def _hash_query(self, query: str, context: dict[str, Any]) -> str:
        """Create deterministic hash for query + context."""
        key_data = f"{query}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    def _elapsed(self, start: float) -> float:
        """Calculate elapsed milliseconds."""
        return (time.perf_counter() - start) * 1000

    def _is_simple_query(self, query: str) -> bool:
        """Detect simple queries that don't need deep thinking."""
        simple_indicators = [
            "what is",
            "how to",
            "define",
            "explain",
            "tldr",
            "quick",
            "fast",
            "brief",
            "short",
            "simple",
        ]
        return any(ind in query.lower() for ind in simple_indicators)

    def _get_rule_based_response(self, query: str) -> Optional[FastThinkingResult]:
        """
        Rule-based fast responses for common patterns.
        No ML/vector search needed - instant response.
        """
        query_lower = query.lower().strip()

        # Greeting patterns
        greetings = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! What would you like to work on?",
            "hey": "Hey! Ready to assist.",
            "good morning": "Good morning! What can I do for you?",
        }
        for greeting, response in greetings.items():
            if query_lower.startswith(greeting):
                return FastThinkingResult(
                    response=response,
                    confidence=0.95,
                    source="rule_greeting",
                    latency_ms=0.1,
                    metadata={"pattern": "greeting"},
                )

        # Status check patterns
        if any(kw in query_lower for kw in ["status", "how are you", "ready"]):
            resp = "I'm ready and operational. All systems are running smoothly."
            return FastThinkingResult(
                response=resp,
                confidence=0.9,
                source="rule_status",
                latency_ms=0.1,
                metadata={"pattern": "status_check"},
            )

        # Help patterns
        if "help" in query_lower and len(query_lower) < 20:
            help_msg = (
                "I can help you with coding, analysis, architecture decisions, "
                "debugging, and more. What specifically do you need?"
            )
            return FastThinkingResult(
                response=help_msg,
                confidence=0.85,
                source="rule_help",
                latency_ms=0.1,
                metadata={"pattern": "help_request"},
            )

        return None

    async def think_fast(
        self, query: str, context: Optional[dict[str, Any]] = None
    ) -> FastThinkingResult:
        """
        Execute fast thinking path.

        Pipeline (target <100ms total):
        1. L1 Cache check (<1ms)
        2. Rule-based patterns (<1ms)
        3. Vector semantic search (30-50ms)
        4. Pattern matching (10ms)
        5. Response assembly (10ms)

        Returns fallback_to_slow if confidence < 0.7
        """
        start = time.perf_counter()
        context = context or {}

        # 1. L1 Cache check - instant
        cache_key = self._hash_query(query, context)
        cached = self._l1_cache.get(cache_key)
        if cached and cached.confidence > 0.7:
            self.cache_hits += 1
            return FastThinkingResult(
                response=cached.response,
                confidence=cached.confidence,
                source="l1_cache",
                latency_ms=self._elapsed(start),
                metadata={"cached": True, "original_source": cached.source},
            )

        # 2. Rule-based patterns - instant
        rule_result = self._get_rule_based_response(query)
        if rule_result:
            # Store in L1 cache
            self._l1_cache[cache_key] = rule_result
            return rule_result

        # Check remaining time budget
        elapsed = self._elapsed(start)
        if elapsed > self.latency_budget_ms * 0.5:
            # Not enough time for vector search
            return FastThinkingResult(
                response=None, confidence=0.0, source="timeout_fallback", latency_ms=elapsed
            )

        # 3. Try vector search (if available)
        try:
            vector_result = await self._vector_search_path(query, context, start)
            if vector_result and vector_result.confidence > 0.7:
                # Cache result
                self._l1_cache[cache_key] = vector_result
                return vector_result
        except Exception:
            # Vector search failed, fall through to slow
            pass

        # Fast path failed - delegate to slow thinking
        self.cache_misses += 1
        return FastThinkingResult(
            response=None,
            confidence=0.0,
            source="fallback_to_slow",
            latency_ms=self._elapsed(start),
        )

    async def _vector_search_path(
        self, query: str, context: dict[str, Any], start_time: float
    ) -> Optional[FastThinkingResult]:
        """
        Vector search path for pattern matching.
        Only runs if vector service is available.
        """
        # Import here to avoid circular dependency
        try:
            from amos_vector_search import ContentType, get_vector_service
        except ImportError:
            return None

        vector_service = get_vector_service()
        if not vector_service:
            return None

        # Semantic search
        results = await vector_service.semantic_search(
            query=query,
            content_types=[ContentType.CONVERSATION, ContentType.KNOWLEDGE, ContentType.CODE],
            top_k=3,
            tenant_id=context.get("workspace_id"),
        )

        if not results:
            return None

        # Check best match
        best = results[0]
        if best.similarity_score < 0.75:
            return None

        # Adapt pattern to query
        adapted = self._adapt_pattern(best.content, query)

        return FastThinkingResult(
            response=adapted,
            confidence=best.similarity_score,
            source="vector_search",
            latency_ms=self._elapsed(start_time),
            matched_pattern=best.id,
            metadata={"similarity": best.similarity_score, "content_type": best.content_type},
        )

    def _adapt_pattern(self, pattern_content: str, query: str) -> str:
        """
        Adapt a cached pattern to the specific query.
        Simple template adaptation.
        """
        # For now, return pattern with query context
        # In production, this would do intelligent template filling
        return f"Based on similar queries, here's what I found:\n\n{pattern_content}"

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "l1_cache_size": len(self._l1_cache),
            "latency_budget_ms": self.latency_budget_ms,
        }

    def clear_cache(self) -> None:
        """Clear L1 cache."""
        self._l1_cache.clear()


# Global instance
_fast_thinking_engine: Optional[FastThinkingEngine] = None


def get_fast_thinking_engine() -> FastThinkingEngine:
    """Get or create global fast thinking engine."""
    global _fast_thinking_engine
    if _fast_thinking_engine is None:
        _fast_thinking_engine = FastThinkingEngine()
    return _fast_thinking_engine


# Convenience function
async def think_fast(query: str, context: Optional[dict[str, Any]] = None) -> FastThinkingResult:
    """Quick access to fast thinking."""
    engine = get_fast_thinking_engine()
    return await engine.think_fast(query, context)

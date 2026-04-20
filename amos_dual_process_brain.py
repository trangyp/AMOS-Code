from __future__ import annotations

from typing import Any, Optional

"""AMOS Dual-Process Brain - Fast & Slow Thinking Integration

Based on research:
- "Agents Thinking Fast and Slow: A Talker-Reasoner Architecture" (Google Research 2024)
- "Medusa: Simple LLM Inference Acceleration Framework" (Together AI 2024)

Integrates System 1 (Fast) and System 2 (Slow) thinking with:
- Parallel indexing and thinking
- Tiered response system
- Speculative decoding pattern for AMOS
"""

import asyncio
import time
from dataclasses import dataclass, field

from amos_brain.facade import BrainClient, BrainResponse
from amos_fast_thinking import FastThinkingEngine, FastThinkingResult


@dataclass
class DualProcessResult:
    """Result from dual-process thinking."""

    response: str
    thinking_mode: str  # fast_only, slow_only, combined
    confidence: float
    latency_ms: float
    fast_result: Optional[FastThinkingResult] = None
    slow_result: Optional[BrainResponse] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DualProcessBrain:
    """
    Dual-process brain combining fast (System 1) and slow (System 2) thinking.

    Architecture:
        Input Query
            │
            ▼
    ┌───────────────────┐
    │  Fast Path (<1ms) │  L1 Cache Check
    │  If confidence>0.8  │
    │     Return Fast   │
    └─────────┬─────────┘
              │ Cache Miss
              ▼
    ┌───────────────────┐
    │  Fast Path (<50ms)│  Vector Search + Rules
    │  If confidence>0.7│
    │     Return Fast   │
    └─────────┬─────────┘
              │ Low Confidence
              ▼
    ┌───────────────────────────┐
    │   Parallel Processing     │
    │   ┌─────────┐ ┌────────┐  │
    │   │ Indexing│ │Thinking│  │  Both run simultaneously
    │   │ (500ms) │ │(2000ms)│  │  Total time = max, not sum
    │   └────┬────┘ └────┬───┘  │
    │        └─────┬─────┘      │
    │              ▼            │
    │      Combine Results      │
    └───────────────────────────┘
              │
              ▼
          Response
    """

    def __init__(self):
        self.fast_engine = FastThinkingEngine()
        self.slow_brain = BrainClient()
        self.stats = {
            "fast_hits": 0,
            "slow_fallbacks": 0,
            "parallel_executions": 0,
            "total_queries": 0,
        }

    async def think(
        self,
        query: str,
        context: dict[str, Any] = None,
        prefer_fast: bool = False,
        latency_budget_ms: float = 2000.0,
    ) -> DualProcessResult:
        """
        Execute dual-process thinking.

        Strategy:
        1. Always try fast path first (<100ms)
        2. If confident, return immediately
        3. Otherwise, run slow thinking with parallel indexing
        """
        start = time.perf_counter()
        context = context or {}

        self.stats["total_queries"] += 1

        # Phase 1: Try fast path
        fast_result = await self.fast_engine.think_fast(query, context)

        # If fast path was confident, return immediately
        if fast_result.confidence > 0.8:
            self.stats["fast_hits"] += 1
            return DualProcessResult(
                response=fast_result.response or "",
                thinking_mode="fast_only",
                confidence=fast_result.confidence,
                latency_ms=(time.perf_counter() - start) * 1000,
                fast_result=fast_result,
                metadata={"source": fast_result.source},
            )

        # Phase 2: Decide on strategy based on latency budget
        elapsed = (time.perf_counter() - start) * 1000
        remaining_budget = latency_budget_ms - elapsed

        if prefer_fast and fast_result.confidence > 0.6:
            # User prefers fast, use medium-confidence fast result
            self.stats["fast_hits"] += 1
            return DualProcessResult(
                response=fast_result.response or "",
                thinking_mode="fast_only",
                confidence=fast_result.confidence,
                latency_ms=elapsed,
                fast_result=fast_result,
                metadata={"source": fast_result.source, "preferred_fast": True},
            )

        # Phase 3: Parallel slow thinking + background indexing
        if remaining_budget > 500:
            self.stats["parallel_executions"] += 1
            return await self._parallel_think(query, context, fast_result, start)

        # Phase 4: Fallback to slow thinking only
        self.stats["slow_fallbacks"] += 1
        return await self._slow_only_think(query, context, start)

    async def _parallel_think(
        self,
        query: str,
        context: dict[str, Any],
        fast_result: FastThinkingResult,
        start_time: float,
    ) -> DualProcessResult:
        """
        Run slow thinking with parallel indexing.

        Simultaneously:
        - Index query for future fast retrieval
        - Execute deep thinking
        - Combine results
        """
        # Create parallel tasks
        asyncio.create_task(self._index_query(query, context))

        slow_task = asyncio.create_task(self._run_slow_thinking(query, context))

        # Wait for slow thinking (the critical path)
        slow_result = await slow_task

        # Let indexing continue in background
        # Don't await index_task - it runs independently

        elapsed = (time.perf_counter() - start_time) * 1000

        # Combine fast and slow insights if fast had partial result
        if fast_result.confidence > 0.4 and fast_result.response:
            combined_response = self._combine_responses(fast_result.response, slow_result.content)
            return DualProcessResult(
                response=combined_response,
                thinking_mode="combined",
                confidence=slow_result.confidence,
                latency_ms=elapsed,
                fast_result=fast_result,
                slow_result=slow_result,
                metadata={"parallel": True},
            )

        return DualProcessResult(
            response=slow_result.content,
            thinking_mode="slow_only",
            confidence=slow_result.confidence,
            latency_ms=elapsed,
            fast_result=fast_result,
            slow_result=slow_result,
            metadata={"parallel": True},
        )

    async def _slow_only_think(
        self, query: str, context: dict[str, Any], start_time: float
    ) -> DualProcessResult:
        """Run only slow thinking without parallel indexing."""
        slow_result = await self._run_slow_thinking(query, context)

        elapsed = (time.perf_counter() - start_time) * 1000

        return DualProcessResult(
            response=slow_result.content,
            thinking_mode="slow_only",
            confidence=slow_result.confidence,
            latency_ms=elapsed,
            slow_result=slow_result,
            metadata={"parallel": False},
        )

    async def _run_slow_thinking(self, query: str, context: dict[str, Any]) -> BrainResponse:
        """Execute slow thinking via BrainClient."""
        # Run in thread pool to make it async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,  # Default executor
            self.slow_brain.think,
            query,
            context.get("domain", "general"),
            True,  # require_law_compliance
        )

    async def _index_query(self, query: str, context: dict[str, Any]) -> None:
        """
        Index query for future fast retrieval.

        This runs in background and doesn't block the response.
        """
        try:
            # Add to vector search index if available
            from amos_vector_search import ContentType, get_vector_service

            vector_service = get_vector_service()
            if vector_service:
                # Store query pattern for similar future queries
                await vector_service.add_embedding(
                    content_type=ContentType.CONVERSATION,
                    source_id=f"query_{hash(query) % 1000000}",
                    content=query,
                    metadata={"context": context},
                )
        except Exception:
            # Indexing failure shouldn't affect user experience
            pass

    def _combine_responses(self, fast_response: str, slow_response: str) -> str:
        """
        Combine fast and slow thinking results.

        Fast provides quick context, slow provides deep analysis.
        """
        return f"{fast_response}\n\n---\n\nDetailed Analysis:\n{slow_response}"

    def get_stats(self) -> dict[str, Any]:
        """Get dual-process statistics."""
        total = self.stats["total_queries"]
        if total == 0:
            return self.stats

        return {
            **self.stats,
            "fast_hit_rate": self.stats["fast_hits"] / total,
            "slow_fallback_rate": self.stats["slow_fallbacks"] / total,
            "parallel_rate": self.stats["parallel_executions"] / total,
        }


# Global instance
_dual_brain: Optional[DualProcessBrain] = None


def get_dual_process_brain() -> DualProcessBrain:
    """Get or create global dual-process brain."""
    global _dual_brain
    if _dual_brain is None:
        _dual_brain = DualProcessBrain()
    return _dual_brain


# Convenience function
async def dual_think(
    query: str, context: dict[str, Any] = None, prefer_fast: bool = False
) -> DualProcessResult:
    """Quick access to dual-process thinking."""
    brain = get_dual_process_brain()
    return await brain.think(query, context, prefer_fast)

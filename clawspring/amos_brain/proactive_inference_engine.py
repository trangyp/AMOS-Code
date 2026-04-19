from typing import Any, Dict, Optional, Set

"""Proactive Inference Engine for AMOS Brain

Separates internal deliberation from user-facing outputs to bound latency.
Based on research: Proactive architectures for bounded interactive latency.

Architecture:
- Fast Path: Immediate response (<100ms)
- Background Path: Deep deliberation (ongoing)
- Refinement: Update response if deep path finds better answer
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto

try:
    from .amos_kernel_runtime import AMOSKernelRuntime
except ImportError:
    from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402


class InferenceMode(Enum):
    """Inference execution modes."""

    FAST = auto()
    BACKGROUND = auto()
    REFINED = auto()


@dataclass
class InferenceResult:
    """Result from proactive inference."""

    response: str
    mode: InferenceMode
    confidence: float
    latency_ms: float
    deliberation_id: str
    can_refine: bool
    provisional: bool


@dataclass
class DeliberationState:
    """Background deliberation state."""

    deliberation_id: str
    query: str
    start_time: datetime
    fast_result: Optional[InferenceResult] = None
    refined_result: Optional[InferenceResult] = None
    complete: bool = False
    iterations: int = 0


class ProactiveInferenceEngine:
    """
    Proactive inference with bounded latency.

    Strategy:
    1. Return fast provisional response immediately
    2. Continue deliberation in background
    3. Notify if refined answer differs significantly
    """

    def __init__(
        self,
        kernel: Optional[AMOSKernelRuntime] = None,
        fast_budget_ms: float = 100.0,
        max_background_time_ms: float = 5000.0,
        refinement_threshold: float = 0.3,
    ):
        self.kernel = kernel or AMOSKernelRuntime()
        self.fast_budget_ms = fast_budget_ms
        self.max_background_time_ms = max_background_time_ms
        self.refinement_threshold = refinement_threshold

        # Background deliberations
        self._deliberations: Dict[str, DeliberationState] = {}
        self._background_tasks: Set[asyncio.Task[Any]] = set()

    async def infer(self, query: str, context: Dict[str, Any] = None) -> InferenceResult:
        """
        Main inference entry point.

        Returns fast result immediately, starts background refinement.
        """
        deliberation_id = f"delib_{int(time.time() * 1000)}"
        start_time = time.perf_counter()

        # Create deliberation state
        state = DeliberationState(
            deliberation_id=deliberation_id,
            query=query,
            start_time=datetime.now(timezone.utc),
        )
        self._deliberations[deliberation_id] = state

        # Generate fast response
        fast_result = await self._fast_inference(query, context, start_time)
        state.fast_result = fast_result

        # Start background refinement
        if fast_result.can_refine:
            coro = self._background_deliberation(deliberation_id, query, context)
            task = asyncio.create_task(coro)
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        return fast_result

    async def _fast_inference(
        self,
        query: str,
        context: Dict[str, Any],
        start_time: float,
    ) -> InferenceResult:
        """Fast inference under budget constraint."""
        # Use brain kernel for quick classification
        observation = {
            "query": query,
            "context": context or {},
            "mode": "fast",
        }
        goal = {"type": "fast_response", "target": query}

        # Execute brain cycle
        cycle_result = self.kernel.execute_cycle(observation, goal)

        # Generate fast response based on cycle result
        legality = cycle_result.get("legality", 0.5)

        # Simple response generation
        if legality > 0.7:
            response = f"Quick answer: {query[:50]}..."
            confidence = 0.7
        elif legality > 0.4:
            response = f"Provisional: {query[:50]} (checking deeper)..."
            confidence = 0.5
        else:
            response = f"I need a moment to analyze: {query[:50]}..."
            confidence = 0.3

        latency = (time.perf_counter() - start_time) * 1000

        return InferenceResult(
            response=response,
            mode=InferenceMode.FAST,
            confidence=confidence,
            latency_ms=latency,
            deliberation_id=f"delib_{int(time.time() * 1000)}",
            can_refine=True,
            provisional=confidence < 0.7,
        )

    async def _background_deliberation(
        self,
        deliberation_id: str,
        query: str,
        context: Dict[str, Any],
    ) -> None:
        """Background deep deliberation."""
        state = self._deliberations.get(deliberation_id)
        if not state:
            return

        start_time = time.perf_counter()

        # Simulate deeper analysis
        await asyncio.sleep(0.1)  # Background work

        # Generate refined response
        observation = {
            "query": query,
            "context": context or {},
            "mode": "deep",
            "fast_response": state.fast_result.response if state.fast_result else "",
        }
        goal = {"type": "refined_response", "target": query}

        cycle_result = self.kernel.execute_cycle(observation, goal)

        # Check if refinement is meaningfully different
        legality = cycle_result.get("legality", 0.5)
        refined_confidence = min(legality + 0.2, 0.95)

        # Only create refined result if confidence improved significantly
        if state.fast_result and refined_confidence > state.fast_result.confidence + 0.2:
            refined_result = InferenceResult(
                response=f"Refined answer for: {query[:50]} (confidence: {refined_confidence:.2f})",
                mode=InferenceMode.REFINED,
                confidence=refined_confidence,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                deliberation_id=deliberation_id,
                can_refine=False,
                provisional=False,
            )
            state.refined_result = refined_result

        state.complete = True
        state.iterations += 1

    def get_refinement(self, deliberation_id: str) -> Optional[InferenceResult]:
        """Get refined result if available."""
        state = self._deliberations.get(deliberation_id)
        if state and state.refined_result:
            return state.refined_result
        return None

    def is_deliberation_complete(self, deliberation_id: str) -> bool:
        """Check if background deliberation is complete."""
        state = self._deliberations.get(deliberation_id)
        return state.complete if state else False


# Global engine instance
_global_engine: Optional[ProactiveInferenceEngine] = None


def get_proactive_engine() -> ProactiveInferenceEngine:
    """Get or create global proactive inference engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = ProactiveInferenceEngine()
    return _global_engine


if __name__ == "__main__":

    async def test():
        engine = get_proactive_engine()

        # Test fast inference
        result = await engine.infer("What is the capital of France?")
        print(f"Fast result: {result.response}")
        print(f"Latency: {result.latency_ms:.1f}ms")
        print(f"Provisional: {result.provisional}")

        # Wait for background
        await asyncio.sleep(0.2)

        # Check for refinement
        refined = engine.get_refinement(result.deliberation_id)
        if refined:
            print(f"\nRefined: {refined.response}")

    asyncio.run(test())

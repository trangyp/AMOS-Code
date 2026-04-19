"""Brain Event Integration - Real-time Brain Processing Events

Integrates brain processing with event streaming for real-time updates.
Based on research: Event-driven agent architectures for responsive systems.
"""

import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Dict, List, Optional, Protocol

from amos_brain.integrated_brain_api import (
    BrainResponse,
    IntegratedBrainAPI,
    get_brain_api,
)


class EventEmitter(Protocol):
    """Protocol for event emission."""

    async def emit(self, event_type: str, payload: Dict[str, Any], source: str) -> None:
        """Emit an event."""
        ...


@dataclass
class BrainProcessingEvent:
    """Event for brain processing step."""

    query_id: str
    step: str
    iteration: int
    thought: str
    action: str
    observation: str
    latency_ms: float
    timestamp: str


class BrainEventProcessor:
    """
    Process brain queries with real-time event streaming.

    Emits events for each step of brain processing:
    - query_received
    - processing_started
    - thought_generated
    - action_executed
    - observation_received
    - result_ready
    """

    def __init__(
        self,
        brain: Optional[IntegratedBrainAPI] = None,
        event_emitter: Optional[EventEmitter] = None,
    ):
        self.brain = brain or get_brain_api()
        self.emitter = event_emitter
        self._active_queries: Dict[str, dict[str, Any]] = {}

    async def process_with_events(
        self,
        query: str,
        mode: str = "auto",
        context: Dict[str, Any] = None,
    ) -> BrainResponse:
        """
        Process query with event streaming.

        Args:
            query: User query
            mode: Processing mode
            context: Additional context

        Returns:
            BrainResponse with final result
        """
        query_id = f"brain_{uuid.uuid4().hex[:8]}"
        start_time = time.perf_counter()

        # Emit query received
        await self._emit(
            "query_received",
            {
                "query_id": query_id,
                "query": query[:100],
                "mode": mode,
            },
        )

        # Track query
        self._active_queries[query_id] = {
            "start_time": start_time,
            "query": query,
            "status": "processing",
        }

        # Emit processing started
        await self._emit(
            "processing_started",
            {
                "query_id": query_id,
                "components": self._estimate_components(mode),
            },
        )

        try:
            # Process with brain
            result = await self.brain.process(query, mode, context)

            # Calculate total latency
            total_latency = (time.perf_counter() - start_time) * 1000

            # Emit result ready
            await self._emit(
                "result_ready",
                {
                    "query_id": query_id,
                    "response": result.response[:200],
                    "confidence": result.confidence,
                    "latency_ms": total_latency,
                    "components_used": result.components_used,
                },
            )

            # Update tracking
            self._active_queries[query_id]["status"] = "completed"
            self._active_queries[query_id]["result"] = result

            return result

        except Exception as e:
            # Emit error
            await self._emit(
                "processing_error",
                {
                    "query_id": query_id,
                    "error": str(e),
                },
            )

            self._active_queries[query_id]["status"] = "error"
            self._active_queries[query_id]["error"] = str(e)
            raise

    async def stream_react_steps(
        self,
        query: str,
        available_tools: List[str] = None,
    ) -> AsyncIterator[BrainProcessingEvent]:
        """
        Stream ReAct steps in real-time.

        Yields:
            BrainProcessingEvent for each step
        """
        query_id = f"react_{uuid.uuid4().hex[:8]}"
        iteration = 0

        from amos_brain.react_agent import get_react_agent

        agent = get_react_agent()

        while iteration < agent.max_iterations:
            iteration += 1
            step_start = time.perf_counter()

            # Generate thought
            thought = f"Iteration {iteration}: Analyzing {query[:50]}..."

            yield BrainProcessingEvent(
                query_id=query_id,
                step="thought",
                iteration=iteration,
                thought=thought,
                action=None,
                observation=None,
                latency_ms=(time.perf_counter() - step_start) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Simulate action (in real implementation, this would call tools)
            action = f"analyze({query[:30]})"

            yield BrainProcessingEvent(
                query_id=query_id,
                step="action",
                iteration=iteration,
                thought=thought,
                action=action,
                observation=None,
                latency_ms=(time.perf_counter() - step_start) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Simulate observation
            observation = f"Analysis complete for iteration {iteration}"

            yield BrainProcessingEvent(
                query_id=query_id,
                step="observation",
                iteration=iteration,
                thought=thought,
                action=action,
                observation=observation,
                latency_ms=(time.perf_counter() - step_start) * 1000,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Check termination condition
            if iteration >= 3:  # Simplified
                break

        # Final answer
        final_start = time.perf_counter()
        yield BrainProcessingEvent(
            query_id=query_id,
            step="complete",
            iteration=iteration,
            thought=None,
            action=None,
            observation=None,
            latency_ms=(time.perf_counter() - final_start) * 1000,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _estimate_components(self, mode: str) -> List[str]:
        """Estimate which components will be used."""
        if mode == "fast":
            return ["proactive_inference"]
        elif mode == "react":
            return ["react_agent"]
        elif mode == "reflect":
            return ["reflection"]
        else:
            return ["proactive_inference", "react_agent", "reflection"]

    async def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        """Emit event if emitter is available."""
        if self.emitter:
            await self.emitter.emit(event_type, payload, "brain")

    def get_active_queries(self) -> Dict[str, dict[str, Any]]:
        """Get currently active queries."""
        return self._active_queries.copy()

    def cleanup_completed(self) -> int:
        """Remove completed queries from tracking."""
        completed = [
            qid
            for qid, data in self._active_queries.items()
            if data.get("status") in ("completed", "error")
        ]
        for qid in completed:
            del self._active_queries[qid]
        return len(completed)


# Global instance
_global_event_processor: Optional[BrainEventProcessor] = None


def get_brain_event_processor() -> BrainEventProcessor:
    """Get or create global brain event processor."""
    global _global_event_processor
    if _global_event_processor is None:
        _global_event_processor = BrainEventProcessor()
    return _global_event_processor


async def _test_main() -> None:
    processor = get_brain_event_processor()

    # Test basic processing
    result = await processor.process_with_events(
        "Test query for event streaming",
        mode="fast",
    )
    print(f"Result: {result.response[:50]}...")

    # Test streaming
    print("\nStreaming ReAct steps:")
    async for event in processor.stream_react_steps("Analyze this"):
        print(f"  Step {event.iteration}: {event.step}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(_test_main())

from typing import Any, Optional

"""
AMOS FastLoop Runtime
Integrated FastLoop execution engine.

Implements: InterruptClassify → Route → FastCommit → Escalate
Target: 80% of requests < 50ms
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any

from amos_delta_state import create_delta, get_delta_manager
from amos_fastloop_classifier import (
    ClassificationResult,
    InterruptClass,
    classify_request,
    get_classifier,
    is_fast_path,
)
from amos_sparse_router import (
    ActiveModuleSet,
    ModuleType,
    RouteResult,
    get_router,
    route_classification,
)


@dataclass
class FastLoopResult:
    """Result of FastLoop execution."""

    success: bool
    output: Any
    latency_ms: float
    classification: ClassificationResult
    route: RouteResult
    state_id: Optional[str]
    escalation_triggered: bool = False
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FastLoopRuntime:
    """
    FastLoop execution engine for AMOS.

    Pipeline:
    1. Interrupt Classify (< 1ms)
    2. Sparse Route (< 1ms)
    3. Delta State Load (< 5ms)
    4. Fast Commit (variable, bounded)
    5. Compact Output (< 1ms)
    """

    def __init__(self):
        self.classifier = get_classifier()
        self.router = get_router()
        self.state_manager = get_delta_manager()
        self._request_count = 0
        self._fast_path_count = 0
        self._escalation_count = 0
        self._total_latency_ms = 0.0

    async def execute(
        self,
        request: str,
        current_state_id: Optional[str] = None,
        context: Dict[str, Any] = None,
    ) -> FastLoopResult:
        """
        Execute request through FastLoop.

        Args:
            request: Input request string
            current_state_id: Optional current state to update
            context: Additional context

        Returns:
            FastLoopResult with output and metrics
        """
        start_time = time.perf_counter()
        self._request_count += 1

        try:
            # === 1. INTERRUPT CLASSIFY (< 1ms) ===
            classification = await classify_request(request)

            # Check for immediate escalation
            if classification.class_type == InterruptClass.ESCALATION:
                self._escalation_count += 1
                latency = (time.perf_counter() - start_time) * 1000
                return FastLoopResult(
                    success=True,
                    output={"status": "escalated", "message": "Request escalated to human"},
                    latency_ms=latency,
                    classification=classification,
                    route=RouteResult(
                        module_set=ActiveModuleSet(
                            modules={ModuleType.INTERFACE},
                            latency_budget_ms=5.0,
                            verification_tier="none",
                            search_limits={},
                        ),
                        routing_latency_ms=0.0,
                    ),
                    state_id=current_state_id,
                    escalation_triggered=True,
                )

            # === 2. SPARSE ROUTE (< 1ms) ===
            route = await route_classification(classification)

            # === 3. DELTA STATE LOAD (< 5ms) ===
            if current_state_id:
                state = self.state_manager.get_full_state(current_state_id)
            else:
                state = None

            # === 4. FAST COMMIT (bounded) ===
            if is_fast_path(classification):
                self._fast_path_count += 1
                output = await self._execute_fast_path(
                    request, classification, route, state, context
                )
            else:
                # REASONING - requires full loop, but with bounds
                output = await self._execute_bounded_reasoning(
                    request, classification, route, state, context
                )

            # === 5. COMPACT OUTPUT (< 1ms) ===
            # Default to structured output, not natural language
            if not isinstance(output, dict):
                output = {"result": output}

            # Update state if provided
            new_state_id = current_state_id
            if current_state_id and isinstance(output, dict):
                delta = create_delta("last_result", output)
                new_state = self.state_manager.apply_delta(current_state_id, delta)
                if new_state:
                    new_state_id = new_state.state_id

            latency = (time.perf_counter() - start_time) * 1000
            self._total_latency_ms += latency

            return FastLoopResult(
                success=True,
                output=output,
                latency_ms=latency,
                classification=classification,
                route=route,
                state_id=new_state_id,
                escalation_triggered=False,
            )

        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            return FastLoopResult(
                success=False,
                output=None,
                latency_ms=latency,
                classification=ClassificationResult(
                    class_type=InterruptClass.UNKNOWN, confidence=0.0, latency_ms=0.0
                )
                if "classification" not in locals()
                else classification,
                route=RouteResult(
                    module_set=ActiveModuleSet(
                        modules=set(),
                        latency_budget_ms=0.0,
                        verification_tier="none",
                        search_limits={},
                    ),
                    routing_latency_ms=0.0,
                )
                if "route" not in locals()
                else route,
                state_id=current_state_id,
                error=str(e),
            )

    async def _execute_fast_path(
        self,
        request: str,
        classification: ClassificationResult,
        route: RouteResult,
        state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute fast path request."""
        class_type = classification.class_type

        if class_type == InterruptClass.QUERY:
            # Information retrieval
            return await self._execute_query(request, state, context)

        elif class_type == InterruptClass.ACTION:
            # State mutation
            return await self._execute_action(request, state, context)

        elif class_type == InterruptClass.ECHO:
            # Identity/passthrough
            return {"echo": request, "timestamp": datetime.now(timezone.utc).isoformat()}

        return {"error": "Unknown fast path type"}

    async def _execute_query(
        self, request: str, state: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute query against state."""
        # Simple query implementation
        # In production, this would use vector search, knowledge base, etc.

        # Extract query terms (simplified)
        terms = request.lower().split()

        # Search state if available
        results = []
        if state:
            for key, value in state.items():
                if any(term in str(key).lower() or term in str(value).lower() for term in terms):
                    results.append({"key": key, "value": value})

        return {
            "query": request,
            "results": results[:10],  # Limit results
            "count": len(results),
            "source": "state" if state else "none",
        }

    async def _execute_action(
        self, request: str, state: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute state mutation action."""
        # Parse action (simplified)
        # In production, this would use structured action parsing

        action_type = "unknown"
        if "create" in request.lower() or "add" in request.lower():
            action_type = "create"
        elif "update" in request.lower() or "set" in request.lower():
            action_type = "update"
        elif "delete" in request.lower() or "remove" in request.lower():
            action_type = "delete"

        return {
            "action": action_type,
            "request": request,
            "status": "acknowledged",
            "previous_state_keys": list(state.keys()) if state else [],
        }

    async def _execute_bounded_reasoning(
        self,
        request: str,
        classification: ClassificationResult,
        route: RouteResult,
        state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute reasoning with strict bounds.

        Limits from routing:
        - branches: max 3
        - horizon: max 2
        - depth: max 2
        """
        limits = route.module_set.search_limits

        # Simulate bounded reasoning
        # In production, this would call the AMOS brain with limits enforced

        return {
            "reasoning_type": "bounded",
            "request": request,
            "limits_applied": limits,
            "branches_explored": min(limits.get("branches", 3), 3),
            "horizon_reached": min(limits.get("horizon", 2), 2),
            "state_accessed": state is not None,
            "note": "Full AMOS reasoning would execute here with enforced bounds",
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get runtime statistics."""
        return {
            "total_requests": self._request_count,
            "fast_path_count": self._fast_path_count,
            "escalation_count": self._escalation_count,
            "fast_path_rate": self._fast_path_count / max(1, self._request_count),
            "avg_latency_ms": self._total_latency_ms / max(1, self._request_count),
            "classifier_stats": self.classifier.get_stats(),
            "router_stats": self.router.get_stats(),
            "state_stats": self.state_manager.get_stats(),
        }


# Global singleton
_runtime: Optional[FastLoopRuntime] = None


def get_fastloop_runtime() -> FastLoopRuntime:
    """Get global FastLoop runtime."""
    global _runtime
    if _runtime is None:
        _runtime = FastLoopRuntime()
    return _runtime


async def fastloop_execute(
    request: str, state_id: Optional[str] = None, context: Dict[str, Any] = None
) -> FastLoopResult:
    """Convenience function for FastLoop execution."""
    runtime = get_fastloop_runtime()
    return await runtime.execute(request, state_id, context)


# Test
if __name__ == "__main__":

    async def test():
        print("\n" + "=" * 60)
        print("AMOS FastLoop Runtime Test")
        print("=" * 60)

        test_cases = [
            ("What is the current status?", None),
            ("Deploy the application", None),
            ("Explain the architecture tradeoffs", None),
            ("Help with a critical bug", None),
            ("Hello", None),
            ("List all users", None),
            ("Ping", None),
            ("Analyze performance bottleneck", None),
        ]

        runtime = get_fastloop_runtime()

        for request, state_id in test_cases:
            result = await runtime.execute(request, state_id)

            fast_marker = (
                "⚡ FAST"
                if not result.escalation_triggered
                and result.classification.class_type
                in [InterruptClass.QUERY, InterruptClass.ACTION, InterruptClass.ECHO]
                else "🐢 SLOW"
                if result.classification.class_type == InterruptClass.REASONING
                else "📢 ESC"
            )

            print(
                f"\n{fast_marker} {result.classification.class_type.name:12} {result.latency_ms:6.2f}ms | {request[:40]}..."
            )
            print(
                f"   Modules: {len(result.route.module_set.modules)} | Output keys: {list(result.output.keys()) if isinstance(result.output, dict) else 'N/A'}"
            )

        print("\n" + "=" * 60)
        stats = runtime.get_stats()
        print(f"Total requests: {stats['total_requests']}")
        print(f"Fast path rate: {stats['fast_path_rate']:.1%}")
        print(f"Avg latency: {stats['avg_latency_ms']:.2f}ms")
        print(f"Cache hit rate: {stats['classifier_stats']['cache_hit_rate']:.1%}")
        print("=" * 60)

    asyncio.run(test())

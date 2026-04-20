from __future__ import annotations

from typing import Any, Optional

"""AMOS Intelligent Task Router

Routes tasks to appropriate execution engines based on reading kernel analysis.
Integrates reading kernel with orchestrator bridge for end-to-end task execution.
"""


import time
import uuid
from dataclasses import dataclass

from backend.amos_reading_kernel import ResponseMode, get_reading_service
from backend.real_orchestrator_bridge import TaskResult, get_real_orchestrator_bridge


@dataclass
class RoutedTask:
    """Task with routing information."""

    task_id: str
    original_text: str
    reading_result: Any
    routing_decision: str
    target_engine: Optional[str]
    estimated_duration_ms: float
    priority: str
    queued_at: float


@dataclass
class RoutingResult:
    """Result of task routing and execution."""

    task_id: str
    routed: bool
    executed: bool
    reading_latency_ms: float
    routing_latency_ms: float
    execution_latency_ms: float
    total_latency_ms: float
    result: Optional[TaskResult]
    error: Optional[str] = None


class IntelligentTaskRouter:
    """Routes tasks from reading to execution."""

    _instance: Optional[IntelligentTaskRouter] = None

    def __new__(cls) -> IntelligentTaskRouter:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._reading_service = get_reading_service()
        self._orchestrator = get_real_orchestrator_bridge()
        self._routing_history: list[RoutingResult] = []
        self._initialized = True

    async def route_and_execute(self, text: str, context: dict[str, Any] = None) -> RoutingResult:
        """Complete pipeline: read → route → execute."""
        total_start = time.time()
        task_id = f"route_{uuid.uuid4().hex[:12]}"

        # Step 1: Reading
        read_start = time.time()
        reading = self._reading_service.process(text, context)
        reading_latency = (time.time() - read_start) * 1000

        # Step 2: Routing decision
        route_start = time.time()

        if reading.verified_goal.mode == ResponseMode.CLARIFY:
            routing_latency = (time.time() - route_start) * 1000
            total_latency = (time.time() - total_start) * 1000
            result = RoutingResult(
                task_id=task_id,
                routed=False,
                executed=False,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=0,
                total_latency_ms=total_latency,
                result=None,
                error="Needs clarification: "
                + "; ".join(reading.stable_read.clarification_questions),
            )
            self._routing_history.append(result)
            return result

        if reading.verified_goal.mode == ResponseMode.BLOCK:
            routing_latency = (time.time() - route_start) * 1000
            total_latency = (time.time() - total_start) * 1000
            result = RoutingResult(
                task_id=task_id,
                routed=False,
                executed=False,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=0,
                total_latency_ms=total_latency,
                result=None,
                error="Task blocked: " + reading.verified_goal.reason,
            )
            self._routing_history.append(result)
            return result

        if not reading.verified_goal.executable:
            routing_latency = (time.time() - route_start) * 1000
            total_latency = (time.time() - total_start) * 1000
            result = RoutingResult(
                task_id=task_id,
                routed=False,
                executed=False,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=0,
                total_latency_ms=total_latency,
                result=None,
                error="Task not executable: " + reading.verified_goal.reason,
            )
            self._routing_history.append(result)
            return result

        # Determine routing
        plan = reading.execution_plan
        if not plan:
            routing_latency = (time.time() - route_start) * 1000
            total_latency = (time.time() - total_start) * 1000
            result = RoutingResult(
                task_id=task_id,
                routed=False,
                executed=False,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=0,
                total_latency_ms=total_latency,
                result=None,
                error="No execution plan generated",
            )
            self._routing_history.append(result)
            return result

        routing_latency = (time.time() - route_start) * 1000

        # Step 3: Execution via orchestrator
        exec_start = time.time()

        priority = "HIGH" if plan.get("priority") == "high" else "MEDIUM"

        try:
            task_result = await self._orchestrator.execute_task(
                task_description=text,
                priority=priority,
                context={
                    "reading_result": {
                        "primary_goal": reading.stable_read.primary_goal,
                        "domain": plan.get("domain"),
                        "action_type": plan.get("action_type"),
                        "confidence": reading.verified_goal.confidence,
                    }
                },
            )
            execution_latency = (time.time() - exec_start) * 1000
            total_latency = (time.time() - total_start) * 1000

            routing_result = RoutingResult(
                task_id=task_id,
                routed=True,
                executed=task_result.success,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=execution_latency,
                total_latency_ms=total_latency,
                result=task_result,
                error=task_result.error,
            )
            self._routing_history.append(routing_result)
            return routing_result

        except Exception as e:
            execution_latency = (time.time() - exec_start) * 1000
            total_latency = (time.time() - total_start) * 1000
            result = RoutingResult(
                task_id=task_id,
                routed=True,
                executed=False,
                reading_latency_ms=reading_latency,
                routing_latency_ms=routing_latency,
                execution_latency_ms=execution_latency,
                total_latency_ms=total_latency,
                result=None,
                error=f"Execution failed: {str(e)}",
            )
            self._routing_history.append(result)
            return result

    def get_history(self, limit: int = 100) -> list[RoutingResult]:
        """Get routing history."""
        return self._routing_history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get routing statistics."""
        if not self._routing_history:
            return {
                "total": 0,
                "success_rate": 0,
                "avg_total_latency_ms": 0,
            }

        total = len(self._routing_history)
        executed = sum(1 for r in self._routing_history if r.executed)

        return {
            "total": total,
            "routed": sum(1 for r in self._routing_history if r.routed),
            "executed": executed,
            "success_rate": executed / total if total > 0 else 0,
            "avg_reading_latency_ms": sum(r.reading_latency_ms for r in self._routing_history)
            / total,
            "avg_routing_latency_ms": sum(r.routing_latency_ms for r in self._routing_history)
            / total,
            "avg_execution_latency_ms": sum(r.execution_latency_ms for r in self._routing_history)
            / total,
            "avg_total_latency_ms": sum(r.total_latency_ms for r in self._routing_history) / total,
        }


# Global router instance
_intelligent_router: Optional[IntelligentTaskRouter] = None


def get_intelligent_router() -> IntelligentTaskRouter:
    """Get or create global intelligent router."""
    global _intelligent_router
    if _intelligent_router is None:
        _intelligent_router = IntelligentTaskRouter()
    return _intelligent_router


async def route_task(text: str, context: dict[str, Any] = None) -> RoutingResult:
    """Route a task through the intelligent router."""
    router = get_intelligent_router()
    return await router.route_and_execute(text, context)

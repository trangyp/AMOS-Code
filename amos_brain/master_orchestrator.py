"""AMOS Brain Master Orchestrator - Central cognitive orchestration interface."""


from dataclasses import dataclass
from typing import Any

from .cognitive_engine import get_cognitive_engine
from .meta_controller import get_meta_controller


@dataclass
class OrchestrationResult:
    """Result of an orchestrated cognitive task."""

    output: str
    confidence: float
    metadata: dict[str, Any]


class MasterOrchestrator:
    """Master orchestrator for cognitive tasks."""

    def __init__(self) -> None:
        self._meta_controller = get_meta_controller()
        self._cognitive_engine = get_cognitive_engine()

    def orchestrate_cognitive_task(
        self, task: str, domain: str = "general", context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Orchestrate a cognitive task.

        Args:
            task: The task description/query
            domain: Domain for the task (default: general)
            context: Additional context

        Returns:
            Dict with output, confidence, and metadata
        """
from __future__ import annotations

        # Use cognitive engine for direct processing
        result = self._cognitive_engine.process(task, domain=domain, context=context)

        return {
            "output": result.content,
            "confidence": 0.85 if result.confidence == "high" else 0.75 if result.confidence == "medium" else 0.6,
            "metadata": result.metadata,
        }

    def orchestrate_goal(
        self, goal: str, domain: str = "general", auto_execute: bool = False
    ) -> Any:
        """Orchestrate achievement of a complex goal.

        Args:
            goal: The goal to achieve
            domain: Domain for the goal
            auto_execute: Whether to auto-execute the plan

        Returns:
            WorkflowPlan or execution result
        """
        return self._meta_controller.orchestrate(goal, domain, auto_execute)


# Global singleton instance
_master_orchestrator: MasterOrchestrator | None = None


def get_orchestrator() -> MasterOrchestrator:
    """Get the singleton MasterOrchestrator instance."""
    global _master_orchestrator
    if _master_orchestrator is None:
        _master_orchestrator = MasterOrchestrator()
    return _master_orchestrator


def reset_orchestrator() -> None:
    """Reset the orchestrator singleton (for testing)."""
    global _master_orchestrator
    _master_orchestrator = None


__all__ = [
    "MasterOrchestrator",
    "OrchestrationResult",
    "get_orchestrator",
    "reset_orchestrator",
]  # type: ignore

from typing import Any

"""Cognitive Task Processor - Brain-powered task execution.

Processes cognitive tasks using the AMOS brain with proper
result tracking and error handling.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timezone

UTC = UTC
from .facade import BrainClient


@dataclass
class CognitiveTaskResponse:
    """Response from cognitive task processing."""

    task_id: str
    success: bool
    domain: str
    engines_used: list[str]
    duration_ms: float
    timestamp: str
    result: dict[str, Any]


def process_cognitive_task(
    description: str, priority: str = "MEDIUM", context: dict[str, Any] = None
) -> CognitiveTaskResponse:
    """Process a cognitive task using the brain.

    Args:
        description: Task description/query
        priority: Task priority (LOW, MEDIUM, HIGH)
        context: Additional context for processing

    Returns:
        CognitiveTaskResponse with results
    """
    import time
    import uuid

    start_time = time.perf_counter()
    task_id = f"ct_{uuid.uuid4().hex[:12]}"

    client = BrainClient()

    try:
        # Use brain to process the task
        response = client.think(
            description, domain=context.get("domain", "general") if context else "general"
        )

        duration_ms = (time.perf_counter() - start_time) * 1000

        return CognitiveTaskResponse(
            task_id=task_id,
            success=response.success,
            domain=context.get("domain", "general") if context else "general",
            engines_used=["brain", "cognitive"],
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc).isoformat(),
            result={
                "content": response.content,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "law_compliant": response.law_compliant,
                "violations": response.violations,
            },
        )
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000

        return CognitiveTaskResponse(
            task_id=task_id,
            success=False,
            domain="error",
            engines_used=[],
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc).isoformat(),
            result={"error": str(e), "error_type": type(e).__name__},
        )

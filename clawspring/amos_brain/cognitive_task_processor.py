from typing import Any, Dict, List, Optional

"""AMOS Cognitive Task Processor - Production task execution using brain/organism.

Real implementation that uses:
- MasterOrchestrator for cognitive routing
- OrganismBridge for enhanced execution
- Predictive integration for outcome forecasting
- Task execution for actual work

Owner: Trang Phan
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

try:
    from .master_orchestrator import get_master_orchestrator
    from .organism_bridge import get_organism_bridge
except ImportError:
    from master_orchestrator import get_master_orchestrator

    from organism_bridge import get_organism_bridge


@dataclass
class TaskRequest:
    """Request for cognitive task processing."""

    description: str
    priority: str = "MEDIUM"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResponse:
    """Response from cognitive task processing."""

    task_id: str
    success: bool
    domain: str
    result: Dict[str, Any]
    duration_ms: float
    engines_used: List[str]
    timestamp: str


class CognitiveTaskProcessor:
    """Production task processor using AMOS brain ecosystem."""

    def __init__(self):
        self._orchestrator = None
        self._organism = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize brain connections."""
        try:
            self._orchestrator = get_master_orchestrator()
            self._organism = get_organism_bridge()
            self._initialized = True
            return True
        except Exception as e:
            print(f"[TaskProcessor] Initialization failed: {e}")
            return False

    def process_task(self, request: TaskRequest) -> TaskResponse:
        """Process a cognitive task using full brain/organism stack."""
        if not self._initialized:
            self.initialize()

        task_id = f"task-{uuid.uuid4().hex[:8]}"
        start = time.time()

        # Get organism enhancement
        organism_data = {}
        if self._organism:
            try:
                enhancement = self._organism.enhance_cognitive_analysis(request.description)
                organism_data = enhancement.get("organism_enhancements", {})
            except Exception:
                pass

        # Execute via orchestrator
        result = self._orchestrator.orchestrate_cognitive_task(
            task_id, request.description, request.priority
        )

        duration = (time.time() - start) * 1000

        return TaskResponse(
            task_id=task_id,
            success=result.overall_success,
            domain=result.domain,
            result={
                "analysis": result.analysis,
                "prediction": result.prediction,
                "execution": result.execution,
                "organism_data": organism_data,
            },
            duration_ms=duration,
            engines_used=result.analysis.get("recommended_engines", []),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Singleton
_processor: Optional[CognitiveTaskProcessor] = None


def get_task_processor() -> CognitiveTaskProcessor:
    """Get or create singleton processor."""
    global _processor
    if _processor is None:
        _processor = CognitiveTaskProcessor()
        _processor.initialize()
    return _processor


def process_cognitive_task(description: str, priority: str = "MEDIUM") -> TaskResponse:
    """Convenience function to process a task."""
    processor = get_task_processor()
    return processor.process_task(TaskRequest(description=description, priority=priority))


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS COGNITIVE TASK PROCESSOR")
    print("=" * 60)

    test_tasks = [
        "Design REST API for user authentication",
        "Optimize database query performance",
        "Create monitoring dashboard",
    ]

    for task in test_tasks:
        print(f"\nProcessing: {task[:50]}...")
        response = process_cognitive_task(task, "HIGH")
        print(f"  Domain: {response.domain}")
        print(f"  Success: {response.success}")
        print(f"  Duration: {response.duration_ms:.1f}ms")
        print(f"  Engines: {', '.join(response.engines_used[:3])}")

    print("\n" + "=" * 60)
    print("Processing complete")

#!/usr/bin/env python3
"""AMOS Unified Execution Engine - Coordinates all 15 organism subsystems."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExecutionResult:
    """Result from subsystem execution."""

    subsystem: str
    task: str
    status: str
    output: Any
    timestamp: str
    duration_ms: float


@dataclass
class UnifiedExecutionContext:
    """Context for coordinating multi-subsystem execution."""

    task: str
    parameters: dict[str, Any] = field(default_factory=dict)
    subsystems_involved: list[str] = field(default_factory=list)
    results: list[ExecutionResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class UnifiedExecutionEngine:
    """Coordinates execution across all 15 AMOS organism subsystems.

    This is the execution layer that bridges the brain's cognitive
    processing with the organism's physical subsystems.
    """

    SUBSYSTEMS = {
        "01_BRAIN": "Cognitive processing and reasoning",
        "02_SENSES": "Environmental scanning and context",
        "03_IMMUNE": "Anomaly detection and security",
        "04_BLOOD": "Resource and budget management",
        "05_MUSCLE": "Task execution engine",
        "06_HEART": "Workflow orchestration",
        "07_MOUTH": "Communication interface",
        "08_EARS": "Data ingestion pipeline",
        "09_EYES": "Monitoring and observability",
        "10_HANDS": "Action execution",
        "11_NERVES": "Event processing system",
        "12_ETHICS": "Validation and compliance",
        "13_REFLEX": "Automated responses",
        "14_INTERFACES": "System integration",
        "15_MEMORY": "State persistence",
    }

    def __init__(self):
        """Initialize the unified execution engine."""
        self.initialized = False
        self.execution_count = 0
        self.subsystem_status = dict.fromkeys(self.SUBSYSTEMS, "idle")

    def initialize(self) -> dict[str, Any]:
        """Initialize all 15 subsystems."""
        try:
            from amos_brain import initialize_organism

            organism = initialize_organism()

            self.initialized = True
            return {
                "status": "initialized",
                "subsystems": 15,
                "organism": organism is not None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            # Fallback: initialize without organism bridge
            self.initialized = True
            return {
                "status": "initialized_standalone",
                "subsystems": 15,
                "organism": False,
                "note": f"Using standalone mode: {e}",
            }

    def route_to_subsystem(self, task: str) -> list[str]:
        """Determine which subsystems should handle a task.

        Returns list of subsystem codes based on task analysis.
        """
        task_lower = task.lower()
        subsystems = []

        # Task routing logic
        if any(w in task_lower for w in ["analyze", "think", "reason", "cognitive"]):
            subsystems.append("01_BRAIN")

        if any(w in task_lower for w in ["scan", "sense", "detect", "environment"]):
            subsystems.append("02_SENSES")

        if any(w in task_lower for w in ["security", "anomaly", "threat", "audit"]):
            subsystems.append("03_IMMUNE")

        if any(w in task_lower for w in ["budget", "resource", "cost", "finance"]):
            subsystems.append("04_BLOOD")

        if any(w in task_lower for w in ["execute", "run", "process", "task"]):
            subsystems.append("05_MUSCLE")

        if any(w in task_lower for w in ["workflow", "orchestrate", "coordinate"]):
            subsystems.append("06_HEART")

        if any(w in task_lower for w in ["communicate", "message", "notify", "report"]):
            subsystems.append("07_MOUTH")

        if any(w in task_lower for w in ["ingest", "collect", "gather", "data"]):
            subsystems.append("08_EARS")

        if any(w in task_lower for w in ["monitor", "observe", "track", "watch"]):
            subsystems.append("09_EYES")

        if any(w in task_lower for w in ["action", "perform", "do", "implement"]):
            subsystems.append("10_HANDS")

        if any(w in task_lower for w in ["event", "trigger", "response", "react"]):
            subsystems.append("11_NERVES")

        if any(w in task_lower for w in ["validate", "compliance", "ethics", "check"]):
            subsystems.append("12_ETHICS")

        if any(w in task_lower for w in ["auto", "reflex", "immediate", "quick"]):
            subsystems.append("13_REFLEX")

        if any(w in task_lower for w in ["integrate", "connect", "interface", "bridge"]):
            subsystems.append("14_INTERFACES")

        if any(w in task_lower for w in ["remember", "store", "persist", "memory"]):
            subsystems.append("15_MEMORY")

        # Default: include BRAIN and MUSCLE if no specific match
        if not subsystems:
            subsystems = ["01_BRAIN", "05_MUSCLE"]

        return subsystems

    def execute(self, task: str, parameters: dict = None) -> UnifiedExecutionContext:
        """Execute a task across coordinated subsystems.

        This is the main execution entry point that:
        1. Routes task to appropriate subsystems
        2. Executes on each subsystem
        3. Collects and returns results
        """
        import time

        start_time = time.time()
        self.execution_count += 1

        # Create execution context
        context = UnifiedExecutionContext(
            task=task,
            parameters=parameters or {},
            subsystems_involved=self.route_to_subsystem(task),
            metadata={
                "execution_id": self.execution_count,
                "start_time": datetime.now().isoformat(),
            },
        )

        # Execute on each subsystem
        for subsystem_code in context.subsystems_involved:
            subsystem_start = time.time()

            # Simulate subsystem execution
            self.subsystem_status[subsystem_code] = "executing"

            result = self._execute_on_subsystem(subsystem_code, task, context.parameters)

            context.results.append(
                ExecutionResult(
                    subsystem=subsystem_code,
                    task=task,
                    status=result.get("status", "unknown"),
                    output=result.get("output"),
                    timestamp=datetime.now().isoformat(),
                    duration_ms=(time.time() - subsystem_start) * 1000,
                )
            )

            self.subsystem_status[subsystem_code] = "idle"

        context.metadata["duration_ms"] = (time.time() - start_time) * 1000
        context.metadata["end_time"] = datetime.now().isoformat()

        return context

    def _execute_on_subsystem(self, subsystem: str, task: str, params: dict) -> dict:
        """Execute task on a specific subsystem."""
        subsystem_name = self.SUBSYSTEMS.get(subsystem, "Unknown")

        # Simulate subsystem-specific processing
        return {
            "status": "completed",
            "output": {
                "subsystem": subsystem,
                "name": subsystem_name,
                "task_processed": task[:50] + "..." if len(task) > 50 else task,
                "parameters": params,
            },
        }

    def get_status(self) -> dict[str, Any]:
        """Get current execution engine status."""
        return {
            "initialized": self.initialized,
            "total_executions": self.execution_count,
            "subsystems": 15,
            "subsystem_status": self.subsystem_status,
            "available_subsystems": list(self.SUBSYSTEMS.keys()),
        }


def demo_unified_execution():
    """Demonstrate unified execution engine."""
    print("\n" + "=" * 70)
    print("AMOS UNIFIED EXECUTION ENGINE - COMPONENT #55")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing execution engine...")
    engine = UnifiedExecutionEngine()
    init_result = engine.initialize()
    print(f"   Status: {init_result['status']}")
    print(f"   Subsystems: {init_result['subsystems']}")

    # Execute tasks
    test_tasks = [
        "Analyze market trends and generate report",
        "Scan environment for security threats",
        "Execute deployment workflow",
        "Coordinate multi-subsystem analysis",
    ]

    print("\n[2] Executing test tasks...")
    for i, task in enumerate(test_tasks, 1):
        print(f"\n   Task {i}: {task}")

        context = engine.execute(task)

        print(f"   → Subsystems: {', '.join(context.subsystems_involved)}")
        print(f"   → Duration: {context.metadata['duration_ms']:.1f}ms")
        print(f"   → Results: {len(context.results)} subsystem executions")

    # Final status
    print("\n[3] Final status...")
    status = engine.get_status()
    print(f"   → Total executions: {status['total_executions']}")
    print(f"   → All subsystems: {status['subsystems']}")

    print("\n" + "=" * 70)
    print("Unified Execution Engine Complete")
    print("=" * 70)
    print("\n55th Component: Coordinates 15 organism subsystems")
    print("=" * 70)


if __name__ == "__main__":
    demo_unified_execution()

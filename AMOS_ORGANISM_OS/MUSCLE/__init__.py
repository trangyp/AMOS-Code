"""
MUSCLE module — Alias for 06_MUSCLE
"""

import sys
from pathlib import Path

# Add 06_MUSCLE to path
muscle_path = Path(__file__).parent.parent / "06_MUSCLE"
if str(muscle_path) not in sys.path:
    sys.path.insert(0, str(muscle_path))

# Import and re-export
from executor import MuscleExecutor, ExecutionResult, ExecutionContext, ExecutionStatus
from code_runner import CodeRunner, CodeRunResult, Language
from workflow_engine import WorkflowEngine, Workflow, WorkflowStep, StepStatus

__all__ = [
    "MuscleExecutor",
    "ExecutionResult",
    "ExecutionContext",
    "ExecutionStatus",
    "CodeRunner",
    "CodeRunResult",
    "Language",
    "WorkflowEngine",
    "Workflow",
    "WorkflowStep",
    "StepStatus",
]

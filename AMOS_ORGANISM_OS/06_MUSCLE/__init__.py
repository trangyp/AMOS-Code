"""
06_MUSCLE — Run commands, write code, deploy and automate workflows.

The execution engine of AMOS. Takes plans from BRAIN and executes them.
"""

from .executor import MuscleExecutor, ExecutionResult, ExecutionContext
from .code_runner import CodeRunner
from .workflow_engine import WorkflowEngine

__all__ = [
    "MuscleExecutor",
    "ExecutionResult",
    "ExecutionContext",
    "CodeRunner",
    "WorkflowEngine",
]

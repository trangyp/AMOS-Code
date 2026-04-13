"""
06_MUSCLE — Run commands, write code, deploy and automate workflows.

The execution engine of AMOS. Takes plans from BRAIN and executes them.
"""

from .executor import MuscleExecutor, ExecutionResult, ExecutionContext
from .code_runner import CodeRunner
from .workflow_engine import WorkflowEngine
from .amos_worker_engine import (
    AmosWorkerEngine,
    WorkerResult,
    CodeWorker,
    FileWorker,
    get_worker_engine,
)
from .brain_muscle_bridge import (
    BrainMuscleBridge,
    CognitiveTask,
    CognitiveExecutionResult,
    get_brain_muscle_bridge,
)

__all__ = [
    # Base execution
    "MuscleExecutor",
    "ExecutionResult",
    "ExecutionContext",
    "CodeRunner",
    "WorkflowEngine",
    # Worker engine with cognitive runtime
    "AmosWorkerEngine",
    "WorkerResult",
    "CodeWorker",
    "FileWorker",
    "get_worker_engine",
    # Brain-Muscle bridge
    "BrainMuscleBridge",
    "CognitiveTask",
    "CognitiveExecutionResult",
    "get_brain_muscle_bridge",
]

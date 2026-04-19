"""MUSCLE module — Alias for 06_MUSCLE"""

import sys
from pathlib import Path

# Add 06_MUSCLE to path
muscle_path = Path(__file__).parent.parent / "06_MUSCLE"
if str(muscle_path) not in sys.path:
    sys.path.insert(0, str(muscle_path))

# Import and re-export base components
from code_runner import CodeRunner, CodeRunResult, Language
from executor import ExecutionContext, ExecutionResult, ExecutionStatus, MuscleExecutor

from workflow_engine import StepStatus, Workflow, WorkflowEngine, WorkflowStep

# Import cognitive integration components
try:
    from amos_worker_engine import (
        AmosWorkerEngine,
        CodeWorker,
        FileWorker,
        WorkerResult,
        get_worker_engine,
    )
    from brain_muscle_bridge import (
        BrainMuscleBridge,
        CognitiveExecutionResult,
        CognitiveTask,
        get_brain_muscle_bridge,
    )

    _COGNITIVE_AVAILABLE = True
except Exception:
    _COGNITIVE_AVAILABLE = False
    AmosWorkerEngine = None
    WorkerResult = None
    CodeWorker = None
    FileWorker = None
    get_worker_engine = None
    BrainMuscleBridge = None
    CognitiveTask = None
    CognitiveExecutionResult = None
    get_brain_muscle_bridge = None

__all__ = [
    # Base execution
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
    # Cognitive integration (if available)
    "AmosWorkerEngine",
    "WorkerResult",
    "CodeWorker",
    "FileWorker",
    "get_worker_engine",
    "BrainMuscleBridge",
    "CognitiveTask",
    "CognitiveExecutionResult",
    "get_brain_muscle_bridge",
]

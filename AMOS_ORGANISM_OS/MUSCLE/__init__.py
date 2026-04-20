"""MUSCLE module — Alias for 06_MUSCLE"""

import importlib.util
from pathlib import Path

# Load modules from 06_MUSCLE using importlib
_06_MUSCLE_PATH = Path(__file__).parent.parent / "06_MUSCLE"

# code_runner
_spec_cr = importlib.util.spec_from_file_location("_code_run", _06_MUSCLE_PATH / "code_runner.py")
_mod_cr = importlib.util.module_from_spec(_spec_cr)
_spec_cr.loader.exec_module(_mod_cr)
CodeRunner = _mod_cr.CodeRunner
CodeRunResult = _mod_cr.CodeRunResult
Language = _mod_cr.Language

# executor
_spec_ex = importlib.util.spec_from_file_location("_executor", _06_MUSCLE_PATH / "executor.py")
_mod_ex = importlib.util.module_from_spec(_spec_ex)
_spec_ex.loader.exec_module(_mod_ex)
MuscleExecutor = _mod_ex.MuscleExecutor
ExecutionResult = _mod_ex.ExecutionResult
ExecutionContext = _mod_ex.ExecutionContext
ExecutionStatus = _mod_ex.ExecutionStatus

# workflow_engine
_spec_we = importlib.util.spec_from_file_location("_wf_eng", _06_MUSCLE_PATH / "workflow_engine.py")
_mod_we = importlib.util.module_from_spec(_spec_we)
_spec_we.loader.exec_module(_mod_we)
WorkflowEngine = _mod_we.WorkflowEngine
Workflow = _mod_we.Workflow
WorkflowStep = _mod_we.WorkflowStep
StepStatus = _mod_we.StepStatus

# Import cognitive integration components
try:
    _spec_awe = importlib.util.spec_from_file_location(
        "_amos_we", _06_MUSCLE_PATH / "amos_worker_engine.py"
    )
    _mod_awe = importlib.util.module_from_spec(_spec_awe)
    _spec_awe.loader.exec_module(_mod_awe)
    AmosWorkerEngine = _mod_awe.AmosWorkerEngine
    CodeWorker = _mod_awe.CodeWorker
    FileWorker = _mod_awe.FileWorker
    WorkerResult = _mod_awe.WorkerResult
    get_worker_engine = _mod_awe.get_worker_engine

    _spec_bmb = importlib.util.spec_from_file_location(
        "_brain_mb", _06_MUSCLE_PATH / "brain_muscle_bridge.py"
    )
    _mod_bmb = importlib.util.module_from_spec(_spec_bmb)
    _spec_bmb.loader.exec_module(_mod_bmb)
    BrainMuscleBridge = _mod_bmb.BrainMuscleBridge
    CognitiveTask = _mod_bmb.CognitiveTask
    CognitiveExecutionResult = _mod_bmb.CognitiveExecutionResult
    get_brain_muscle_bridge = _mod_bmb.get_brain_muscle_bridge

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

"""MUSCLE executor stub — Re-exports from 06_MUSCLE"""

import importlib.util
from pathlib import Path

# Load from 06_MUSCLE using importlib
_muscle_path = Path(__file__).parent.parent / "06_MUSCLE" / "executor.py"
_spec = importlib.util.spec_from_file_location("_executor", _muscle_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MuscleExecutor = _mod.MuscleExecutor
ExecutionResult = _mod.ExecutionResult
ExecutionContext = _mod.ExecutionContext
ExecutionStatus = _mod.ExecutionStatus

__all__ = ["MuscleExecutor", "ExecutionResult", "ExecutionContext", "ExecutionStatus"]

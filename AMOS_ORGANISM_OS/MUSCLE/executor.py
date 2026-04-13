# Stub to re-export from 06_MUSCLE
import sys
from pathlib import Path

muscle_path = Path(__file__).parent.parent / "06_MUSCLE"
if str(muscle_path) not in sys.path:
    sys.path.insert(0, str(muscle_path))

from executor import (
    MuscleExecutor,
    ExecutionResult,
    ExecutionContext,
    ExecutionStatus,
)

__all__ = ["MuscleExecutor", "ExecutionResult", "ExecutionContext", "ExecutionStatus"]

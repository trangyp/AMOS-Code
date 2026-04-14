# Stub to re-export from 06_MUSCLE
import sys
from pathlib import Path

muscle_path = Path(__file__).parent.parent / "06_MUSCLE"
if str(muscle_path) not in sys.path:
    sys.path.insert(0, str(muscle_path))

from brain_muscle_bridge import (
    BrainMuscleBridge,
    CognitiveExecutionResult,
    CognitiveTask,
    get_brain_muscle_bridge,
)

__all__ = [
    "BrainMuscleBridge",
    "CognitiveTask",
    "CognitiveExecutionResult",
    "get_brain_muscle_bridge",
]

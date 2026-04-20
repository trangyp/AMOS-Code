"""MUSCLE brain_muscle_bridge stub — Re-exports from 06_MUSCLE"""

import importlib.util
from pathlib import Path

# Load from 06_MUSCLE using importlib
_muscle_path = Path(__file__).parent.parent / "06_MUSCLE" / "brain_muscle_bridge.py"
_spec = importlib.util.spec_from_file_location("_brain_muscle", _muscle_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BrainMuscleBridge = _mod.BrainMuscleBridge
CognitiveTask = _mod.CognitiveTask
CognitiveExecutionResult = _mod.CognitiveExecutionResult
get_brain_muscle_bridge = _mod.get_brain_muscle_bridge

__all__ = [
    "BrainMuscleBridge",
    "CognitiveTask",
    "CognitiveExecutionResult",
    "get_brain_muscle_bridge",
]

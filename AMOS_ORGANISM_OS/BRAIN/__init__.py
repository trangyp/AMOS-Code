"""BRAIN module — Alias for 01_BRAIN"""

import importlib.util
from pathlib import Path

# Load modules from 01_BRAIN using importlib
_01_BRAIN_PATH = Path(__file__).parent.parent / "01_BRAIN"

# brain_os
_spec_bo = importlib.util.spec_from_file_location("_brain_os", _01_BRAIN_PATH / "brain_os.py")
_mod_bo = importlib.util.module_from_spec(_spec_bo)
_spec_bo.loader.exec_module(_mod_bo)
BrainOS = _mod_bo.BrainOS
BrainState = _mod_bo.BrainState
Plan = _mod_bo.Plan
Thought = _mod_bo.Thought
ThoughtType = _mod_bo.ThoughtType

# memory_layer
_spec_ml = importlib.util.spec_from_file_location(
    "_memory_layer", _01_BRAIN_PATH / "memory_layer.py"
)
_mod_ml = importlib.util.module_from_spec(_spec_ml)
_spec_ml.loader.exec_module(_mod_ml)
Memory = _mod_ml.Memory
MemoryLayer = _mod_ml.MemoryLayer

# router
_spec_rt = importlib.util.spec_from_file_location("_router", _01_BRAIN_PATH / "router.py")
_mod_rt = importlib.util.module_from_spec(_spec_rt)
_spec_rt.loader.exec_module(_mod_rt)
SystemRouter = _mod_rt.SystemRouter
RoutingDecision = _mod_rt.RoutingDecision

__all__ = [
    "BrainOS",
    "BrainState",
    "Thought",
    "Plan",
    "ThoughtType",
    "SystemRouter",
    "RoutingDecision",
    "MemoryLayer",
    "Memory",
]

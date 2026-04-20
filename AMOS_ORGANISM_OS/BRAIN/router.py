"""BRAIN router stub — Re-exports from 01_BRAIN"""

import importlib.util
from pathlib import Path

# Load from 01_BRAIN using importlib
_brain_path = Path(__file__).parent.parent / "01_BRAIN" / "router.py"
_spec = importlib.util.spec_from_file_location("_router", _brain_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SystemRouter = _mod.SystemRouter
RoutingDecision = _mod.RoutingDecision

__all__ = ["SystemRouter", "RoutingDecision"]

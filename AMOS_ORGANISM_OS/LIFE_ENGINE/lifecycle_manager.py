"""LIFE_ENGINE lifecycle_manager stub — Re-exports from 11_LIFE_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 11_LIFE_ENGINE using importlib
_life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE" / "lifecycle_manager.py"
_spec = importlib.util.spec_from_file_location("_life_lcm", _life_path)
_life_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_life_mod)

LifecycleEvent = _life_mod.LifecycleEvent
LifecycleManager = _life_mod.LifecycleManager
LifecycleStage = _life_mod.LifecycleStage

__all__ = ["LifecycleManager", "LifecycleStage", "LifecycleEvent"]

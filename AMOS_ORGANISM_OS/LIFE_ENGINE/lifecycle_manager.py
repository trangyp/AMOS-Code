"""LIFE_ENGINE lifecycle_manager stub — Re-exports from 11_LIFE_ENGINE"""

import sys
from pathlib import Path

life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE"
if str(life_path) not in sys.path:
    sys.path.insert(0, str(life_path))

from lifecycle_manager import LifecycleEvent, LifecycleManager, LifecycleStage

__all__ = ["LifecycleManager", "LifecycleStage", "LifecycleEvent"]

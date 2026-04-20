"""LIFE_ENGINE health_monitor stub — Re-exports from 11_LIFE_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 11_LIFE_ENGINE using importlib
_life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE" / "health_monitor.py"
_spec = importlib.util.spec_from_file_location("_life_hm", _life_path)
_life_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_life_mod)

HealthMetric = _life_mod.HealthMetric
HealthMonitor = _life_mod.HealthMonitor
HealthStatus = _life_mod.HealthStatus

__all__ = ["HealthMonitor", "HealthMetric", "HealthStatus"]

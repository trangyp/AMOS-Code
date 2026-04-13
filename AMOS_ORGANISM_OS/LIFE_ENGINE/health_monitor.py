"""LIFE_ENGINE health_monitor stub — Re-exports from 11_LIFE_ENGINE"""
import sys
from pathlib import Path

life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE"
if str(life_path) not in sys.path:
    sys.path.insert(0, str(life_path))

from health_monitor import HealthMonitor, HealthMetric, HealthStatus

__all__ = ["HealthMonitor", "HealthMetric", "HealthStatus"]

"""LIFE_ENGINE module — Alias for 11_LIFE_ENGINE"""

import sys
from pathlib import Path

life_path = Path(__file__).parent.parent / "11_LIFE_ENGINE"
if str(life_path) not in sys.path:
    sys.path.insert(0, str(life_path))

from adaptation_system import AdaptationStrategy, AdaptationSystem, EnvironmentFeedback
from growth_engine import GrowthEngine, GrowthPlan, GrowthStage
from health_monitor import HealthMetric, HealthMonitor, HealthStatus
from lifecycle_manager import LifecycleEvent, LifecycleManager, LifecycleStage

__all__ = [
    "GrowthEngine",
    "GrowthPlan",
    "GrowthStage",
    "AdaptationSystem",
    "AdaptationStrategy",
    "EnvironmentFeedback",
    "HealthMonitor",
    "HealthMetric",
    "HealthStatus",
    "LifecycleManager",
    "LifecycleStage",
    "LifecycleEvent",
]

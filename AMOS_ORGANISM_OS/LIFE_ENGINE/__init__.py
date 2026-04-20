"""LIFE_ENGINE module — Alias for 11_LIFE_ENGINE"""

from AMOS_ORGANISM_OS.LIFE_ENGINE.adaptation_system import (
    AdaptationStrategy,
    AdaptationSystem,
    EnvironmentFeedback,
)
from AMOS_ORGANISM_OS.LIFE_ENGINE.growth_engine import GrowthEngine, GrowthPlan, GrowthStage
from AMOS_ORGANISM_OS.LIFE_ENGINE.health_monitor import HealthMetric, HealthMonitor, HealthStatus
from AMOS_ORGANISM_OS.LIFE_ENGINE.lifecycle_manager import (
    LifecycleEvent,
    LifecycleManager,
    LifecycleStage,
)

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

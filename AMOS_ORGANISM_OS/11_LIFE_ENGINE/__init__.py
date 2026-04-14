"""11_LIFE_ENGINE — Growth, Adaptation & Evolution
===============================================

The life management layer of AMOS.
Handles self-modification, health monitoring, resource optimization,
and evolutionary adaptation.

Role: Growth, adaptation, evolution, lifecycle management
Kernel refs: LIFE_KERNEL, GROWTH_KERNEL, EVOLUTION_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .adaptation_system import AdaptationStrategy, AdaptationSystem, EnvironmentFeedback
from .growth_engine import GrowthEngine, GrowthPlan, GrowthStage
from .health_monitor import HealthMetric, HealthMonitor, HealthStatus
from .lifecycle_manager import LifecycleEvent, LifecycleManager, LifecycleStage

__all__ = [
    # Growth
    "GrowthEngine",
    "GrowthPlan",
    "GrowthStage",
    # Adaptation
    "AdaptationSystem",
    "AdaptationStrategy",
    "EnvironmentFeedback",
    # Health
    "HealthMonitor",
    "HealthMetric",
    "HealthStatus",
    # Lifecycle
    "LifecycleManager",
    "LifecycleStage",
    "LifecycleEvent",
]

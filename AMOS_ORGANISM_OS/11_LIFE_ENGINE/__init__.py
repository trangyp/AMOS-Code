"""
11_LIFE_ENGINE — Growth, Adaptation & Evolution
===============================================

The life management layer of AMOS.
Handles self-modification, health monitoring, resource optimization,
and evolutionary adaptation.

Role: Growth, adaptation, evolution, lifecycle management
Kernel refs: LIFE_KERNEL, GROWTH_KERNEL, EVOLUTION_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .growth_engine import GrowthEngine, GrowthPlan, GrowthStage
from .adaptation_system import AdaptationSystem, AdaptationStrategy, EnvironmentFeedback
from .health_monitor import HealthMonitor, HealthMetric, HealthStatus
from .lifecycle_manager import LifecycleManager, LifecycleStage, LifecycleEvent

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

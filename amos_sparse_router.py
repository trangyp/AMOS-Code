from typing import Any, Dict, Optional, Set

"""
AMOS Sparse Router
Implements selective module activation for FastLoop.

From: RuntimeCost ∝ Σᵢ ModuleCostᵢ (all modules)
To:   RuntimeCost ∝ Σᵢ∈ActiveSet ModuleCostᵢ (active only)
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

from amos_fastloop_classifier import ClassificationResult, InterruptClass


class ModuleType(Enum):
    """AMOS system modules."""

    # Core cognition (expensive)
    BRAIN = auto()
    SIMULATOR = auto()
    VERIFIER = auto()

    # Fast path modules
    MEMORY = auto()
    RETRIEVAL = auto()
    STATE = auto()
    EXECUTOR = auto()

    # Interface
    INTERFACE = auto()
    PASSTHROUGH = auto()


@dataclass
class ActiveModuleSet:
    """Set of modules activated for a request."""

    modules: Set[ModuleType]
    latency_budget_ms: float
    verification_tier: str
    search_limits: Dict[str, int]

    def __post_init__(self):
        """Validate module set."""
        if not self.modules:
            raise ValueError("ActiveModuleSet cannot be empty")


@dataclass
class RouteResult:
    """Result of routing decision."""

    module_set: ActiveModuleSet
    routing_latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class SparseRouter:
    """
    Routes requests to minimal active module set.

    Routing Table:
    - QUERY:    [memory, retrieval] - Information lookup only
    - ACTION:   [state, executor] - State mutation only
    - REASONING: [brain, simulator, verifier] - Full cognition
    - ESCALATION: [interface] - Redirect only
    - ECHO:     [passthrough] - No processing
    """

    # Core routing table
    ROUTING_TABLE: Dict[InterruptClass, ActiveModuleSet] = {
        InterruptClass.QUERY: ActiveModuleSet(
            modules={ModuleType.MEMORY, ModuleType.RETRIEVAL},
            latency_budget_ms=10.0,
            verification_tier="none",
            search_limits={"branches": 1, "horizon": 1, "depth": 0},
        ),
        InterruptClass.ACTION: ActiveModuleSet(
            modules={ModuleType.STATE, ModuleType.EXECUTOR},
            latency_budget_ms=50.0,
            verification_tier="syntax",
            search_limits={"branches": 2, "horizon": 1, "depth": 1},
        ),
        InterruptClass.REASONING: ActiveModuleSet(
            modules={ModuleType.BRAIN, ModuleType.SIMULATOR, ModuleType.VERIFIER},
            latency_budget_ms=200.0,
            verification_tier="local",
            search_limits={"branches": 3, "horizon": 2, "depth": 2},
        ),
        InterruptClass.ESCALATION: ActiveModuleSet(
            modules={ModuleType.INTERFACE},
            latency_budget_ms=5.0,
            verification_tier="none",
            search_limits={"branches": 1, "horizon": 1, "depth": 0},
        ),
        InterruptClass.ECHO: ActiveModuleSet(
            modules={ModuleType.PASSTHROUGH},
            latency_budget_ms=1.0,
            verification_tier="none",
            search_limits={"branches": 1, "horizon": 1, "depth": 0},
        ),
        InterruptClass.UNKNOWN: ActiveModuleSet(
            modules={ModuleType.BRAIN, ModuleType.SIMULATOR, ModuleType.VERIFIER},
            latency_budget_ms=200.0,
            verification_tier="full",
            search_limits={"branches": 3, "horizon": 2, "depth": 2},
        ),
    }

    def __init__(self):
        """Initialize router."""
        self._route_count = 0
        self._active_module_stats: Dict[ModuleType, int] = {m: 0 for m in ModuleType}

    def route(self, classification: ClassificationResult) -> RouteResult:
        """
        Route classification to active module set.

        Target: < 1ms routing latency
        """
        start_time = time.perf_counter()
        self._route_count += 1

        # Get module set from routing table
        class_type = classification.class_type
        module_set = self.ROUTING_TABLE.get(class_type, self.ROUTING_TABLE[InterruptClass.UNKNOWN])

        # Update stats
        for module in module_set.modules:
            self._active_module_stats[module] += 1

        latency_ms = (time.perf_counter() - start_time) * 1000

        return RouteResult(
            module_set=module_set,
            routing_latency_ms=latency_ms,
            metadata={
                "classification": class_type.name,
                "confidence": classification.confidence,
                "module_count": len(module_set.modules),
            },
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_module_activations = sum(self._active_module_stats.values())
        return {
            "total_routes": self._route_count,
            "avg_modules_per_route": total_module_activations / max(1, self._route_count),
            "module_activation_counts": {m.name: c for m, c in self._active_module_stats.items()},
        }

    def get_active_modules(self, classification: ClassificationResult) -> set[ModuleType]:
        """Get just the module set for a classification."""
        return self.ROUTING_TABLE.get(
            classification.class_type, self.ROUTING_TABLE[InterruptClass.UNKNOWN]
        ).modules


# Global singleton
_router: Optional[SparseRouter] = None


def get_router() -> SparseRouter:
    """Get global router instance (singleton)."""
    global _router
    if _router is None:
        _router = SparseRouter()
    return _router


async def route_classification(classification: ClassificationResult) -> RouteResult:
    """Async wrapper for routing."""
    router = get_router()
    return router.route(classification)


# Module activation helpers
def is_module_active(module_set: ActiveModuleSet, module: ModuleType) -> bool:
    """Check if a module is in the active set."""
    return module in module_set.modules


def get_latency_budget(classification: ClassificationResult) -> float:
    """Get latency budget for a classification."""
    router = get_router()
    result = router.route(classification)
    return result.module_set.latency_budget_ms


def get_search_limits(classification: ClassificationResult) -> Dict[str, int]:
    """Get search limits for a classification."""
    router = get_router()
    result = router.route(classification)
    return result.module_set.search_limits


# Test/example
if __name__ == "__main__":
    import asyncio

    from amos_fastloop_classifier import InterruptClass, classify_request

    async def test():
        print("\nAMOS Sparse Router Test")
        print("=" * 60)

        test_cases = [
            "What is the status?",
            "Deploy now",
            "Explain the architecture",
            "Help with critical bug",
            "Hello",
        ]

        for request in test_cases:
            classification = await classify_request(request)
            route = await route_classification(classification)

            modules = [m.name for m in route.module_set.modules]
            budget = route.module_set.latency_budget_ms

            print(f"\n'{request[:25]}...'")
            print(f"  Class: {classification.class_type.name} ({classification.confidence:.0%})")
            print(f"  Modules: {', '.join(modules)}")
            print(f"  Budget: {budget}ms")
            print(
                f"  Limits: B={route.module_set.search_limits['branches']}, "
                f"H={route.module_set.search_limits['horizon']}"
            )

        print("\n" + "=" * 60)
        stats = get_router().get_stats()
        print(f"Routes: {stats['total_routes']}")
        print(f"Avg modules/route: {stats['avg_modules_per_route']:.1f}")

    asyncio.run(test())

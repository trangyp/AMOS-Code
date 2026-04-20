"""AMOS Engine Integration - Unified API."""

from dataclasses import dataclass
from typing import Any

from amos_field_dynamics import create_scalar_field
from amos_self_evolution_test_suite import get_self_evolution_test_suite
from amos_temporal_engine import get_temporal_engine


@dataclass
class EngineResult:
    success: bool
    data: dict[str, Any]


class AMOSEngineIntegration:
    """Unified API for all AMOS engines."""

    def __init__(self):
        self.temporal = get_temporal_engine()
        self.safety = get_self_evolution_test_suite()
        self.field = create_scalar_field()

    async def get_system_status(self) -> dict[str, Any]:
        return {
            "temporal": self.temporal.get_metrics(),
            "field": self.field.get_metrics(),
            "safety": self.safety.get_safety_metrics(),
        }


_engine_integration = None


def get_engine_integration() -> AMOSEngineIntegration:
    global _engine_integration
    if _engine_integration is None:
        _engine_integration = AMOSEngineIntegration()
    return _engine_integration

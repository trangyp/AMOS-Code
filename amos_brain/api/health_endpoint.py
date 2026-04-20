"""AMOS Brain Health Check API Endpoint.

Provides health check functionality for the AMOS Brain API.
"""

from dataclasses import dataclass
from typing import Any

from amos_brain import get_super_brain


@dataclass
class HealthStatus:
    """Health check response data."""

    status: str
    version: str
    health_score: float
    subsystems: dict[str, Any]


class HealthCheckEndpoint:
    """AMOS Brain health check API endpoint."""

    VERSION = "14.0.0"

    def check(self) -> HealthStatus:
        """Perform health check on all subsystems."""
        brain = get_super_brain()
        state = brain.get_state()

        return HealthStatus(
            status="healthy" if state.health_score > 0.5 else "degraded",
            version=self.VERSION,
            health_score=state.health_score,
            subsystems=state.subsystem_states if hasattr(state, "subsystem_states") else {},
        )

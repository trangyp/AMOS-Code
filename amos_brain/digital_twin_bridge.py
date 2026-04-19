"""Architectural Digital Twin Bridge (Layer 17).

Integrates digital twin simulation with AMOS Brain cognition.

Provides API for:
- Architecture state capture
- What-if scenario simulation
- Change impact prediction
- Invariant violation forecasting
"""


from pathlib import Path
from typing import Any, Dict, List, Optional

# Import digital twin
try:
    from repo_doctor.architectural_digital_twin import (
        ArchitecturalChange,
        ArchitecturalDigitalTwin,
        ChangeType,
    )

    TWIN_AVAILABLE = True
except ImportError:
    TWIN_AVAILABLE = False


class DigitalTwinBridge:
    """Bridge between digital twin and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._twin: Optional[ArchitecturalDigitalTwin] = None

    @property
    def twin(self) -> Optional[ArchitecturalDigitalTwin]:
        """Lazy initialization of digital twin."""
        if self._twin is None and TWIN_AVAILABLE:
            self._twin = ArchitecturalDigitalTwin()
        return self._twin

    def capture_architecture_state(
        self,
        components: List[dict[str, Any]],
        dependencies: List[dict[str, Any]],
        interfaces: List[dict[str, Any]],
        invariant_status: Dict[str, bool],
    ) -> Dict[str, Any]:
        """Capture current architecture state into digital twin."""
        if not TWIN_AVAILABLE or self.twin is None:
            return {"error": "digital_twin not available"}

        state = self.twin.capture_state(components, dependencies, interfaces, invariant_status)
        return {
            "state_id": state.state_id,
            "timestamp": state.timestamp,
            "complexity_score": state.complexity_score,
            "coupling_score": state.coupling_score,
            "cohesion_score": state.cohesion_score,
            "invariant_count": len(state.invariant_status),
        }

    def simulate_architectural_change(
        self, change_type: str, target: str, description: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate impact of an architectural change."""
        if not TWIN_AVAILABLE or self.twin is None:
            return {"error": "digital_twin not available"}

        try:
            ct = ChangeType(change_type)
        except ValueError:
            return {"error": f"Invalid change type: {change_type}"}

        change = ArchitecturalChange(
            change_id=f"change_{len(self.twin.simulations)}",
            change_type=ct,
            description=description,
            target_component=target,
            change_details=details,
            expected_impact="medium",
        )

        result = self.twin.simulate_change(change)
        return result.to_dict()

    def forecast_invariant_violations(self, steps: int = 5) -> Dict[str, Any]:
        """Forecast future invariant violations."""
        if not TWIN_AVAILABLE or self.twin is None:
            return {"error": "digital_twin not available"}

        forecast = self.twin.forecast_invariants(steps)
        return {
            "forecast_id": forecast.forecast_id,
            "horizon_steps": forecast.horizon_steps,
            "high_risk_invariants": forecast.high_risk_invariants,
            "medium_risk_invariants": forecast.medium_risk_invariants,
            "high_risk_count": len(forecast.high_risk_invariants),
            "medium_risk_count": len(forecast.medium_risk_invariants),
        }

    def evaluate_what_if_scenario(self, changes: List[dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate what-if scenario with multiple changes."""
        if not TWIN_AVAILABLE or self.twin is None:
            return {"error": "digital_twin not available"}

        arch_changes = []
        for i, ch in enumerate(changes):
            try:
                ct = ChangeType(ch["change_type"])
            except (ValueError, KeyError):
                continue

            arch_changes.append(
                ArchitecturalChange(
                    change_id=f"whatif_{i}",
                    change_type=ct,
                    description=ch.get("description", ""),
                    target_component=ch.get("target", ""),
                    change_details=ch.get("details", {}),
                    expected_impact=ch.get("impact", "medium"),
                )
            )

        return self.twin.get_what_if_recommendations(arch_changes)

    def get_twin_status(self) -> Dict[str, Any]:
        """Get digital twin status."""
        if not TWIN_AVAILABLE or self.twin is None:
            return {"error": "digital_twin not available"}

        return self.twin.get_twin_status()


def get_digital_twin_bridge(repo_path: str | Path) -> DigitalTwinBridge:
    """Factory function to get digital twin bridge."""
    return DigitalTwinBridge(repo_path)

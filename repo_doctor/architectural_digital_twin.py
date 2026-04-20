"""
Architectural Digital Twin & Simulation Engine (Layer 17).

Provides simulation and "what-if" scenario modeling for architecture.

Capabilities:
- Digital twin of system architecture state
- What-if scenario simulation for changes
- Predictive architectural evolution modeling
- Architecture change impact prediction
- Invariant violation forecasting

This is the predictive layer that enables "architectural foresight".
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class SimulationType(Enum):
    """Types of architecture simulations."""

    WHAT_IF_CHANGE = "what_if_change"  # Simulate specific change
    STRESS_TEST = "stress_test"  # Simulate failure scenarios
    EVOLUTION_PATH = "evolution_path"  # Simulate long-term evolution
    INVARIANT_FORECAST = "invariant_forecast"  # Predict invariant violations


class ChangeType(Enum):
    """Types of architectural changes."""

    ADD_COMPONENT = "add_component"
    REMOVE_COMPONENT = "remove_component"
    MODIFY_INTERFACE = "modify_interface"
    CHANGE_DEPENDENCY = "change_dependency"
    UPDATE_CONSTRAINT = "update_constraint"


@dataclass
class ArchitectureState:
    """Digital twin representation of architecture state."""

    state_id: str
    timestamp: str

    # Component graph
    components: list[dict[str, Any]]
    dependencies: list[dict[str, Any]]
    interfaces: list[dict[str, Any]]

    # Invariant states
    invariant_status: Dict[str, bool]
    invariant_scores: Dict[str, float]

    # Health metrics
    complexity_score: float
    coupling_score: float
    cohesion_score: float


@dataclass
class ArchitecturalChange:
    """A proposed architectural change."""

    change_id: str
    change_type: ChangeType
    description: str
    target_component: str
    change_details: Dict[str, Any]
    expected_impact: str  # "low", "medium", "high", "critical"


@dataclass
class SimulationScenario:
    """A simulation scenario."""

    scenario_id: str
    simulation_type: SimulationType
    base_state: ArchitectureState
    changes: list[ArchitecturalChange]
    duration_steps: int = 1


@dataclass
class SimulationResult:
    """Result of architecture simulation."""

    result_id: str
    scenario_id: str
    timestamp: str

    # Predicted outcomes
    predicted_state: ArchitectureState
    invariant_changes: dict[str, tuple[bool, bool]]  # (before, after)
    health_delta: Dict[str, float]  # Change in each health metric

    # Risk assessment
    risk_level: str  # "low", "medium", "high", "critical"
    breaking_changes: list[str]
    cascade_effects: list[str]

    # Recommendations
    recommendations: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "scenario_id": self.scenario_id,
            "risk_level": self.risk_level,
            "health_delta": self.health_delta,
            "breaking_changes": len(self.breaking_changes),
            "cascade_effects": len(self.cascade_effects),
            "recommendations": self.recommendations,
        }


@dataclass
class InvariantForecast:
    """Forecast of future invariant violations."""

    forecast_id: str
    timestamp: str
    horizon_steps: int

    # Predictions per invariant
    predictions: dict[str, list[tuple[int, float, str]]]  # (step, probability, reason)

    # Overall risk
    high_risk_invariants: list[str]
    medium_risk_invariants: list[str]


class ArchitecturalDigitalTwin:
    """
    Digital twin for system architecture with simulation capabilities.

    Provides:
    - Real-time architecture state mirroring
    - What-if scenario simulation
    - Predictive invariant violation forecasting
    - Change impact prediction
    """

    def __init__(self):
        self.current_state: ArchitectureState | None = None
        self.state_history: list[ArchitectureState] = []
        self.simulations: list[SimulationResult] = []
        self.forecasts: list[InvariantForecast] = []

        # Simulation parameters
        self.cascade_threshold = 0.7  # Probability threshold for cascade effects
        self.risk_threshold_high = 0.8
        self.risk_threshold_medium = 0.5

    def capture_state(
        self,
        components: list[dict],
        dependencies: list[dict],
        interfaces: list[dict],
        invariant_status: Dict[str, bool],
    ) -> ArchitectureState:
        """Capture current architecture state into digital twin."""
        # Calculate health metrics
        complexity = self._calculate_complexity(components, dependencies)
        coupling = self._calculate_coupling(dependencies)
        cohesion = self._calculate_cohesion(components)

        # Calculate invariant scores
        scores = {inv: (1.0 if valid else 0.0) for inv, valid in invariant_status.items()}

        state = ArchitectureState(
            state_id=f"state_{len(self.state_history)}",
            timestamp="2024-01-01T00:00:00Z",
            components=components,
            dependencies=dependencies,
            interfaces=interfaces,
            invariant_status=invariant_status,
            invariant_scores=scores,
            complexity_score=complexity,
            coupling_score=coupling,
            cohesion_score=cohesion,
        )

        self.current_state = state
        self.state_history.append(state)
        return state

    def _calculate_complexity(self, components: list[dict], dependencies: list[dict]) -> float:
        """Calculate system complexity score."""
        if not components:
            return 0.0
        # Complexity increases with component count and dependencies
        comp_factor = min(len(components) / 50, 1.0)  # Normalize to 50 components
        dep_factor = min(len(dependencies) / (len(components) * 2), 1.0) if components else 0
        return (comp_factor + dep_factor) / 2

    def _calculate_coupling(self, dependencies: list[dict]) -> float:
        """Calculate coupling score (lower is better)."""
        if not dependencies:
            return 0.0
        # Coupling increases with dependency count
        return min(len(dependencies) / 100, 1.0)

    def _calculate_cohesion(self, components: list[dict]) -> float:
        """Calculate cohesion score (higher is better)."""
        # This is a simplified calculation
        # Real implementation would analyze component responsibilities
        return 0.7  # Placeholder

    def simulate_change(
        self, change: ArchitecturalChange, base_state: ArchitectureState | None = None
    ) -> SimulationResult:
        """
        Simulate the impact of an architectural change.

        Args:
            change: The proposed architectural change
            base_state: State to simulate from (defaults to current)

        Returns:
            Simulation result with predicted outcomes

        """
        base = base_state or self.current_state
        if not base:
            raise ValueError("No base state available for simulation")

        # Clone state for simulation
        predicted_invariants = dict(base.invariant_status)
        predicted_scores = dict(base.invariant_scores)

        # Apply change effects based on type
        breaking_changes = []
        cascade_effects = []
        recommendations = []

        if change.change_type == ChangeType.REMOVE_COMPONENT:
            # Check for dependencies on removed component
            dependent_comps = [
                d for d in base.dependencies if d.get("target") == change.target_component
            ]
            if dependent_comps:
                breaking_changes.append(
                    f"Component {change.target_component} has {len(dependent_comps)} dependents"
                )
                predicted_invariants["I_protocol_lifecycle"] = False
                predicted_scores["I_protocol_lifecycle"] = 0.3

        elif change.change_type == ChangeType.MODIFY_INTERFACE:
            # Interface changes risk protocol violations
            breaking_changes.append("Interface modification may violate I_protocol_lifecycle")
            predicted_invariants["I_protocol_lifecycle"] = False
            predicted_scores["I_protocol_lifecycle"] = 0.5
            recommendations.append("Consider versioning the interface change")

        elif change.change_type == ChangeType.CHANGE_DEPENDENCY:
            # Dependency changes can affect temporal ordering
            cascade_effects.append("May affect I_partial_order")
            predicted_scores["I_partial_order"] = max(
                0, predicted_scores.get("I_partial_order", 1.0) - 0.2
            )

        # Calculate health delta
        complexity_delta = 0.0
        coupling_delta = 0.0

        if change.change_type == ChangeType.ADD_COMPONENT:
            complexity_delta = 0.02
            coupling_delta = 0.01
        elif change.change_type == ChangeType.REMOVE_COMPONENT:
            complexity_delta = -0.01
            coupling_delta = -0.02

        # Determine risk level
        if len(breaking_changes) > 0:
            risk_level = "critical" if len(breaking_changes) > 2 else "high"
        elif len(cascade_effects) > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Create predicted state
        predicted_state = ArchitectureState(
            state_id=f"predicted_{len(self.simulations)}",
            timestamp="2024-01-01T00:00:00Z",
            components=base.components,  # Simplified
            dependencies=base.dependencies,
            interfaces=base.interfaces,
            invariant_status=predicted_invariants,
            invariant_scores=predicted_scores,
            complexity_score=max(0, min(1, base.complexity_score + complexity_delta)),
            coupling_score=max(0, min(1, base.coupling_score + coupling_delta)),
            cohesion_score=base.cohesion_score,
        )

        # Track invariant changes
        invariant_changes = {}
        for inv in base.invariant_status:
            before = base.invariant_status[inv]
            after = predicted_invariants.get(inv, before)
            if before != after:
                invariant_changes[inv] = (before, after)

        result = SimulationResult(
            result_id=f"sim_{len(self.simulations)}",
            scenario_id=change.change_id,
            timestamp="2024-01-01T00:00:00Z",
            predicted_state=predicted_state,
            invariant_changes=invariant_changes,
            health_delta={
                "complexity": complexity_delta,
                "coupling": coupling_delta,
                "cohesion": 0.0,
            },
            risk_level=risk_level,
            breaking_changes=breaking_changes,
            cascade_effects=cascade_effects,
            recommendations=recommendations,
        )

        self.simulations.append(result)
        return result

    def forecast_invariants(self, steps: int = 5) -> InvariantForecast:
        """
        Forecast future invariant violations based on trend analysis.

        Args:
            steps: Number of future steps to forecast

        Returns:
            Forecast with violation predictions per invariant

        """
        if not self.state_history:
            raise ValueError("No state history for forecasting")

        predictions: dict[str, list[tuple[int, float, str]]] = {}
        high_risk = []
        medium_risk = []

        # Analyze trends for each invariant
        for invariant in self.state_history[0].invariant_scores:
            scores = [
                s.invariant_scores.get(invariant, 1.0)
                for s in self.state_history[-5:]  # Last 5 states
            ]

            # Simple trend extrapolation
            if len(scores) >= 2:
                trend = (scores[-1] - scores[0]) / len(scores)
            else:
                trend = 0

            inv_predictions = []
            current_score = scores[-1] if scores else 1.0

            for step in range(1, steps + 1):
                predicted_score = max(0, min(1, current_score + (trend * step)))
                probability = 1 - predicted_score

                if probability > 0.5:
                    reason = f"Degrading trend: {trend:.2f} per step"
                    inv_predictions.append((step, probability, reason))

            predictions[invariant] = inv_predictions

            # Classify risk
            max_prob = max((p[1] for p in inv_predictions), default=0)
            if max_prob > self.risk_threshold_high:
                high_risk.append(invariant)
            elif max_prob > self.risk_threshold_medium:
                medium_risk.append(invariant)

        forecast = InvariantForecast(
            forecast_id=f"forecast_{len(self.forecasts)}",
            timestamp="2024-01-01T00:00:00Z",
            horizon_steps=steps,
            predictions=predictions,
            high_risk_invariants=high_risk,
            medium_risk_invariants=medium_risk,
        )

        self.forecasts.append(forecast)
        return forecast

    def simulate_evolution_path(self, changes: list[ArchitecturalChange]) -> list[SimulationResult]:
        """
        Simulate a sequence of architectural changes.

        Args:
            changes: List of changes to apply sequentially

        Returns:
            List of simulation results for each step

        """
        results = []
        current = self.current_state

        for change in changes:
            result = self.simulate_change(change, current)
            results.append(result)
            # Update current state for next iteration
            current = result.predicted_state

        return results

    def get_what_if_recommendations(
        self, proposed_changes: list[ArchitecturalChange]
    ) -> Dict[str, Any]:
        """
        Get recommendations for proposed changes.

        Args:
            proposed_changes: List of proposed architectural changes

        Returns:
            Recommendations with risk assessment

        """
        results = []
        total_risk = 0

        for change in proposed_changes:
            result = self.simulate_change(change)
            results.append(result.to_dict())

            # Accumulate risk
            risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            total_risk += risk_scores.get(result.risk_level, 0)

        avg_risk = total_risk / len(proposed_changes) if proposed_changes else 0

        if avg_risk >= 3:
            overall = "critical"
            advice = "Do not proceed without architectural review"
        elif avg_risk >= 2:
            overall = "high"
            advice = "Proceed with caution and monitoring"
        elif avg_risk >= 1.5:
            overall = "medium"
            advice = "Acceptable with standard monitoring"
        else:
            overall = "low"
            advice = "Safe to proceed"

        return {
            "overall_risk": overall,
            "average_risk_score": avg_risk,
            "recommendation": advice,
            "change_count": len(proposed_changes),
            "simulations": results,
        }

    def get_twin_status(self) -> Dict[str, Any]:
        """Get current digital twin status."""
        return {
            "has_current_state": self.current_state is not None,
            "state_history_count": len(self.state_history),
            "simulation_count": len(self.simulations),
            "forecast_count": len(self.forecasts),
            "last_capture": self.state_history[-1].timestamp if self.state_history else None,
        }

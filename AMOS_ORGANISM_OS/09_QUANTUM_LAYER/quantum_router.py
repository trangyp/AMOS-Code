"""Quantum Router — Intelligent Decision Routing

Routes decisions through appropriate optimization pipelines,
combining scenario evaluation, Monte Carlo simulation, and
multi-criteria analysis.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RouteType(Enum):
    """Types of decision routes."""

    SCENARIO_BASED = "scenario_based"
    SIMULATION_BASED = "simulation_based"
    OPTIMIZER_BASED = "optimizer_based"
    HYBRID = "hybrid"  # Uses all methods


@dataclass
class RouteDecision:
    """A routed decision with full analysis."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    decision_type: str = ""
    route_type: RouteType = RouteType.HYBRID
    input_data: Dict[str, Any] = field(default_factory=dict)
    scenarios: List[dict[str, Any]] = field(default_factory=list)
    simulation_result: Dict[str, Any] = None
    optimizer_result: Dict[str, Any] = None
    recommendation: str = ""
    confidence: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "route_type": self.route_type.value,
        }


class QuantumRouter:
    """Routes decisions through the quantum decision layer.

    Integrates scenario engine, Monte Carlo simulator, and
    decision optimizer to provide comprehensive decision analysis.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir
        self.routes: Dict[str, RouteDecision] = {}

        # Import engines lazily to avoid circular dependencies
        self._scenario_engine = None
        self._monte_carlo = None
        self._optimizer = None

    @property
    def scenario_engine(self):
        """Lazy-load scenario engine."""
        if self._scenario_engine is None:
            from .scenario_engine import get_scenario_engine

            self._scenario_engine = get_scenario_engine(self.data_dir)
        return self._scenario_engine

    @property
    def monte_carlo(self):
        """Lazy-load Monte Carlo simulator."""
        if self._monte_carlo is None:
            from .monte_carlo import get_monte_carlo_simulator

            self._monte_carlo = get_monte_carlo_simulator(self.data_dir)
        return self._monte_carlo

    @property
    def optimizer(self):
        """Lazy-load decision optimizer."""
        if self._optimizer is None:
            from .decision_optimizer import get_decision_optimizer

            self._optimizer = get_decision_optimizer(self.data_dir)
        return self._optimizer

    def route_decision(
        self,
        decision_type: str,
        options: List[dict[str, Any]],
        route_type: RouteType = RouteType.HYBRID,
        criteria: str = "balanced",
    ) -> RouteDecision:
        """Route a decision through the quantum layer.

        Args:
            decision_type: Type/category of decision
            options: List of decision options
            route_type: Which routing method to use
            criteria: Optimization criteria

        Returns:
            RouteDecision with full analysis
        """
        route = RouteDecision(
            decision_type=decision_type,
            route_type=route_type,
            input_data={"options_count": len(options), "criteria": criteria},
        )

        if route_type in (RouteType.SCENARIO_BASED, RouteType.HYBRID):
            self._run_scenarios(route, options, criteria)

        if route_type in (RouteType.SIMULATION_BASED, RouteType.HYBRID):
            self._run_simulation(route, options)

        if route_type in (RouteType.OPTIMIZER_BASED, RouteType.HYBRID):
            self._run_optimizer(route, options, criteria)

        # Combine results for final recommendation
        self._synthesize_recommendation(route)

        self.routes[route.id] = route
        return route

    def _run_scenarios(
        self,
        route: RouteDecision,
        options: List[dict[str, Any]],
        criteria: str,
    ):
        """Run scenario evaluation for options."""
        scenario_ids = []
        for option in options:
            scenario = self.scenario_engine.create_scenario(
                name=option.get("name", "unnamed"),
                description=option.get("description", ""),
                parameters=option,
            )
            scenario_ids.append(scenario.id)

        # Evaluate all scenarios
        self.scenario_engine.evaluate_all(evaluator_type=criteria)

        # Get comparison
        comparisons = self.scenario_engine.compare_scenarios(scenario_ids)
        route.scenarios = comparisons

    def _run_simulation(
        self,
        route: RouteDecision,
        options: List[dict[str, Any]],
    ):
        """Run Monte Carlo simulation for options."""
        # Create simulation functions for each option
        strategies = {}
        for option in options:
            name = option.get("name", "unnamed")
            expected_value = option.get("value", 0.5)
            risk = option.get("risk", 0.3)

            # Create function that simulates outcomes with variance
            def make_sim(val, rk):
                import random

                def sim():
                    if random.random() < (1 - rk):  # Success probability
                        return random.gauss(val, val * rk * 0.5)
                    return random.gauss(-val * 0.5, val * rk)  # Failure

                return sim

            strategies[name] = make_sim(expected_value, risk)

        if strategies:
            results = self.monte_carlo.compare_strategies(strategies)
            # Store best result summary
            best = self.monte_carlo.recommend_decision(results, "risk_adjusted")
            route.simulation_result = {
                "strategies": list(results.keys()),
                "recommended": best,
                "details": {k: v.to_dict() for k, v in results.items()},
            }

    def _run_optimizer(
        self,
        route: RouteDecision,
        options: List[dict[str, Any]],
        criteria: str,
    ):
        """Run decision optimizer for options."""
        # Map criteria string to enum
        from .decision_optimizer import DecisionCriteria

        criteria_map = {
            "maximize_return": DecisionCriteria.MAXIMIZE_RETURN,
            "minimize_risk": DecisionCriteria.MINIMIZE_RISK,
            "minimize_cost": DecisionCriteria.MINIMIZE_COST,
            "minimize_time": DecisionCriteria.MINIMIZE_TIME,
            "balanced": DecisionCriteria.BALANCED,
        }
        decision_criteria = criteria_map.get(criteria, DecisionCriteria.BALANCED)

        decision = self.optimizer.create_decision(
            name=route.decision_type,
            criteria=decision_criteria,
        )

        for option in options:
            self.optimizer.add_option(
                decision_id=decision.id,
                option_id=option.get("id", str(uuid.uuid4())[:8]),
                name=option.get("name", "unnamed"),
                value=option.get("value", 0.0),
                risk=option.get("risk", 0.5),
                cost=option.get("cost", 0.0),
                time=option.get("time", 0.0),
                metadata=option,
            )

        outcome = self.optimizer.evaluate_options(decision.id)
        if outcome:
            route.optimizer_result = {
                "selected_option": decision.selected_option,
                "expected_value": outcome.expected_value,
                "risk_score": outcome.risk_score,
                "confidence": outcome.confidence,
            }

    def _synthesize_recommendation(self, route: RouteDecision):
        """Combine all analyses into final recommendation."""
        recommendations = []

        # From scenarios
        if route.scenarios:
            best_scenario = max(route.scenarios, key=lambda x: x.get("score", 0))
            recommendations.append(
                (
                    best_scenario.get("name", ""),
                    best_scenario.get("score", 0) * 0.4,  # 40% weight
                )
            )

        # From simulation
        if route.simulation_result:
            sim_rec = route.simulation_result.get("recommended", "")
            recommendations.append((sim_rec, 0.35))  # 35% weight

        # From optimizer
        if route.optimizer_result:
            opt_rec = route.optimizer_result.get("selected_option", "")
            conf = route.optimizer_result.get("confidence", 0.5)
            recommendations.append((opt_rec, conf * 0.25))  # 25% weight

        # Combine weighted recommendations
        if recommendations:
            scores: Dict[str, float] = {}
            for name, weight in recommendations:
                if name:
                    scores[name] = scores.get(name, 0) + weight

            if scores:
                best = max(scores.items(), key=lambda x: x[1])
                route.recommendation = best[0]
                route.confidence = min(0.95, best[1] / 0.4)  # Normalize

    def get_route(self, route_id: str) -> Optional[RouteDecision]:
        """Get a specific routed decision."""
        return self.routes.get(route_id)

    def list_routes(self) -> List[dict[str, Any]]:
        """List all routed decisions."""
        return [r.to_dict() for r in self.routes.values()]

    def get_status(self) -> Dict[str, Any]:
        """Get router status."""
        return {
            "total_routes": len(self.routes),
            "route_types": [t.value for t in RouteType],
            "engines": ["scenario_engine", "monte_carlo", "optimizer"],
        }


_ROUTER: Optional[QuantumRouter] = None


def get_quantum_router(data_dir: Optional[Path] = None) -> QuantumRouter:
    """Get or create global quantum router."""
    global _ROUTER
    if _ROUTER is None:
        _ROUTER = QuantumRouter(data_dir)
    return _ROUTER

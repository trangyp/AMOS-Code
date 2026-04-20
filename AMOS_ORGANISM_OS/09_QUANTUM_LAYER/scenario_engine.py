"""Scenario Engine — Parallel Scenario Evaluation

Evaluates multiple decision scenarios in parallel,
comparing outcomes to find optimal paths.
"""

import random
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any


class ScenarioStatus(Enum):
    """Status of a scenario evaluation."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScenarioResult:
    """Result of a scenario evaluation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    scenario_id: str = ""
    score: float = 0.0  # 0-1 success score
    risk_level: float = 0.0  # 0-1 risk assessment
    cost_estimate: float = 0.0
    time_estimate: float = 0.0  # seconds
    outcome_data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Scenario:
    """A single scenario for evaluation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    status: ScenarioStatus = ScenarioStatus.PENDING
    result: ScenarioResult = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
        }


class ScenarioEngine:
    """Evaluates multiple scenarios in parallel for decision making.

    Creates scenario variations, runs simulations,
    and compares outcomes to recommend optimal paths.
    """

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.scenarios: dict[str, Scenario] = {}
        self.evaluators: dict[str, Callable] = {}

        self._register_default_evaluators()

    def _register_default_evaluators(self):
        """Register default scenario evaluators."""
        self.evaluators["default"] = self._default_evaluator
        self.evaluators["risk_assessment"] = self._risk_evaluator
        self.evaluators["cost_benefit"] = self._cost_benefit_evaluator

    def create_scenario(
        self,
        name: str,
        description: str = "",
        parameters: dict[str, Any] = None,
    ) -> Scenario:
        """Create a new scenario."""
        scenario = Scenario(
            name=name,
            description=description,
            parameters=parameters or {},
        )
        self.scenarios[scenario.id] = scenario
        return scenario

    def evaluate_scenario(
        self,
        scenario_id: str,
        evaluator_type: str = "default",
    ) -> ScenarioResult:
        """Evaluate a single scenario."""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return None

        scenario.status = ScenarioStatus.RUNNING
        evaluator = self.evaluators.get(evaluator_type, self._default_evaluator)

        try:
            result = evaluator(scenario)
            scenario.result = result
            scenario.status = ScenarioStatus.COMPLETED
            return result
        except Exception as e:
            scenario.status = ScenarioStatus.FAILED
            scenario.result = ScenarioResult(
                scenario_id=scenario_id,
                score=0.0,
                risk_level=1.0,
                outcome_data={"error": str(e)},
            )
            return scenario.result

    def evaluate_all(
        self,
        evaluator_type: str = "default",
    ) -> dict[str, ScenarioResult]:
        """Evaluate all pending scenarios."""
        results = {}
        for scenario_id, scenario in self.scenarios.items():
            if scenario.status == ScenarioStatus.PENDING:
                result = self.evaluate_scenario(scenario_id, evaluator_type)
                if result:
                    results[scenario_id] = result
        return results

    def compare_scenarios(
        self,
        scenario_ids: list[str],
        metric: str = "score",
    ) -> list[dict[str, Any]]:
        """Compare multiple scenarios by a metric."""
        comparisons = []
        for sid in scenario_ids:
            scenario = self.scenarios.get(sid)
            if scenario and scenario.result:
                comparisons.append(
                    {
                        "id": sid,
                        "name": scenario.name,
                        "score": scenario.result.score,
                        "risk": scenario.result.risk_level,
                        "cost": scenario.result.cost_estimate,
                        "time": scenario.result.time_estimate,
                    }
                )

        # Sort by metric (descending for score, ascending for risk/cost/time)
        reverse = metric == "score"
        comparisons.sort(key=lambda x: x.get(metric, 0), reverse=reverse)
        return comparisons

    def recommend_best(
        self,
        scenario_ids: list[str],
        criteria: str = "balanced",  # score, risk, cost, balanced
    ) -> str:
        """Recommend the best scenario based on criteria."""
        if not scenario_ids:
            return None

        comparisons = self.compare_scenarios(scenario_ids)
        if not comparisons:
            return None

        if criteria == "score":
            return comparisons[0]["id"]  # Highest score
        elif criteria == "risk":
            return min(comparisons, key=lambda x: x["risk"])["id"]
        elif criteria == "cost":
            return min(comparisons, key=lambda x: x["cost"])["id"]
        elif criteria == "balanced":
            # Score - risk - normalized cost
            for comp in comparisons:
                comp["balanced_score"] = (
                    comp["score"] * 0.5 - comp["risk"] * 0.3 - (comp["cost"] / 100) * 0.2
                )
            return max(comparisons, key=lambda x: x["balanced_score"])["id"]

        return comparisons[0]["id"]

    # Default evaluators
    def _default_evaluator(self, scenario: Scenario) -> ScenarioResult:
        """Default scenario evaluator."""
        params = scenario.parameters
        # Simulate evaluation
        score = params.get("expected_success", 0.7)
        risk = params.get("risk_factor", 0.3)
        cost = params.get("estimated_cost", 100)
        time = params.get("estimated_time", 60)

        # Add some randomness for simulation
        score = max(0, min(1, score + random.uniform(-0.1, 0.1)))
        risk = max(0, min(1, risk + random.uniform(-0.05, 0.05)))

        return ScenarioResult(
            scenario_id=scenario.id,
            score=score,
            risk_level=risk,
            cost_estimate=cost,
            time_estimate=time,
        )

    def _risk_evaluator(self, scenario: Scenario) -> ScenarioResult:
        """Risk-focused evaluator."""
        params = scenario.parameters
        base_risk = params.get("risk_factor", 0.5)

        # Higher risk for complex scenarios
        complexity = len(params.get("steps", []))
        risk = min(1.0, base_risk + (complexity * 0.05))

        # Lower score for high risk
        score = max(0, 1 - risk - random.uniform(0, 0.1))

        return ScenarioResult(
            scenario_id=scenario.id,
            score=score,
            risk_level=risk,
            cost_estimate=params.get("estimated_cost", 100) * (1 + risk),
            time_estimate=params.get("estimated_time", 60),
        )

    def _cost_benefit_evaluator(self, scenario: Scenario) -> ScenarioResult:
        """Cost-benefit focused evaluator."""
        params = scenario.parameters
        benefit = params.get("expected_benefit", 100)
        cost = params.get("estimated_cost", 50)

        # ROI calculation
        roi = (benefit - cost) / max(cost, 1)
        score = max(0, min(1, roi / 2))  # Normalize

        return ScenarioResult(
            scenario_id=scenario.id,
            score=score,
            risk_level=params.get("risk_factor", 0.3),
            cost_estimate=cost,
            time_estimate=params.get("estimated_time", 60),
            outcome_data={"roi": roi, "benefit": benefit},
        )

    def list_scenarios(self) -> list[dict[str, Any]]:
        """List all scenarios."""
        return [s.to_dict() for s in self.scenarios.values()]

    def get_status(self) -> dict[str, Any]:
        """Get engine status."""
        pending = sum(1 for s in self.scenarios.values() if s.status == ScenarioStatus.PENDING)
        completed = sum(1 for s in self.scenarios.values() if s.status == ScenarioStatus.COMPLETED)
        failed = sum(1 for s in self.scenarios.values() if s.status == ScenarioStatus.FAILED)

        return {
            "total_scenarios": len(self.scenarios),
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "evaluators": list(self.evaluators.keys()),
        }


_ENGINE: ScenarioEngine = None


def get_scenario_engine(data_dir: Path = None) -> ScenarioEngine:
    """Get or create global scenario engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ScenarioEngine(data_dir)
    return _ENGINE

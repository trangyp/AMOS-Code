"""Monte Carlo Simulator — Probabilistic Decision Analysis

Runs Monte Carlo simulations to evaluate decision outcomes
with probabilistic confidence intervals.
"""

import random
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path
from typing import Any, Optional


@dataclass
class SimulationResult:
    """Result of a Monte Carlo simulation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    iterations: int = 1000
    mean_outcome: float = 0.0
    median_outcome: float = 0.0
    std_deviation: float = 0.0
    min_outcome: float = 0.0
    max_outcome: float = 0.0
    confidence_95_low: float = 0.0
    confidence_95_high: float = 0.0
    success_rate: float = 0.0  # Probability of positive outcome
    distribution: dict[str, float] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MonteCarloSimulator:
    """Runs Monte Carlo simulations for decision analysis.

    Simulates many possible outcomes based on probability distributions,
    providing confidence intervals and risk assessment.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir
        self.simulations: dict[str, SimulationResult] = {}

    def run_simulation(
        self,
        decision_func: Callable[[], float],
        iterations: int = 1000,
        name: str = "",
    ) -> SimulationResult:
        """Run a Monte Carlo simulation.

        Args:
            decision_func: Function that returns outcome value for one iteration
            iterations: Number of simulation runs
            name: Optional name for this simulation

        Returns:
            SimulationResult with statistical analysis
        """
        outcomes = []
        successes = 0

        for _ in range(iterations):
            outcome = decision_func()
            outcomes.append(outcome)
            if outcome > 0:
                successes += 1

        # Statistical analysis
        outcomes.sort()
        mean = sum(outcomes) / len(outcomes)
        median = outcomes[len(outcomes) // 2]
        min_val = min(outcomes)
        max_val = max(outcomes)

        # Standard deviation
        variance = sum((x - mean) ** 2 for x in outcomes) / len(outcomes)
        std_dev = variance**0.5

        # 95% confidence interval
        ci_low = outcomes[int(len(outcomes) * 0.025)]
        ci_high = outcomes[int(len(outcomes) * 0.975)]

        # Distribution buckets
        distribution = self._calculate_distribution(outcomes)

        result = SimulationResult(
            iterations=iterations,
            mean_outcome=mean,
            median_outcome=median,
            std_deviation=std_dev,
            min_outcome=min_val,
            max_outcome=max_val,
            confidence_95_low=ci_low,
            confidence_95_high=ci_high,
            success_rate=successes / iterations,
            distribution=distribution,
        )

        self.simulations[result.id] = result
        return result

    def simulate_risk_scenario(
        self,
        base_value: float,
        risk_factors: list[dict[str, Any]],
        iterations: int = 1000,
    ) -> SimulationResult:
        """Simulate a risk scenario with multiple risk factors.

        Args:
            base_value: Starting value
            risk_factors: List of {probability, impact, type} dicts
            iterations: Number of simulation runs
        """

        def scenario():
            value = base_value
            for factor in risk_factors:
                prob = factor.get("probability", 0.5)
                impact = factor.get("impact", 0.1)
                negative = factor.get("type", "loss") == "loss"

                if random.random() < prob:
                    if negative:
                        value *= 1 - impact
                    else:
                        value *= 1 + impact
            return value - base_value  # Return delta

        return self.run_simulation(scenario, iterations, "risk_scenario")

    def simulate_investment(
        self,
        principal: float,
        expected_return: float,
        volatility: float,
        time_periods: int = 12,  # months
        iterations: int = 1000,
    ) -> SimulationResult:
        """Simulate investment returns with given volatility."""

        def investment():
            value = principal
            for _ in range(time_periods):
                # Monthly return with random volatility
                monthly_return = random.gauss(
                    expected_return / time_periods, volatility / (time_periods**0.5)
                )
                value *= 1 + monthly_return
            return value - principal

        return self.run_simulation(investment, iterations, "investment")

    def compare_strategies(
        self,
        strategies: dict[str, Callable[[], float]],
        iterations: int = 1000,
    ) -> dict[str, SimulationResult]:
        """Compare multiple strategies via simulation."""
        results = {}
        for name, func in strategies.items():
            results[name] = self.run_simulation(func, iterations, name)
        return results

    def _calculate_distribution(self, outcomes: list[float]) -> dict[str, float]:
        """Calculate outcome distribution buckets."""
        if not outcomes:
            return {}

        min_val = min(outcomes)
        max_val = max(outcomes)
        if min_val == max_val:
            return {"single_value": float(min_val)}

        bucket_size = (max_val - min_val) / 5
        buckets = {
            "very_low": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "very_high": 0,
        }

        for outcome in outcomes:
            normalized = (outcome - min_val) / (max_val - min_val)
            if normalized < 0.2:
                buckets["very_low"] += 1
            elif normalized < 0.4:
                buckets["low"] += 1
            elif normalized < 0.6:
                buckets["medium"] += 1
            elif normalized < 0.8:
                buckets["high"] += 1
            else:
                buckets["very_high"] += 1

        # Convert to percentages
        total = len(outcomes)
        return {k: v / total for k, v in buckets.items()}

    def recommend_decision(
        self,
        results: dict[str, SimulationResult],
        criteria: str = "expected_value",  # expected_value, risk_adjusted, safety
    ) -> str:
        """Recommend best strategy based on simulation results."""
        if not results:
            return ""

        scored = []
        for name, result in results.items():
            if criteria == "expected_value":
                score = result.mean_outcome
            elif criteria == "risk_adjusted":
                # Sharpe-like ratio: return / risk
                if result.std_deviation > 0:
                    score = result.mean_outcome / result.std_deviation
                else:
                    score = result.mean_outcome
            elif criteria == "safety":
                # Prefer high success rate and low downside
                score = result.success_rate - (result.confidence_95_low < 0) * 0.5
            else:
                score = result.mean_outcome

            scored.append((name, score, result))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else ""

    def get_status(self) -> dict[str, Any]:
        """Get simulator status."""
        return {
            "total_simulations": len(self.simulations),
            "recent_simulations": list(self.simulations.keys())[-5:],
        }


_SIMULATOR: Optional[MonteCarloSimulator] = None


def get_monte_carlo_simulator(data_dir: Optional[Path] = None) -> MonteCarloSimulator:
    """Get or create global Monte Carlo simulator."""
    global _SIMULATOR
    if _SIMULATOR is None:
        _SIMULATOR = MonteCarloSimulator(data_dir)
    return _SIMULATOR

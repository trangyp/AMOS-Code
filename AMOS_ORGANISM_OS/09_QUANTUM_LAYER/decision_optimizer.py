"""
Decision Optimizer — Multi-Criteria Decision Analysis

Optimizes decisions using multiple criteria and weighted analysis.
Integrates with scenario engine and Monte Carlo simulator.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


class DecisionCriteria(Enum):
    """Decision optimization criteria."""
    MAXIMIZE_RETURN = "maximize_return"
    MINIMIZE_RISK = "minimize_risk"
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_TIME = "minimize_time"
    BALANCED = "balanced"


@dataclass
class DecisionOutcome:
    """Outcome prediction for a decision."""
    expected_value: float = 0.0
    risk_score: float = 0.0  # 0-1, higher = more risky
    cost: float = 0.0
    time_estimate: float = 0.0
    confidence: float = 0.5  # 0-1
    scenarios_analyzed: int = 0
    simulations_run: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Decision:
    """A decision with multiple options."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list)
    criteria: DecisionCriteria = DecisionCriteria.BALANCED
    weights: Dict[str, float] = field(default_factory=dict)
    selected_option: Optional[str] = None
    outcome: Optional[DecisionOutcome] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    decided_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "criteria": self.criteria.value,
            "outcome": self.outcome.to_dict() if self.outcome else None,
        }


class DecisionOptimizer:
    """
    Optimizes decisions using multi-criteria analysis.

    Evaluates options across multiple dimensions (cost, risk, time, value),
    applies weighted scoring, and recommends optimal choices.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir
        self.decisions: Dict[str, Decision] = {}
        self.default_weights = {
            "value": 0.35,
            "risk": 0.25,
            "cost": 0.20,
            "time": 0.20,
        }

    def create_decision(
        self,
        name: str,
        description: str = "",
        criteria: DecisionCriteria = DecisionCriteria.BALANCED,
        weights: Optional[Dict[str, float]] = None,
    ) -> Decision:
        """Create a new decision context."""
        decision = Decision(
            name=name,
            description=description,
            criteria=criteria,
            weights=weights or self.default_weights.copy(),
        )
        self.decisions[decision.id] = decision
        return decision

    def add_option(
        self,
        decision_id: str,
        option_id: str,
        name: str,
        value: float = 0.0,
        risk: float = 0.5,
        cost: float = 0.0,
        time: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add an option to a decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return False

        option = {
            "id": option_id,
            "name": name,
            "value": value,
            "risk": risk,
            "cost": cost,
            "time": time,
            "metadata": metadata or {},
            "score": 0.0,
        }
        decision.options.append(option)
        return True

    def evaluate_options(self, decision_id: str) -> Optional[DecisionOutcome]:
        """Evaluate all options for a decision and select best."""
        decision = self.decisions.get(decision_id)
        if not decision or not decision.options:
            return None

        weights = decision.weights
        criteria = decision.criteria

        # Calculate scores for each option
        scored_options = []
        for option in decision.options:
            score = self._calculate_score(option, weights, criteria)
            option["score"] = score
            scored_options.append((option, score))

        # Sort by score
        scored_options.sort(key=lambda x: x[1], reverse=True)

        # Select best option
        best_option = scored_options[0][0]
        decision.selected_option = best_option["id"]
        decision.decided_at = datetime.utcnow().isoformat()

        # Calculate outcome prediction
        decision.outcome = DecisionOutcome(
            expected_value=best_option["value"],
            risk_score=best_option["risk"],
            cost=best_option["cost"],
            time_estimate=best_option["time"],
            confidence=self._calculate_confidence(scored_options),
            scenarios_analyzed=len(decision.options),
        )

        return decision.outcome

    def _calculate_score(
        self,
        option: Dict[str, Any],
        weights: Dict[str, float],
        criteria: DecisionCriteria,
    ) -> float:
        """Calculate weighted score for an option."""
        # Normalize values (higher is better for value, lower for cost/risk/time)
        value_score = option["value"]  # Assume 0-1 or normalize
        risk_score = 1 - option["risk"]  # Invert: lower risk = higher score
        cost_score = 1 / (1 + option["cost"] / 100)  # Normalize cost
        time_score = 1 / (1 + option["time"] / 60)  # Normalize time

        if criteria == DecisionCriteria.MAXIMIZE_RETURN:
            return value_score
        elif criteria == DecisionCriteria.MINIMIZE_RISK:
            return risk_score
        elif criteria == DecisionCriteria.MINIMIZE_COST:
            return cost_score
        elif criteria == DecisionCriteria.MINIMIZE_TIME:
            return time_score
        else:  # BALANCED
            return (
                value_score * weights.get("value", 0.25)
                + risk_score * weights.get("risk", 0.25)
                + cost_score * weights.get("cost", 0.25)
                + time_score * weights.get("time", 0.25)
            )

    def _calculate_confidence(
        self,
        scored_options: List[Tuple[Dict[str, Any], float]],
    ) -> float:
        """Calculate confidence based on score separation."""
        if len(scored_options) < 2:
            return 0.5

        scores = [s for _, s in scored_options]
        best = scores[0]
        second = scores[1]

        # Higher confidence if best option is clearly better
        if best > 0:
            separation = (best - second) / best
            return min(0.95, 0.5 + separation)
        return 0.5

    def get_decision_report(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report for a decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return None

        return {
            "decision": decision.to_dict(),
            "options_ranked": sorted(
                decision.options,
                key=lambda x: x["score"],
                reverse=True,
            ),
            "recommendation": decision.selected_option,
            "confidence": decision.outcome.confidence if decision.outcome else 0,
        }

    def list_decisions(self) -> List[Dict[str, Any]]:
        """List all decisions."""
        return [d.to_dict() for d in self.decisions.values()]

    def get_status(self) -> Dict[str, Any]:
        """Get optimizer status."""
        pending = sum(1 for d in self.decisions.values() if not d.selected_option)
        decided = sum(1 for d in self.decisions.values() if d.selected_option)

        return {
            "total_decisions": len(self.decisions),
            "pending": pending,
            "decided": decided,
            "default_criteria": list(DecisionCriteria.__members__.keys()),
        }


_OPTIMIZER: Optional[DecisionOptimizer] = None


def get_decision_optimizer(data_dir: Optional[Path] = None) -> DecisionOptimizer:
    """Get or create global decision optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = DecisionOptimizer(data_dir)
    return _OPTIMIZER

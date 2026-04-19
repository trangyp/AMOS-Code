"""Explanatory Intelligence Bridge.

Integrates explanatory engine with AMOS Brain cognition.

Provides API for:
- Decision explanation
- Confidence explanation
- Reasoning trace visualization
- Action justification
"""

from __future__ import annotations


from pathlib import Path
from typing import Any

# Import explanatory engine
try:
    from repo_doctor.explanatory_engine import (
        Evidence,
        EvidenceStrength,
        Explanation,
        ExplanationType,
        ExplanatoryEngine,
        ReasoningStep,
        ReasoningTrace,
    )

    EXPLANATORY_AVAILABLE = True
except ImportError:
    EXPLANATORY_AVAILABLE = False


class ExplanatoryBridge:
    """Bridge between explanatory engine and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: Optional[ExplanatoryEngine] = None

    @property
    def engine(self) -> Optional[ExplanatoryEngine]:
        """Lazy initialization of explanatory engine."""
        if self._engine is None and EXPLANATORY_AVAILABLE:
            self._engine = ExplanatoryEngine()
        return self._engine

    def explain_decision(
        self, decision: dict[str, Any], context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Explain a decision."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return {"error": "explanatory_engine not available"}

        explanation = self.engine.explain_decision(decision, context)
        return explanation.to_dict()

    def explain_confidence(self, score: float, factors: dict[str, Any]) -> dict[str, Any]:
        """Explain confidence score."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return {"error": "explanatory_engine not available"}

        explanation = self.engine.explain_confidence(score, factors)
        return explanation.to_dict()

    def trace_reasoning(
        self,
        start_state: dict[str, Any],
        decision: dict[str, Any],
        steps: list[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Generate reasoning trace."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return {"error": "explanatory_engine not available"}

        trace = self.engine.trace_reasoning(start_state, decision, steps)
        return trace.to_dict()

    def justify_action(
        self,
        action: str,
        expected_outcome: str,
        risks: list[str],
        benefits: list[str],
    ) -> dict[str, Any]:
        """Justify an action."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return {"error": "explanatory_engine not available"}

        explanation = self.engine.justify_action(action, expected_outcome, risks, benefits)
        return explanation.to_dict()

    def compare_alternatives(
        self, alternatives: list[dict[str, Any]], criteria: list[str]
    ) -> dict[str, Any]:
        """Compare alternatives."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return {"error": "explanatory_engine not available"}

        explanation = self.engine.compare_alternatives(alternatives, criteria)
        return explanation.to_dict()

    def get_explanation_history(self) -> list[dict[str, Any]]:
        """Get explanation history."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return []

        return self.engine.get_explanation_history()

    def get_reasoning_traces(self) -> list[dict[str, Any]]:
        """Get reasoning traces."""
        if not EXPLANATORY_AVAILABLE or self.engine is None:
            return []

        return self.engine.get_traces()


def get_explanatory_bridge(repo_path: str | Path) -> ExplanatoryBridge:
    """Factory function to get explanatory bridge."""
    return ExplanatoryBridge(repo_path)

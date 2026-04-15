"""Predictive Intelligence Bridge.

Integrates predictive architecture engine with AMOS Brain cognition.

Provides:
- Failure prediction from health data
- Change risk assessment
- Early warning generation
- Trend extrapolation for architecture metrics
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import predictive engine
try:
    from repo_doctor.predictive_engine import (
        ChangeRiskAssessment,
        EarlyWarning,
        Prediction,
        PredictiveArchitectureEngine,
        get_predictive_engine,
    )

    PREDICTIVE_AVAILABLE = True
except ImportError:
    PREDICTIVE_AVAILABLE = False


class PredictiveIntelligenceBridge:
    """Bridge between predictive engine and AMOS Brain.

    Enables the brain to:
    - Predict future architecture failures
    - Assess risk of code changes
    - Generate early warnings
    - Learn from outcomes
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: PredictiveArchitectureEngine | None = None

    @property
    def engine(self) -> PredictiveArchitectureEngine | None:
        """Lazy initialization of predictive engine."""
        if self._engine is None and PREDICTIVE_AVAILABLE:
            self._engine = get_predictive_engine(self.repo_path)
        return self._engine

    def predict_from_health(self, health_data: dict[str, Any]) -> dict[str, Any]:
        """Generate predictions from health dashboard data."""
        if not PREDICTIVE_AVAILABLE or self.engine is None:
            return {"error": "predictive_engine not available"}

        return self.engine.analyze_health_data(health_data)

    def assess_change_risk(self, changed_files: list[str]) -> dict[str, Any]:
        """Assess risk of code changes before they are committed."""
        if not PREDICTIVE_AVAILABLE or self.engine is None:
            return {"error": "predictive_engine not available"}

        assessment = self.engine.assess_change_risk(changed_files)
        return {
            "overall_risk": assessment.overall_risk,
            "safe_to_proceed": assessment.safe_to_proceed,
            "risk_factors": assessment.risk_factors,
            "predicted_issues": assessment.predicted_issues,
            "recommended_tests": assessment.recommended_tests,
            "protected_invariants_at_risk": assessment.protected_invariants_at_risk,
        }

    def get_top_predictions(self, n: int = 5) -> list[dict[str, Any]]:
        """Get top N most confident predictions."""
        if not PREDICTIVE_AVAILABLE or self.engine is None:
            return []

        predictions = self.engine.get_top_predictions(n)
        return [
            {
                "id": p.prediction_id,
                "pattern": p.pattern_id,
                "metric": p.metric,
                "current": p.current_value,
                "predicted": p.predicted_value,
                "confidence": p.confidence,
                "lead_time_hours": p.lead_time_hours,
                "severity": p.severity,
                "message": p.message,
                "action": p.recommended_action,
            }
            for p in predictions
        ]

    def get_active_warnings(self) -> list[dict[str, Any]]:
        """Get all active early warnings."""
        if not PREDICTIVE_AVAILABLE or self.engine is None:
            return []

        warnings = self.engine.get_active_warnings()
        return [
            {
                "id": w.warning_id,
                "type": w.warning_type,
                "confidence": w.confidence,
                "lead_time_hours": w.lead_time_hours,
                "indicators": w.indicators,
                "actions": w.recommended_actions,
            }
            for w in warnings
        ]

    def get_overall_risk_score(self) -> float:
        """Get current overall risk score (0-1)."""
        if not PREDICTIVE_AVAILABLE or self.engine is None:
            return 0.0

        # Calculate from active predictions and warnings
        predictions = self.engine.get_top_predictions(5)
        warnings = self.engine.get_active_warnings()

        return self.engine._calculate_risk_score(predictions, warnings)


def get_predictive_bridge(repo_path: str | Path | None = None) -> PredictiveIntelligenceBridge:
    """Factory function to get predictive bridge instance."""
    return PredictiveIntelligenceBridge(repo_path or ".")

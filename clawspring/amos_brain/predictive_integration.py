"""AMOS Predictive Integration - Connect Organism Predictive Engine to Cognitive System."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Add organism OS to path - use relative path from this file
ORGANISM_PATH = Path(__file__).parent.parent.parent / "AMOS_ORGANISM_OS"
if str(ORGANISM_PATH) not in sys.path:
    sys.path.insert(0, str(ORGANISM_PATH))


@dataclass
class PredictionResult:
    """Result from predictive analysis."""

    task_type: str
    predicted_duration_ms: float
    confidence: float
    recommended_priority: str
    risk_factors: list


class PredictiveIntegration:
    """Integrates organism predictive engine with cognitive routing."""

    def __init__(self):
        self._engine = None
        self._initialized = False
        self._initialize()

    def _initialize(self):
        """Initialize predictive engine connection."""
        try:
            # Import predictive engine
            from AMOS_ORGANISM_OS.QUANTUM_LAYER.predictive_engine import PredictiveEngine

            # Create engine instance with organism root
            self._engine = PredictiveEngine(ORGANISM_PATH)
            self._initialized = True
        except Exception as e:
            # Fallback: create basic prediction without organism engine
            self._initialized = False
            print(f"[Predictive] Using fallback mode: {e}")

    def predict_cognitive_task(
        self, task_description: str, domain: str, priority: str = "MEDIUM"
    ) -> PredictionResult:
        """Predict outcomes for cognitive tasks."""
        # Map domain to task type
        task_type = self._map_domain_to_task_type(domain)

        if self._initialized and self._engine:
            try:
                # Use organism predictive engine
                prediction = self._engine.predict_task_duration(
                    task_type=task_type, priority=priority
                )

                return PredictionResult(
                    task_type=task_type,
                    predicted_duration_ms=prediction.predicted_duration_ms,
                    confidence=prediction.confidence,
                    recommended_priority=self._recommend_priority(prediction),
                    risk_factors=self._identify_risk_factors(prediction, domain),
                )
            except Exception:
                pass

        # Fallback predictions based on domain
        return self._fallback_prediction(task_type, priority, domain)

    def _map_domain_to_task_type(self, domain: str) -> str:
        """Map cognitive domain to organism task type."""
        mapping = {
            "software": "code",
            "analysis": "analysis",
            "security": "security",
            "design": "documentation",
            "data": "analysis",
            "infrastructure": "code",
            "testing": "test",
        }
        return mapping.get(domain, "analysis")

    def _recommend_priority(self, prediction) -> str:
        """Recommend priority based on prediction."""
        if prediction.predicted_duration_ms > 2000:
            return "HIGH"
        elif prediction.predicted_duration_ms > 1000:
            return "MEDIUM"
        return "LOW"

    def _identify_risk_factors(self, prediction, domain: str) -> list:
        """Identify risk factors from prediction."""
        risks = []
        if prediction.confidence < 0.5:
            risks.append("Low prediction confidence")
        if prediction.predicted_duration_ms > 3000:
            risks.append("Long execution time")
        if domain == "security":
            risks.append("Security domain - requires extra validation")
        return risks

    def _fallback_prediction(self, task_type: str, priority: str, domain: str) -> PredictionResult:
        """Fallback prediction when organism engine unavailable."""
        # Baseline durations (ms)
        baselines = {
            "code": 1200,
            "analysis": 500,
            "security": 600,
            "documentation": 800,
            "test": 1000,
        }

        # Priority multipliers
        multipliers = {
            "CRITICAL": 0.7,
            "HIGH": 0.85,
            "MEDIUM": 1.0,
            "LOW": 1.3,
        }

        base = baselines.get(task_type, 1000)
        mult = multipliers.get(priority, 1.0)

        return PredictionResult(
            task_type=task_type,
            predicted_duration_ms=base * mult,
            confidence=0.6,
            recommended_priority=priority,
            risk_factors=[] if domain != "security" else ["Security domain"],
        )

    def record_execution(
        self,
        task_type: str,
        priority: str,
        duration_ms: float,
        success: bool,
        agent_id: str = "cognitive_router",
    ):
        """Record execution for future predictions."""
        if self._initialized and self._engine:
            try:
                self._engine.record_execution(
                    task_type=task_type,
                    priority=priority,
                    duration_ms=duration_ms,
                    agent_id=agent_id,
                    success=success,
                )
            except Exception:
                pass

    def get_status(self) -> Dict[str, Any]:
        """Get predictive integration status."""
        return {
            "initialized": self._initialized,
            "engine_available": self._engine is not None,
            "organism_path": str(ORGANISM_PATH),
        }


# Singleton instance
_predictive_integration: Optional[PredictiveIntegration] = None


def get_predictive_integration() -> PredictiveIntegration:
    """Get or create singleton predictive integration."""
    global _predictive_integration
    if _predictive_integration is None:
        _predictive_integration = PredictiveIntegration()
    return _predictive_integration


def predict_task(task_description: str, domain: str, priority: str = "MEDIUM") -> PredictionResult:
    """Convenience function to predict cognitive task."""
    integration = get_predictive_integration()
    return integration.predict_cognitive_task(task_description, domain, priority)


if __name__ == "__main__":
    # Test predictive integration
    print("=" * 60)
    print("AMOS Predictive Integration - Test")
    print("=" * 60)

    integration = get_predictive_integration()
    status = integration.get_status()

    print(f"\nStatus: {status}")

    # Test prediction
    test_tasks = [
        ("Design API endpoint", "software", "MEDIUM"),
        ("Analyze security vulnerability", "security", "HIGH"),
        ("Write documentation", "design", "LOW"),
    ]

    print("\nPredictions:")
    for task, domain, priority in test_tasks:
        pred = predict_task(task, domain, priority)
        print(
            f"  {task[:30]:<30} -> {pred.predicted_duration_ms:.0f}ms (conf: {pred.confidence:.0%})"
        )

"""Unified Architecture Orchestrator Bridge (Layer 16).

Integrates unified architecture orchestration with AMOS Brain cognition.

Provides API for:
- Unified assessment across all 19 invariants
- Cross-domain correlation detection
- Architectural decision synthesis
- Unified health monitoring
"""

from __future__ import annotations


from pathlib import Path
from typing import Any

# Import unified orchestrator
try:
    from repo_doctor.unified_architecture_orchestrator import (
        UnifiedArchitectureOrchestrator,
        UnifiedArchitectureState,
    )

    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False


class UnifiedOrchestratorBridge:
    """Bridge between unified orchestrator and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: UnifiedArchitectureOrchestrator | None = None

    @property
    def engine(self) -> UnifiedArchitectureOrchestrator | None:
        """Lazy initialization of unified orchestrator."""
        if self._engine is None and UNIFIED_AVAILABLE:
            self._engine = UnifiedArchitectureOrchestrator()
        return self._engine

    def assess_unified_architecture(self) -> dict[str, Any]:
        """Perform unified assessment across all 19 invariants."""
        if not UNIFIED_AVAILABLE or self.engine is None:
            return {"error": "unified_orchestrator not available"}

        state = self.engine.assess_unified_architecture()
        return state.to_dict()

    def get_unified_decision(self) -> dict[str, Any]:
        """Get synthesized architectural decision."""
        if not UNIFIED_AVAILABLE or self.engine is None:
            return {"error": "unified_orchestrator not available"}

        # Ensure we have an assessment
        if not self.engine.states:
            self.engine.assess_unified_architecture()

        return self.engine.get_architectural_decision_report()

    def get_cross_domain_correlations(self) -> dict[str, Any]:
        """Get active cross-domain correlations."""
        if not UNIFIED_AVAILABLE or self.engine is None:
            return {"error": "unified_orchestrator not available"}

        correlations = self.engine.correlations
        return {
            "correlations": [
                {
                    "id": c.correlation_id,
                    "source": c.source_invariant,
                    "target": c.target_invariant,
                    "type": c.correlation_type.value,
                    "strength": c.strength,
                    "explanation": c.explanation,
                }
                for c in correlations
            ],
            "count": len(correlations),
        }

    def get_unified_insights(self) -> dict[str, Any]:
        """Get unified architectural insights."""
        if not UNIFIED_AVAILABLE or self.engine is None:
            return {"error": "unified_orchestrator not available"}

        insights = self.engine.get_unified_insights()
        return {
            "insights": insights,
            "count": len(insights),
        }

    def get_architectural_health_dashboard(self) -> dict[str, Any]:
        """Get comprehensive health dashboard."""
        if not UNIFIED_AVAILABLE or self.engine is None:
            return {"error": "unified_orchestrator not available"}

        # Ensure we have an assessment
        if not self.engine.states:
            self.engine.assess_unified_architecture()

        latest = self.engine.states[-1]

        return {
            "timestamp": latest.timestamp,
            "health_scores": {
                "constitutional": latest.constitutional_health,
                "temporal": latest.temporal_health,
                "operational": latest.operational_health,
                "resilience": latest.resilience_health,
                "overall": latest.overall_health,
            },
            "status": self._health_to_status(latest.overall_health),
            "critical_issues": len(latest.critical_violations),
            "warning_issues": len(latest.warning_violations),
            "invariant_summary": {
                "total": 19,
                "valid": sum(1 for v in latest.invariants.values() if v.valid),
                "violated": sum(1 for v in latest.invariants.values() if not v.valid),
            },
        }

    def _health_to_status(self, health: float) -> str:
        """Convert health score to status."""
        if health >= 0.9:
            return "healthy"
        elif health >= 0.7:
            return "degraded"
        elif health >= 0.5:
            return "warning"
        else:
            return "critical"


def get_unified_orchestrator_bridge(repo_path: str | Path) -> UnifiedOrchestratorBridge:
    """Factory function to get unified orchestrator bridge."""
    return UnifiedOrchestratorBridge(repo_path)

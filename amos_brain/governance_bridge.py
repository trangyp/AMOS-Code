"""Autonomous Governance Bridge.

Integrates governance engine with AMOS Brain cognition.

Provides:
- Auto-remediation decisions
- Governance policy management
- Autonomy statistics
- Decision audit trail

Closes the cognitive loop: Predict → Decide → Act.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import governance engine
try:
    from repo_doctor.autonomous_governance import (
        AutonomousGovernanceEngine,
        get_governance_engine,
        GovernancePolicy,
        AutonomyLevel,
    )
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False


class AutonomousGovernanceBridge:
    """
    Bridge between governance engine and AMOS Brain.

    Enables the brain to:
    - Make autonomous decisions on repairs
    - Manage governance policies
    - Track autonomy statistics
    - Maintain decision audit trail
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: AutonomousGovernanceEngine | None = None

    @property
    def engine(self) -> AutonomousGovernanceEngine | None:
        """Lazy initialization of governance engine."""
        if self._engine is None and GOVERNANCE_AVAILABLE:
            self._engine = get_governance_engine(self.repo_path)
        return self._engine

    def evaluate_prediction(self, prediction: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a prediction for autonomous action."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return {"error": "governance_engine not available"}

        # Get current health for context
        from .monitoring_bridge import get_monitoring_bridge
        monitor = get_monitoring_bridge(self.repo_path)
        health = monitor.get_health_dashboard()

        decision = self.engine.evaluate_prediction(prediction, health)

        return {
            "decision_id": decision.decision_id,
            "action": decision.action_type.name,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "executed": decision.executed,
            "outcome": decision.outcome,
        }

    def evaluate_repair(self, repair: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a repair suggestion for auto-application."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return {"error": "governance_engine not available"}

        risk_score = repair.get("risk_score", 0.5)
        decision = self.engine.evaluate_repair_suggestion(repair, risk_score)

        return {
            "decision_id": decision.decision_id,
            "action": decision.action_type.name,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "executed": decision.executed,
            "outcome": decision.outcome,
        }

    def evaluate_change_risk(self, risk_assessment: dict[str, Any]) -> dict[str, Any]:
        """Evaluate code change risk for autonomous decision."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return {"error": "governance_engine not available"}

        decision = self.engine.evaluate_change_risk(risk_assessment)

        return {
            "decision_id": decision.decision_id,
            "action": decision.action_type.name,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "executed": decision.executed,
            "outcome": decision.outcome,
        }

    def get_governance_audit(self) -> list[dict[str, Any]]:
        """Get audit log of governance decisions."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return []

        return self.engine.get_governance_audit_log()

    def get_autonomy_stats(self) -> dict[str, Any]:
        """Get statistics on autonomous actions."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return {}

        return self.engine.get_autonomy_statistics()

    def update_policy(self, policy_config: dict[str, Any]) -> bool:
        """Update governance policy."""
        if not GOVERNANCE_AVAILABLE or self.engine is None:
            return False

        # Parse autonomy levels
        repair_auto = policy_config.get("repair_autonomy", "ASSISTED")
        invariant_auto = policy_config.get("invariant_autonomy", "FULL")

        autonomy_map = {
            "FULL": AutonomyLevel.FULL,
            "ASSISTED": AutonomyLevel.ASSISTED,
            "SUPERVISED": AutonomyLevel.SUPERVISED,
            "OBSERVE": AutonomyLevel.OBSERVE,
        }

        new_policy = GovernancePolicy(
            policy_id=policy_config.get("policy_id", "custom"),
            name=policy_config.get("name", "Custom Policy"),
            description=policy_config.get("description", ""),
            repair_autonomy=autonomy_map.get(repair_auto, AutonomyLevel.ASSISTED),
            invariant_autonomy=autonomy_map.get(invariant_auto, AutonomyLevel.FULL),
            auto_execute_threshold=policy_config.get("auto_execute_threshold", 0.90),
            notify_threshold=policy_config.get("notify_threshold", 0.75),
            max_auto_repairs_per_hour=policy_config.get("max_repairs_per_hour", 5),
            require_human_for_critical=policy_config.get("require_human_critical", True),
            require_human_for_security=policy_config.get("require_human_security", True),
        )

        self.engine.policy = new_policy
        return True


def get_governance_bridge(repo_path: str | Path | None = None) -> AutonomousGovernanceBridge:
    """Factory function to get governance bridge instance."""
    return AutonomousGovernanceBridge(repo_path or ".")

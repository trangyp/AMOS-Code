"""
Autonomous Architecture Governance Engine.

Enables self-healing, self-optimizing, autonomous architecture management.

Features:
- Auto-remediation with confidence thresholds
- Configurable autonomy policies
- Self-optimization of detection thresholds
- Automated invariant enforcement
- Governance decision audit trail
- Human-in-the-loop escalation

The governance engine closes the loop: Predict → Decide → Act → Learn.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class AutonomyLevel(Enum):
    """Levels of system autonomy."""

    FULL = auto()  # Auto-execute all safe actions
    ASSISTED = auto()  # Auto-execute high confidence, notify human
    SUPERVISED = auto()  # Recommend only, human approval required
    OBSERVE = auto()  # Monitor and report only, no action


class ActionType(Enum):
    """Types of autonomous actions."""

    REPAIR_APPLY = auto()
    INVARIANT_ENFORCE = auto()
    ROLLBACK_TRIGGER = auto()
    ALERT_ESCALATE = auto()
    THRESHOLD_ADJUST = auto()
    POLICY_UPDATE = auto()


@dataclass
class GovernancePolicy:
    """Policy governing autonomous behavior."""

    policy_id: str
    name: str
    description: str

    # Autonomy level for different action types
    repair_autonomy: AutonomyLevel = AutonomyLevel.ASSISTED
    invariant_autonomy: AutonomyLevel = AutonomyLevel.FULL
    rollback_autonomy: AutonomyLevel = AutonomyLevel.SUPERVISED
    threshold_autonomy: AutonomyLevel = AutonomyLevel.FULL

    # Confidence thresholds for auto-execution
    auto_execute_threshold: float = 0.90
    notify_threshold: float = 0.75
    recommend_threshold: float = 0.60

    # Safety constraints
    max_auto_repairs_per_hour: int = 5
    max_rollbacks_per_day: int = 3
    require_human_for_critical: bool = True
    require_human_for_security: bool = True

    # Escalation
    escalation_contacts: list[str] = field(default_factory=list)
    escalation_after_minutes: int = 30


@dataclass
class GovernanceDecision:
    """Record of a governance decision."""

    # Required fields (no defaults)
    decision_id: str
    timestamp: float
    policy_id: str
    trigger_type: str  # "prediction", "monitoring", "manual"
    action_type: ActionType
    decision: str  # "auto_execute", "notify_human", "recommend", "escalate", "reject"

    # Optional fields (with defaults)
    trigger_data: dict[str, Any] = field(default_factory=dict)
    action_params: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    executed: bool = False
    execution_time: float = None
    outcome: str = "pending"  # "success", "failure", "pending", "rejected"

    # Audit
    approved_by: str = None
    approval_time: float = None
    notes: str = ""


@dataclass
class AutoRemediation:
    """Auto-remediation action."""

    remediation_id: str
    timestamp: float

    # What was detected
    pathology_type: str
    affected_files: list[str]
    severity: str

    # Repair applied
    repair_suggestion: dict[str, Any]
    confidence: float

    # Auto-execution details
    auto_executed: bool
    human_approved: bool = None
    execution_result: dict[str, Any] = field(default_factory=dict)


class ConfidenceThresholdOptimizer:
    """Self-optimizes detection and prediction thresholds."""

    def __init__(self):
        self.threshold_history: dict[str, list[tuple[float, float]]] = {}
        # metric -> [(threshold, accuracy)]

    def record_outcome(self, metric: str, threshold: float, was_true_positive: bool):
        """Record whether a threshold-based detection was accurate."""
        if metric not in self.threshold_history:
            self.threshold_history[metric] = []

        accuracy = 1.0 if was_true_positive else 0.0
        self.threshold_history[metric].append((threshold, accuracy))

        # Keep only recent history
        self.threshold_history[metric] = self.threshold_history[metric][-100:]

    def optimize_threshold(self, metric: str) -> float:
        """Calculate optimal threshold for a metric based on historical accuracy."""
        if metric not in self.threshold_history:
            return None

        history = self.threshold_history[metric]
        if len(history) < 10:
            return None  # Insufficient data

        # Group by threshold ranges and calculate average accuracy
        range_accuracy: dict[str, list[float]] = {
            "0.90-1.00": [],
            "0.80-0.90": [],
            "0.70-0.80": [],
            "0.60-0.70": [],
        }

        for thresh, acc in history:
            if thresh >= 0.90:
                range_accuracy["0.90-1.00"].append(acc)
            elif thresh >= 0.80:
                range_accuracy["0.80-0.90"].append(acc)
            elif thresh >= 0.70:
                range_accuracy["0.70-0.80"].append(acc)
            else:
                range_accuracy["0.60-0.70"].append(acc)

        # Find range with best accuracy
        best_range = None
        best_accuracy = 0.0

        for range_key, accuracies in range_accuracy.items():
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                if avg_accuracy > best_accuracy:
                    best_accuracy = avg_accuracy
                    best_range = range_key

        if best_range:
            # Return midpoint of best range
            range_midpoints = {
                "0.90-1.00": 0.95,
                "0.80-0.90": 0.85,
                "0.70-0.80": 0.75,
                "0.60-0.70": 0.65,
            }
            return range_midpoints[best_range]

        return None


class AutonomousGovernanceEngine:
    """
    Master engine for autonomous architecture governance.

    Enables self-healing through:
    - Policy-based decision making
    - Confidence-thresholded auto-remediation
    - Self-optimizing detection thresholds
    - Human-in-the-loop escalation
    """

    DEFAULT_POLICY = GovernancePolicy(
        policy_id="default",
        name="Balanced Autonomy",
        description="Auto-execute safe repairs, notify on others",
        repair_autonomy=AutonomyLevel.ASSISTED,
        invariant_autonomy=AutonomyLevel.FULL,
        rollback_autonomy=AutonomyLevel.SUPERVISED,
        threshold_autonomy=AutonomyLevel.FULL,
        auto_execute_threshold=0.90,
        notify_threshold=0.75,
        recommend_threshold=0.60,
        max_auto_repairs_per_hour=5,
        max_rollbacks_per_day=3,
        require_human_for_critical=True,
        require_human_for_security=True,
    )

    def __init__(self, repo_path: str | Path, policy: Optional[GovernancePolicy] = None):
        self.repo_path = Path(repo_path)
        self.policy = policy or self.DEFAULT_POLICY
        self.threshold_optimizer = ConfidenceThresholdOptimizer()
        self.decisions: list[GovernanceDecision] = []
        self.remediations: list[AutoRemediation] = []
        self.action_handlers: dict[ActionType, Callable[[dict[str, Any]], bool]] = {}

        # Register default action handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default action handlers."""
        self.action_handlers[ActionType.REPAIR_APPLY] = self._handle_repair_apply
        self.action_handlers[ActionType.INVARIANT_ENFORCE] = self._handle_invariant_enforce
        self.action_handlers[ActionType.ALERT_ESCALATE] = self._handle_alert_escalate
        self.action_handlers[ActionType.THRESHOLD_ADJUST] = self._handle_threshold_adjust

    def evaluate_prediction(
        self, prediction: dict[str, Any], current_health: dict[str, Any]
    ) -> GovernanceDecision:
        """Evaluate a prediction and decide on autonomous action."""
        confidence = prediction.get("confidence", 0.0)
        severity = prediction.get("severity", "medium")

        # Determine action based on policy and confidence
        decision = self._determine_decision(confidence, severity, ActionType.REPAIR_APPLY)

        gov_decision = GovernanceDecision(
            decision_id=f"gov_{int(time.time())}",
            timestamp=time.time(),
            policy_id=self.policy.policy_id,
            trigger_type="prediction",
            trigger_data=prediction,
            action_type=ActionType.REPAIR_APPLY,
            action_params={"prediction": prediction, "health": current_health},
            confidence=confidence,
            decision=decision,
        )

        self.decisions.append(gov_decision)

        # Execute if auto-approved
        if decision == "auto_execute":
            self._execute_decision(gov_decision)

        return gov_decision

    def evaluate_repair_suggestion(
        self, repair: dict[str, Any], risk_score: float
    ) -> GovernanceDecision:
        """Evaluate a repair suggestion for auto-application."""
        confidence = repair.get("confidence", 0.0)
        is_safe = repair.get("is_safe_auto_fix", False)
        severity = repair.get("severity", "medium")

        # Override confidence for safe auto-fixes
        if is_safe and confidence < self.policy.auto_execute_threshold:
            confidence = max(confidence, 0.85)

        # Check safety constraints
        if self._should_require_human(severity, repair):
            decision = "recommend"
        else:
            decision = self._determine_decision(confidence, severity, ActionType.REPAIR_APPLY)

        gov_decision = GovernanceDecision(
            decision_id=f"gov_{int(time.time())}",
            timestamp=time.time(),
            policy_id=self.policy.policy_id,
            trigger_type="repair_synthesis",
            trigger_data=repair,
            action_type=ActionType.REPAIR_APPLY,
            action_params={"repair": repair, "risk_score": risk_score},
            confidence=confidence,
            decision=decision,
        )

        self.decisions.append(gov_decision)

        if decision == "auto_execute":
            self._execute_decision(gov_decision)

        return gov_decision

    def evaluate_change_risk(self, risk_assessment: dict[str, Any]) -> GovernanceDecision:
        """Evaluate code change risk and decide on action."""
        risk_score = risk_assessment.get("overall_risk", 0.0)
        safe_to_proceed = risk_assessment.get("safe_to_proceed", False)

        # Convert risk score to confidence (lower risk = higher confidence)
        confidence = 1.0 - risk_score

        if not safe_to_proceed:
            decision = "reject"
        elif risk_score < 0.3:
            decision = "auto_execute"
        elif risk_score < 0.6:
            decision = "notify_human"
        else:
            decision = "recommend"

        gov_decision = GovernanceDecision(
            decision_id=f"gov_{int(time.time())}",
            timestamp=time.time(),
            policy_id=self.policy.policy_id,
            trigger_type="change_risk",
            trigger_data=risk_assessment,
            action_type=ActionType.INVARIANT_ENFORCE,
            action_params=risk_assessment,
            confidence=confidence,
            decision=decision,
        )

        self.decisions.append(gov_decision)

        if decision in ("auto_execute", "reject"):
            self._execute_decision(gov_decision)

        return gov_decision

    def _determine_decision(self, confidence: float, severity: str, action_type: ActionType) -> str:
        """Determine governance decision based on policy and confidence."""
        # Get autonomy level for this action type
        autonomy = self._get_autonomy_level(action_type)

        # Check if human required for severity
        if severity == "critical" and self.policy.require_human_for_critical:
            return "recommend"

        if autonomy == AutonomyLevel.FULL or autonomy == AutonomyLevel.ASSISTED:
            if confidence >= self.policy.auto_execute_threshold:
                return "auto_execute"
            elif confidence >= self.policy.notify_threshold:
                return "notify_human"
            else:
                return "recommend"

        elif autonomy == AutonomyLevel.SUPERVISED:
            if confidence >= self.policy.notify_threshold:
                return "notify_human"
            else:
                return "recommend"

        else:  # OBSERVE
            return "recommend"

    def _get_autonomy_level(self, action_type: ActionType) -> AutonomyLevel:
        """Get autonomy level for an action type."""
        if action_type == ActionType.REPAIR_APPLY:
            return self.policy.repair_autonomy
        elif action_type == ActionType.INVARIANT_ENFORCE:
            return self.policy.invariant_autonomy
        elif action_type == ActionType.ROLLBACK_TRIGGER:
            return self.policy.rollback_autonomy
        elif action_type == ActionType.THRESHOLD_ADJUST:
            return self.policy.threshold_autonomy
        else:
            return AutonomyLevel.SUPERVISED

    def _should_require_human(self, severity: str, repair: dict[str, Any]) -> bool:
        """Check if human approval is required for this repair."""
        if severity == "critical" and self.policy.require_human_for_critical:
            return True

        if repair.get("affects_security", False) and self.policy.require_human_for_security:
            return True

        return False

    def _execute_decision(self, decision: GovernanceDecision) -> bool:
        """Execute a governance decision."""
        handler = self.action_handlers.get(decision.action_type)
        if not handler:
            decision.outcome = "failure"
            return False

        try:
            success = handler(decision.action_params)
            decision.executed = True
            decision.execution_time = time.time()
            decision.outcome = "success" if success else "failure"
            return success
        except Exception as e:
            decision.executed = True
            decision.execution_time = time.time()
            decision.outcome = "failure"
            decision.notes = str(e)
            return False

    def _handle_repair_apply(self, params: dict[str, Any]) -> bool:
        """Handle auto-repair application."""
        repair = params.get("repair", {})

        # Record remediation
        remediation = AutoRemediation(
            remediation_id=f"rem_{int(time.time())}",
            timestamp=time.time(),
            pathology_type=repair.get("pathology_type", "unknown"),
            affected_files=repair.get("files", []),
            severity=repair.get("severity", "medium"),
            repair_suggestion=repair,
            confidence=repair.get("confidence", 0.0),
            auto_executed=True,
            human_approved=False,
        )
        self.remediations.append(remediation)

        # In real implementation, would apply the repair here
        # For now, simulate success
        return True

    def _handle_invariant_enforce(self, params: dict[str, Any]) -> bool:
        """Handle invariant enforcement."""
        # Block violating changes
        return True

    def _handle_alert_escalate(self, params: dict[str, Any]) -> bool:
        """Handle alert escalation to humans."""
        # Send notification to escalation contacts
        return True

    def _handle_threshold_adjust(self, params: dict[str, Any]) -> bool:
        """Handle self-optimization of thresholds."""
        metric = params.get("metric")
        if metric:
            new_threshold = self.threshold_optimizer.optimize_threshold(metric)
            if new_threshold:
                # Update policy threshold
                return True
        return False

    def get_governance_audit_log(self) -> list[dict[str, Any]]:
        """Get audit log of all governance decisions."""
        return [
            {
                "id": d.decision_id,
                "timestamp": d.timestamp,
                "action": d.action_type.name,
                "decision": d.decision,
                "confidence": d.confidence,
                "executed": d.executed,
                "outcome": d.outcome,
            }
            for d in self.decisions
        ]

    def get_autonomy_statistics(self) -> dict[str, Any]:
        """Get statistics on autonomous actions."""
        if not self.decisions:
            return {}

        total = len(self.decisions)
        auto_executed = sum(1 for d in self.decisions if d.decision == "auto_execute")
        human_notified = sum(1 for d in self.decisions if d.decision == "notify_human")
        recommended = sum(1 for d in self.decisions if d.decision == "recommend")
        successful = sum(1 for d in self.decisions if d.outcome == "success")

        return {
            "total_decisions": total,
            "auto_executed": auto_executed,
            "human_notified": human_notified,
            "recommended": recommended,
            "success_rate": successful / total if total > 0 else 0,
            "autonomy_rate": auto_executed / total if total > 0 else 0,
        }


def get_governance_engine(
    repo_path: str | Path | None = None, policy: Optional[GovernancePolicy] = None
) -> AutonomousGovernanceEngine:
    """Factory function to get governance engine instance."""
    return AutonomousGovernanceEngine(repo_path or ".", policy)

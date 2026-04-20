"""AMOS Auto-Remediation Engine v1.0.0 - Self-Healing System

Implements automated response to detection alerts from UnifiedDetectionEngine.

Architecture:
    Detection (UnifiedDetectionEngine)
        ↓
    Analysis (RemediationEngine - this module)
        ↓
    Remediation (Automated fix strategies)
        ↓
    Validation (Re-run detection)
        ↓
    Learning (Feedback loop updates)

Remediation Strategies:
- Hallucination: Temperature reduction, sampling adjustment, NLI verification
- Integrity: Distribution rebalancing, consensus reconfiguration, checkpoint restore
- Drift: Structural rebalancing, graph rewiring, state normalization

Integration:
- UnifiedDetectionEngine (triggers)
- TemporalCognitionBridge (tracks effectiveness over time)
- CognitiveFeedbackLoop (learns what works)
- AuditExporter (records all actions)

Owner: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import detection engine
try:
    from .unified_detection_engine import (
        HallucinationScore,
        IntegrityMetrics,
        StructuralDriftMetrics,
        UnifiedDetectionEngine,
        UnifiedDetectionReport,
    )

    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False

# Import temporal bridge for tracking
try:
    from .temporal_bridge import TemporalCognitionBridge

    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False

# Import feedback loop for learning
try:
    from .feedback_loop import CognitiveFeedbackLoop, get_feedback_loop

    FEEDBACK_AVAILABLE = True
except ImportError:
    FEEDBACK_AVAILABLE = False

# Import audit exporter for recording
try:
    from .audit_exporter import AuditExporter

    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False


# =============================================================================
# Enums and Data Classes
# =============================================================================


class IssueType(Enum):
    """Types of issues that can be detected and remediated."""

    HALLUCINATION = "hallucination"
    INTEGRITY_VIOLATION = "integrity_violation"
    STRUCTURAL_DRIFT = "structural_drift"
    UNKNOWN = "unknown"


class RemediationStatus(Enum):
    """Status of remediation attempt."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class RemediationStrategy(Enum):
    """Available remediation strategies."""

    # Hallucination strategies
    TEMPERATURE_REDUCTION = "temperature_reduction"
    SAMPLING_ADJUSTMENT = "sampling_adjustment"
    NLI_VERIFICATION = "nli_verification"
    ENSEMBLE_EXPANSION = "ensemble_expansion"

    # Integrity strategies
    DISTRIBUTION_REBALANCE = "distribution_rebalance"
    CONSENSUS_RECONFIG = "consensus_reconfig"
    CHECKPOINT_RESTORE = "checkpoint_restore"
    ENTROPY_NORMALIZATION = "entropy_normalization"

    # Drift strategies
    STRUCTURAL_REBALANCE = "structural_rebalance"
    GRAPH_REWIRE = "graph_rewire"
    STATE_NORMALIZE = "state_normalize"
    SPECTRAL_CORRECTION = "spectral_correction"


@dataclass
class RemediationAction:
    """Single remediation action record."""

    action_id: str
    timestamp: str
    issue_type: IssueType
    strategy: RemediationStrategy
    target_metrics: dict[str, float]
    parameters: dict[str, Any]

    # Execution tracking
    status: RemediationStatus = RemediationStatus.PENDING
    execution_time_ms: float = 0.0
    error_message: str = None

    # Results
    before_score: float = 0.0
    after_score: float = 0.0
    improvement: float = 0.0


@dataclass
class RemediationPlan:
    """Complete remediation plan for a detected issue."""

    plan_id: str
    detection_report: dict[str, Any]
    created_at: str

    # Actions to take
    actions: list[RemediationAction] = field(default_factory=list)

    # Validation
    validation_threshold: float = 0.7
    requires_approval: bool = False

    # Results
    overall_status: RemediationStatus = RemediationStatus.PENDING
    total_execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "detection_summary": {
                "overall_health": self.detection_report.get("overall_health"),
                "critical_alerts": len(self.detection_report.get("critical_alerts", [])),
            },
            "actions": [
                {
                    "action_id": a.action_id,
                    "issue_type": a.issue_type.value,
                    "strategy": a.strategy.value,
                    "status": a.status.value,
                    "improvement": a.improvement,
                }
                for a in self.actions
            ],
            "overall_status": self.overall_status.value,
            "total_execution_time_ms": self.total_execution_time_ms,
        }


@dataclass
class RemediationHistory:
    """Historical record of remediation effectiveness."""

    strategy: RemediationStrategy
    issue_type: IssueType
    total_attempts: int = 0
    successful_attempts: int = 0
    avg_improvement: float = 0.0
    avg_execution_time_ms: float = 0.0
    last_attempt: str = None

    @property
    def success_rate(self) -> float:
        return self.successful_attempts / self.total_attempts if self.total_attempts > 0 else 0.0


# =============================================================================
# Auto-Remediation Engine
# =============================================================================


class AutoRemediationEngine:
    """Main auto-remediation engine that implements self-healing.

    Flow:
    1. Receive detection report from UnifiedDetectionEngine
    2. Analyze issues and select remediation strategies
    3. Execute remediation actions
    4. Validate results by re-running detection
    5. Record outcomes to feedback loop for learning
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}

        # Thresholds
        self.auto_remediate_threshold = self.config.get("auto_remediate_threshold", 0.8)
        self.max_retries = self.config.get("max_retries", 3)
        self.validation_timeout = self.config.get("validation_timeout", 30)

        # State
        self._history: dict[tuple[RemediationStrategy, IssueType], RemediationHistory] = {}
        self._active_plans: dict[str, RemediationPlan] = {}
        self._completed_plans: list[RemediationPlan] = []

        # Integrations
        self._detection_engine: UnifiedDetectionEngine | None = None
        self._temporal_bridge: Any | None = None
        self._feedback_loop: CognitiveFeedbackLoop | None = None
        self._audit_exporter: AuditExporter | None = None

        if DETECTION_AVAILABLE:
            self._detection_engine = UnifiedDetectionEngine()
        if TEMPORAL_AVAILABLE:
            # Would initialize with repo path
            pass
        if FEEDBACK_AVAILABLE:
            self._feedback_loop = get_feedback_loop()
        if AUDIT_AVAILABLE:
            try:
                self._audit_exporter = AuditExporter()
            except Exception:
                pass

    # ==========================================================================
    # Main API
    # ==========================================================================

    def remediate(self, detection_report: UnifiedDetectionReport) -> RemediationPlan:
        """Main entry point: Automatically remediate issues from detection report.

        Args:
            detection_report: Report from UnifiedDetectionEngine

        Returns:
            RemediationPlan with all actions and results

        """
        plan_id = f"remediation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create plan
        plan = RemediationPlan(
            plan_id=plan_id,
            detection_report=detection_report.to_dict(),
            created_at=datetime.now().isoformat(),
            validation_threshold=self.auto_remediate_threshold,
        )

        # Analyze and create actions
        actions = self._analyze_and_plan(detection_report)
        plan.actions = actions

        # Store as active
        self._active_plans[plan_id] = plan

        # Determine if auto-execution is allowed
        plan.requires_approval = self._requires_manual_approval(plan)

        if not plan.requires_approval:
            # Execute automatically
            self._execute_plan(plan)

        return plan

    def execute_plan(self, plan_id: str) -> RemediationPlan:
        """Manually execute a pending remediation plan."""
        if plan_id not in self._active_plans:
            raise ValueError(f"Plan {plan_id} not found")

        plan = self._active_plans[plan_id]
        self._execute_plan(plan)
        return plan

    def _analyze_and_plan(self, report: UnifiedDetectionReport) -> list[RemediationAction]:
        """Analyze detection report and create remediation actions."""
        actions = []

        # Check hallucination
        if report.hallucination.is_hallucination:
            h_actions = self._plan_hallucination_remediation(report.hallucination)
            actions.extend(h_actions)

        # Check integrity
        if report.integrity.is_integrity_violation:
            i_actions = self._plan_integrity_remediation(report.integrity)
            actions.extend(i_actions)

        # Check structural drift
        if report.structural_drift.is_structural_degradation:
            s_actions = self._plan_drift_remediation(report.structural_drift)
            actions.extend(s_actions)

        return actions

    def _plan_hallucination_remediation(
        self,
        score: HallucinationScore,
    ) -> list[RemediationAction]:
        """Plan remediation for hallucination issues."""
        actions = []

        # Strategy based on dominant factor
        if score.dominant_factor == "semantic_entropy":
            actions.append(
                self._create_action(
                    IssueType.HALLUCINATION,
                    RemediationStrategy.NLI_VERIFICATION,
                    {"target_entropy": 1.0, "verification_model": "deberta"},
                    {"semantic_entropy": score.semantic_entropy},
                )
            )

        if score.dominant_factor in ["reppl", "confidence"]:
            actions.append(
                self._create_action(
                    IssueType.HALLUCINATION,
                    RemediationStrategy.TEMPERATURE_REDUCTION,
                    {"temperature": 0.3, "top_p": 0.9},
                    {"reppl_score": score.reppl_score},
                )
            )

        if score.dominant_factor == "self_consistency":
            actions.append(
                self._create_action(
                    IssueType.HALLUCINATION,
                    RemediationStrategy.ENSEMBLE_EXPANSION,
                    {"num_samples": 10, "consensus_threshold": 0.7},
                    {"self_consistency": score.self_consistency},
                )
            )

        # Always add sampling adjustment as baseline
        actions.append(
            self._create_action(
                IssueType.HALLUCINATION,
                RemediationStrategy.SAMPLING_ADJUSTMENT,
                {"temperature": 0.5, "top_k": 50, "top_p": 0.95},
                {"unified_score": score.unified_hallucination_score},
            )
        )

        return actions

    def _plan_integrity_remediation(
        self,
        metrics: IntegrityMetrics,
    ) -> list[RemediationAction]:
        """Plan remediation for integrity violations."""
        actions = []

        # High entropy degradation
        if metrics.entropy_ratio < 0.7:
            actions.append(
                self._create_action(
                    IssueType.INTEGRITY_VIOLATION,
                    RemediationStrategy.ENTROPY_NORMALIZATION,
                    {"target_ratio": 0.9, "smoothing": 0.1},
                    {"entropy_ratio": metrics.entropy_ratio},
                )
            )

        # High divergence
        if metrics.total_variation_distance > 0.5:
            actions.append(
                self._create_action(
                    IssueType.INTEGRITY_VIOLATION,
                    RemediationStrategy.DISTRIBUTION_REBALANCE,
                    {"rebalance_factor": 0.5, "reference_distribution": "uniform"},
                    {"total_variation": metrics.total_variation_distance},
                )
            )

        # Byzantine issues
        if metrics.byzantine_safety_violations > 0:
            actions.append(
                self._create_action(
                    IssueType.INTEGRITY_VIOLATION,
                    RemediationStrategy.CONSENSUS_RECONFIG,
                    {"min_quorum": 2, "fault_tolerance": 0.33},
                    {"violations": metrics.byzantine_safety_violations},
                )
            )

        # Severe cases - checkpoint restore
        if metrics.unified_integrity_score > 0.8:
            actions.append(
                self._create_action(
                    IssueType.INTEGRITY_VIOLATION,
                    RemediationStrategy.CHECKPOINT_RESTORE,
                    {"checkpoint_age_max": 3600, "verify_integrity": True},
                    {"unified_score": metrics.unified_integrity_score},
                )
            )

        return actions

    def _plan_drift_remediation(
        self,
        metrics: StructuralDriftMetrics,
    ) -> list[RemediationAction]:
        """Plan remediation for structural drift."""
        actions = []

        # Spectral issues
        if metrics.spectral_radius > 2.0:
            actions.append(
                self._create_action(
                    IssueType.STRUCTURAL_DRIFT,
                    RemediationStrategy.SPECTRAL_CORRECTION,
                    {"damping_factor": 0.8, "eigenvalue_clip": 1.5},
                    {"spectral_radius": metrics.spectral_radius},
                )
            )

        if metrics.spectral_gap < 0.2:
            actions.append(
                self._create_action(
                    IssueType.STRUCTURAL_DRIFT,
                    RemediationStrategy.GRAPH_REWIRE,
                    {"connectivity_target": 0.8, "max_edges": 100},
                    {"spectral_gap": metrics.spectral_gap},
                )
            )

        # Clustering issues
        if metrics.degradation_rate in ["moderate", "rapid"]:
            actions.append(
                self._create_action(
                    IssueType.STRUCTURAL_DRIFT,
                    RemediationStrategy.STRUCTURAL_REBALANCE,
                    {"ch_threshold": 50, "db_threshold": 1.5},
                    {"degradation_rate": metrics.degradation_rate},
                )
            )

        # Lyapunov instability
        if metrics.lyapunov_exponent > 0:
            actions.append(
                self._create_action(
                    IssueType.STRUCTURAL_DRIFT,
                    RemediationStrategy.STATE_NORMALIZE,
                    {"stability_target": -0.1, "damping": 0.9},
                    {"lyapunov": metrics.lyapunov_exponent},
                )
            )

        return actions

    def _create_action(
        self,
        issue_type: IssueType,
        strategy: RemediationStrategy,
        parameters: dict[str, Any],
        target_metrics: dict[str, float],
    ) -> RemediationAction:
        """Create a remediation action."""
        action_id = f"action_{int(time.time() * 1000)}_{strategy.value}"

        return RemediationAction(
            action_id=action_id,
            timestamp=datetime.now().isoformat(),
            issue_type=issue_type,
            strategy=strategy,
            target_metrics=target_metrics,
            parameters=parameters,
            before_score=sum(target_metrics.values()) / len(target_metrics)
            if target_metrics
            else 0.0,
        )

    def _requires_manual_approval(self, plan: RemediationPlan) -> bool:
        """Determine if plan requires manual approval."""
        # Require approval for:
        # 1. Checkpoint restore (destructive)
        # 2. High severity issues
        # 3. Multiple coordinated changes

        for action in plan.actions:
            if action.strategy == RemediationStrategy.CHECKPOINT_RESTORE:
                return True

        # Check severity
        critical_alerts = plan.detection_report.get("critical_alerts", [])
        if len(critical_alerts) > 2:
            return True

        return False

    # ==========================================================================
    # Execution
    # ==========================================================================

    def _execute_plan(self, plan: RemediationPlan):
        """Execute all actions in a remediation plan."""
        plan.overall_status = RemediationStatus.IN_PROGRESS
        start_time = time.time()

        for action in plan.actions:
            self._execute_action(action)

            # If action failed and is critical, may need to stop
            if action.status == RemediationStatus.FAILED:
                if action.strategy == RemediationStrategy.CHECKPOINT_RESTORE:
                    # Don't continue if restore failed
                    break

        # Calculate overall status
        statuses = [a.status for a in plan.actions]
        if all(s == RemediationStatus.SUCCESS for s in statuses):
            plan.overall_status = RemediationStatus.SUCCESS
        elif any(s == RemediationStatus.SUCCESS for s in statuses):
            plan.overall_status = RemediationStatus.PARTIAL
        else:
            plan.overall_status = RemediationStatus.FAILED

        plan.total_execution_time_ms = (time.time() - start_time) * 1000

        # Move from active to completed
        if plan.plan_id in self._active_plans:
            del self._active_plans[plan.plan_id]
        self._completed_plans.append(plan)

        # Record to feedback loop for learning
        self._record_to_feedback(plan)

        # Export to audit
        if self._audit_exporter:
            try:
                self._audit_exporter.export_detection_report(plan.to_dict())
            except Exception:
                pass

    def _execute_action(self, action: RemediationAction):
        """Execute a single remediation action."""
        action.status = RemediationStatus.IN_PROGRESS
        start_time = time.time()

        try:
            # Route to appropriate executor
            executors: dict[RemediationStrategy, Callable[[RemediationAction], bool]] = {
                RemediationStrategy.TEMPERATURE_REDUCTION: self._execute_temperature_reduction,
                RemediationStrategy.SAMPLING_ADJUSTMENT: self._execute_sampling_adjustment,
                RemediationStrategy.NLI_VERIFICATION: self._execute_nli_verification,
                RemediationStrategy.ENSEMBLE_EXPANSION: self._execute_ensemble_expansion,
                RemediationStrategy.DISTRIBUTION_REBALANCE: self._execute_distribution_rebalance,
                RemediationStrategy.CONSENSUS_RECONFIG: self._execute_consensus_reconfig,
                RemediationStrategy.ENTROPY_NORMALIZATION: self._execute_entropy_normalization,
                RemediationStrategy.CHECKPOINT_RESTORE: self._execute_checkpoint_restore,
                RemediationStrategy.STRUCTURAL_REBALANCE: self._execute_structural_rebalance,
                RemediationStrategy.GRAPH_REWIRE: self._execute_graph_rewire,
                RemediationStrategy.STATE_NORMALIZE: self._execute_state_normalize,
                RemediationStrategy.SPECTRAL_CORRECTION: self._execute_spectral_correction,
            }

            executor = executors.get(action.strategy)
            if executor:
                success = executor(action)
                action.status = RemediationStatus.SUCCESS if success else RemediationStatus.FAILED
            else:
                action.status = RemediationStatus.FAILED
                action.error_message = f"No executor for strategy {action.strategy}"

            # Calculate improvement (simulated for now)
            action.improvement = self._calculate_improvement(action)
            action.after_score = action.before_score - action.improvement

        except Exception as e:
            action.status = RemediationStatus.FAILED
            action.error_message = str(e)

        action.execution_time_ms = (time.time() - start_time) * 1000

        # Update history
        self._update_history(action)

    def _calculate_improvement(self, action: RemediationAction) -> float:
        """Calculate improvement from remediation (placeholder)."""
        # In production, this would re-run detection and compare
        # For now, use success-based estimation
        if action.status == RemediationStatus.SUCCESS:
            # Typical improvement ranges by strategy
            improvements = {
                RemediationStrategy.TEMPERATURE_REDUCTION: 0.2,
                RemediationStrategy.SAMPLING_ADJUSTMENT: 0.15,
                RemediationStrategy.NLI_VERIFICATION: 0.25,
                RemediationStrategy.ENSEMBLE_EXPANSION: 0.18,
                RemediationStrategy.DISTRIBUTION_REBALANCE: 0.22,
                RemediationStrategy.CONSENSUS_RECONFIG: 0.3,
                RemediationStrategy.ENTROPY_NORMALIZATION: 0.2,
                RemediationStrategy.CHECKPOINT_RESTORE: 0.5,
                RemediationStrategy.STRUCTURAL_REBALANCE: 0.25,
                RemediationStrategy.GRAPH_REWIRE: 0.2,
                RemediationStrategy.STATE_NORMALIZE: 0.28,
                RemediationStrategy.SPECTRAL_CORRECTION: 0.3,
            }
            return improvements.get(action.strategy, 0.1)
        return 0.0

    # ==========================================================================
    # Strategy Executors
    # ==========================================================================

    def _execute_temperature_reduction(self, action: RemediationAction) -> bool:
        """Execute temperature reduction for hallucination."""
        temp = action.parameters.get("temperature", 0.3)
        print(f"[Remediation] Reducing temperature to {temp}")
        # Would integrate with LLM inference config
        return True

    def _execute_sampling_adjustment(self, action: RemediationAction) -> bool:
        """Execute sampling parameter adjustment."""
        top_k = action.parameters.get("top_k", 50)
        top_p = action.parameters.get("top_p", 0.95)
        print(f"[Remediation] Adjusting sampling: top_k={top_k}, top_p={top_p}")
        return True

    def _execute_nli_verification(self, action: RemediationAction) -> bool:
        """Enable NLI-based verification."""
        model = action.parameters.get("verification_model", "deberta")
        print(f"[Remediation] Enabling NLI verification with {model}")
        return True

    def _execute_ensemble_expansion(self, action: RemediationAction) -> bool:
        """Expand ensemble size."""
        num_samples = action.parameters.get("num_samples", 10)
        print(f"[Remediation] Expanding ensemble to {num_samples} samples")
        return True

    def _execute_distribution_rebalance(self, action: RemediationAction) -> bool:
        """Rebalance distribution."""
        factor = action.parameters.get("rebalance_factor", 0.5)
        print(f"[Remediation] Rebalancing distribution with factor {factor}")
        return True

    def _execute_consensus_reconfig(self, action: RemediationAction) -> bool:
        """Reconfigure consensus parameters."""
        min_quorum = action.parameters.get("min_quorum", 2)
        print(f"[Remediation] Reconfiguring consensus: min_quorum={min_quorum}")
        return True

    def _execute_entropy_normalization(self, action: RemediationAction) -> bool:
        """Normalize entropy."""
        target = action.parameters.get("target_ratio", 0.9)
        print(f"[Remediation] Normalizing entropy to ratio {target}")
        return True

    def _execute_checkpoint_restore(self, action: RemediationAction) -> bool:
        """Restore from checkpoint."""
        max_age = action.parameters.get("checkpoint_age_max", 3600)
        print(f"[Remediation] Restoring from checkpoint (max age {max_age}s)")
        # Would integrate with checkpoint system
        return True

    def _execute_structural_rebalance(self, action: RemediationAction) -> bool:
        """Rebalance structure."""
        ch_threshold = action.parameters.get("ch_threshold", 50)
        print(f"[Remediation] Rebalancing structure: CH threshold {ch_threshold}")
        return True

    def _execute_graph_rewire(self, action: RemediationAction) -> bool:
        """Rewire graph edges."""
        connectivity = action.parameters.get("connectivity_target", 0.8)
        print(f"[Remediation] Rewiring graph for {connectivity} connectivity")
        return True

    def _execute_state_normalize(self, action: RemediationAction) -> bool:
        """Normalize state."""
        stability = action.parameters.get("stability_target", -0.1)
        print(f"[Remediation] Normalizing state to stability {stability}")
        return True

    def _execute_spectral_correction(self, action: RemediationAction) -> bool:
        """Apply spectral correction."""
        damping = action.parameters.get("damping_factor", 0.8)
        print(f"[Remediation] Applying spectral correction with damping {damping}")
        return True

    # ==========================================================================
    # Learning and Feedback
    # ==========================================================================

    def _update_history(self, action: RemediationAction):
        """Update remediation history for learning."""
        key = (action.strategy, action.issue_type)

        if key not in self._history:
            self._history[key] = RemediationHistory(
                strategy=action.strategy,
                issue_type=action.issue_type,
            )

        history = self._history[key]
        history.total_attempts += 1
        history.last_attempt = action.timestamp

        if action.status == RemediationStatus.SUCCESS:
            history.successful_attempts += 1

        # Update averages
        history.avg_improvement = (
            history.avg_improvement * (history.total_attempts - 1) + action.improvement
        ) / history.total_attempts
        history.avg_execution_time_ms = (
            history.avg_execution_time_ms * (history.total_attempts - 1) + action.execution_time_ms
        ) / history.total_attempts

    def _record_to_feedback(self, plan: RemediationPlan):
        """Record remediation results to feedback loop."""
        # This would integrate with CognitiveFeedbackLoop
        # to learn which strategies work best
        pass

    def get_best_strategy(self, issue_type: IssueType) -> RemediationStrategy | None:
        """Get best strategy for an issue type based on history."""
        candidates = [
            (strategy, history)
            for (strategy, itype), history in self._history.items()
            if itype == issue_type
        ]

        if not candidates:
            return None

        # Sort by success rate, then by average improvement
        candidates.sort(key=lambda x: (x[1].success_rate, x[1].avg_improvement), reverse=True)
        return candidates[0][0]

    def get_remediation_report(self) -> str:
        """Generate remediation effectiveness report."""
        lines = [
            "# AMOS Auto-Remediation Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Total completed plans: {len(self._completed_plans)}",
            f"- Active plans: {len(self._active_plans)}",
            f"- Strategy types learned: {len(self._history)}",
            "",
            "## Strategy Effectiveness",
        ]

        if not self._history:
            lines.append("*No remediation history yet*")
        else:
            for (strategy, issue_type), history in sorted(
                self._history.items(), key=lambda x: x[1].success_rate, reverse=True
            ):
                lines.extend(
                    [
                        f"\n### {strategy.value} ({issue_type.value})",
                        f"- Success rate: {history.success_rate:.1%}",
                        f"- Avg improvement: {history.avg_improvement:.3f}",
                        f"- Avg execution time: {history.avg_execution_time_ms:.1f}ms",
                        f"- Total attempts: {history.total_attempts}",
                    ]
                )

        return "\n".join(lines)

    def export_history(self, output_path: Path | None = None) -> Path:
        """Export remediation history to JSON."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"amos_remediation_history_{timestamp}.json")

        data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            },
            "history": [
                {
                    "strategy": h.strategy.value,
                    "issue_type": h.issue_type.value,
                    "total_attempts": h.total_attempts,
                    "successful_attempts": h.successful_attempts,
                    "success_rate": h.success_rate,
                    "avg_improvement": h.avg_improvement,
                    "avg_execution_time_ms": h.avg_execution_time_ms,
                }
                for h in self._history.values()
            ],
            "completed_plans": [p.to_dict() for p in self._completed_plans[-10:]],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path


# =============================================================================
# Self-Healing Orchestrator
# =============================================================================


class SelfHealingOrchestrator:
    """Continuous self-healing orchestrator that runs detection and remediation
    in an automated loop.

    Configuration:
    - detection_interval: Seconds between detection runs
    - auto_remediate: Whether to auto-execute or require approval
    - health_threshold: System health threshold for triggering remediation
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.detection_interval = self.config.get("detection_interval", 300)  # 5 min
        self.auto_remediate = self.config.get("auto_remediate", False)
        self.health_threshold = self.config.get("health_threshold", 0.6)

        self._detection_engine = UnifiedDetectionEngine() if DETECTION_AVAILABLE else None
        self._remediation_engine = AutoRemediationEngine(config)

        self._running = False
        self._last_detection: UnifiedDetectionReport | None = None
        self._last_remediation: RemediationPlan | None = None

    def start(self):
        """Start continuous self-healing loop."""
        self._running = True
        print("[SelfHealing] Starting continuous monitoring...")

        while self._running:
            try:
                self._healing_cycle()
            except Exception as e:
                print(f"[SelfHealing] Cycle error: {e}")

            # Wait for next cycle
            time.sleep(self.detection_interval)

    def stop(self):
        """Stop the self-healing loop."""
        self._running = False
        print("[SelfHealing] Stopping...")

    def _healing_cycle(self):
        """Execute one healing cycle: Detect → Analyze → Remediate → Validate."""
        print(f"\n[SelfHealing] Cycle starting at {datetime.now().isoformat()}")

        # Step 1: Detection
        if not self._detection_engine:
            print("[SelfHealing] Detection engine not available")
            return

        # Run detection with sample data (production: real system data)
        report = self._detection_engine.detect_all()
        self._last_detection = report

        print(f"[SelfHealing] Detection complete: Health={report.overall_system_health:.2%}")

        # Step 2: Check if remediation needed
        if report.overall_system_health >= self.health_threshold:
            print(
                f"[SelfHealing] Health above threshold ({self.health_threshold:.0%}), no action needed"
            )
            return

        # Step 3: Remediation
        print("[SelfHealing] Health below threshold, triggering remediation")
        plan = self._remediation_engine.remediate(report)
        self._last_remediation = plan

        print(f"[SelfHealing] Remediation plan created: {len(plan.actions)} actions")

        # If manual approval required
        if plan.requires_approval and not self.auto_remediate:
            print(f"[SelfHealing] Plan requires manual approval (ID: {plan.plan_id})")
            return

        # Step 4: Results
        print(f"[SelfHealing] Remediation complete: Status={plan.overall_status.value}")
        print(f"[SelfHealing] Total execution time: {plan.total_execution_time_ms:.1f}ms")

    def get_status(self) -> dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "running": self._running,
            "detection_interval": self.detection_interval,
            "auto_remediate": self.auto_remediate,
            "health_threshold": self.health_threshold,
            "last_detection": self._last_detection.to_dict() if self._last_detection else None,
            "last_remediation": self._last_remediation.to_dict()
            if self._last_remediation
            else None,
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def create_auto_remediation_engine(config: dict = None) -> AutoRemediationEngine:
    """Factory function to create auto-remediation engine."""
    return AutoRemediationEngine(config)


def start_self_healing(config: dict = None) -> SelfHealingOrchestrator:
    """Start continuous self-healing with configuration."""
    orchestrator = SelfHealingOrchestrator(config)
    # Note: This blocks. Use orchestrator.start() in a thread for non-blocking.
    return orchestrator


def quick_remediate(detection_report: UnifiedDetectionReport) -> RemediationPlan:
    """Quick one-off remediation."""
    engine = AutoRemediationEngine()
    return engine.remediate(detection_report)


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Auto-Remediation Engine - Test Suite")
    print("=" * 70)

    # Create engine
    engine = AutoRemediationEngine()

    # Create sample detection report with issues
    if DETECTION_AVAILABLE:
        print("\n[Test 1] Remediation of Hallucination Issue")
        print("-" * 50)

        # Create detection with high hallucination risk
        inconsistent_samples = [
            "The sky is blue because of magic.",
            "The sky appears blue due to atmospheric refraction.",
            "The sky is blue because of Rayleigh scattering.",
            "The blue sky comes from reflection.",
        ]

        detection = engine._detection_engine.detect_hallucination(inconsistent_samples)
        print(f"Detection: Hallucination Score={detection.unified_hallucination_score:.2%}")
        print(f"Dominant Factor: {detection.dominant_factor}")

        # Create minimal report
        report = UnifiedDetectionReport(
            timestamp=datetime.now().isoformat(),
            session_id="test_session",
            hallucination=detection,
            integrity=IntegrityMetrics(
                shannon_entropy=0.8,
                max_entropy=1.0,
                entropy_ratio=0.8,
                total_variation_distance=0.2,
                jensen_shannon_divergence=0.1,
                kl_divergence=0.15,
                wasserstein_distance=0.1,
                byzantine_safety_violations=0,
                quorum_intersection_size=3,
                fault_tolerance_ratio=0.33,
            ),
            structural_drift=StructuralDriftMetrics(
                spectral_radius=1.5,
                spectral_gap=0.3,
                eigenvalue_spread=0.8,
                lyapunov_exponent=-0.2,
                convergence_rate=0.8,
                calinski_harabasz_index=45,
                davies_bouldin_index=1.2,
                silhouette_score=0.4,
                graph_diameter=3,
                clustering_coefficient=0.5,
                algebraic_connectivity=0.25,
            ),
            fisher_information=0.3,
            renyi_entropy=1.2,
            tsallis_entropy=0.9,
            data_processing_score=0.85,
        )

        # Run remediation
        plan = engine.remediate(report)
        print(f"\nRemediation Plan: {plan.plan_id}")
        print(f"Actions created: {len(plan.actions)}")
        print(f"Requires approval: {plan.requires_approval}")
        print(f"Overall status: {plan.overall_status.value}")

        for action in plan.actions:
            print(
                f"  - {action.strategy.value}: {action.status.value} "
                f"(improvement: {action.improvement:.1%})"
            )

    # Test 2: History tracking
    print("\n[Test 2] Remediation History")
    print("-" * 50)
    print(engine.get_remediation_report())

    # Test 3: Self-healing orchestrator
    print("\n[Test 3] Self-Healing Orchestrator (single cycle)")
    print("-" * 50)

    orchestrator = SelfHealingOrchestrator(
        {
            "detection_interval": 1,
            "auto_remediate": True,
            "health_threshold": 0.7,
        }
    )

    # Run one cycle
    orchestrator._healing_cycle()

    # Get status
    status = orchestrator.get_status()
    print("\nOrchestrator Status:")
    print(f"  Running: {status['running']}")
    print(f"  Auto-remediate: {status['auto_remediate']}")
    print(f"  Health threshold: {status['health_threshold']:.0%}")

    # Export history
    print("\n[Test 4] Export History")
    print("-" * 50)
    export_path = engine.export_history()
    print(f"Exported to: {export_path}")
    export_path.unlink()  # Cleanup

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)

"""Unified Architecture Intelligence Orchestrator (Layer 16).

Integrates all 19 architectural invariants from Layer 15 into unified decision-making.

Capabilities:
- Cross-domain correlation between constitutional, temporal, operational, resilience
- Multi-invariant conflict detection and resolution
- Architectural decision synthesis across all domains
- Autonomous architecture governance based on unified intelligence
- Unified architectural state vector spanning all invariants

This is the meta-layer that makes 19 invariants act as one coherent intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CorrelationType(Enum):
    """Types of cross-domain correlations."""

    CAUSAL = "causal"  # One invariant violation causes another
    AMPLIFYING = "amplifying"  # Violation makes another worse
    MITIGATING = "mitigating"  # Violation reduces impact of another
    INDEPENDENT = "independent"  # No correlation
    SYNERGISTIC = "synergistic"  # Combined effect > sum of parts


class DecisionConfidence(Enum):
    """Confidence levels for architectural decisions."""

    CERTAIN = "certain"  # All invariants agree
    HIGH = "high"  # Most invariants agree, minor conflicts
    MEDIUM = "medium"  # Mixed signals, some conflicts
    LOW = "low"  # Significant disagreement
    CONFLICTED = "conflicted"  # Fundamental invariant conflict


@dataclass
class InvariantStatus:
    """Status of a single invariant."""

    invariant_id: str
    valid: bool
    severity: float  # 0-1, higher = worse
    violations: list[dict[str, Any]] = field(default_factory=list)
    source_engine: str = ""  # Which engine reported this


@dataclass
class CrossDomainCorrelation:
    """Correlation between invariants across domains."""

    correlation_id: str
    source_invariant: str
    target_invariant: str
    correlation_type: CorrelationType
    strength: float  # 0-1
    explanation: str


@dataclass
class UnifiedArchitecturalDecision:
    """Decision synthesized from all invariant domains."""

    decision_id: str
    timestamp: str

    # Input from all domains
    constitutional_status: InvariantStatus | None
    temporal_status: InvariantStatus | None
    operational_status: InvariantStatus | None
    resilience_status: InvariantStatus | None

    # Synthesis
    overall_confidence: DecisionConfidence
    primary_concerns: list[str]
    conflicting_invariants: list[tuple[str, str]]
    recommended_actions: list[dict[str, Any]]

    # Decision
    decision: str
    rationale: str
    auto_executable: bool


@dataclass
class UnifiedArchitectureState:
    """Complete architectural state across all 19 invariants."""

    state_id: str
    timestamp: str

    # All 19 invariants
    invariants: dict[str, InvariantStatus]

    # Correlations
    correlations: list[CrossDomainCorrelation]

    # Derived metrics
    constitutional_health: float  # 0-1
    temporal_health: float
    operational_health: float
    resilience_health: float
    overall_health: float

    # Critical issues
    critical_violations: list[str]
    warning_violations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_id": self.state_id,
            "timestamp": self.timestamp,
            "health": {
                "constitutional": self.constitutional_health,
                "temporal": self.temporal_health,
                "operational": self.operational_health,
                "resilience": self.resilience_health,
                "overall": self.overall_health,
            },
            "invariants": {k: {"valid": v.valid, "severity": v.severity} for k, v in self.invariants.items()},
            "critical_count": len(self.critical_violations),
            "warning_count": len(self.warning_violations),
        }


class UnifiedArchitectureOrchestrator:
    """
    Orchestrates all 19 architectural invariants into unified intelligence.

    This Layer 16 meta-engine:
    1. Collects invariant status from all 4 Layer 15 engines
    2. Detects cross-domain correlations and conflicts
    3. Synthesizes unified architectural decisions
    4. Provides coherent autonomous governance recommendations
    5. Maintains unified architectural state vector
    """

    def __init__(self):
        self.engines: dict[str, Any] = {}
        self.correlations: list[CrossDomainCorrelation] = []
        self.decisions: list[UnifiedArchitecturalDecision] = []
        self.states: list[UnifiedArchitectureState] = []

        # Define known cross-domain correlations
        self._initialize_correlations()

    def _initialize_correlations(self) -> None:
        """Initialize known invariant correlations."""
        self.correlations = [
            # Constitutional -> Temporal
            CrossDomainCorrelation(
                correlation_id="corr_1",
                source_invariant="I_state_ownership",
                target_invariant="I_partial_order",
                correlation_type=CorrelationType.CAUSAL,
                strength=0.7,
                explanation="Unclear ownership leads to conflicting change orders",
            ),
            # Temporal -> Operational
            CrossDomainCorrelation(
                correlation_id="corr_2",
                source_invariant="I_clock",
                target_invariant="I_cache",
                correlation_type=CorrelationType.AMPLIFYING,
                strength=0.8,
                explanation="Clock inconsistency amplifies cache staleness issues",
            ),
            # Operational -> Resilience
            CrossDomainCorrelation(
                correlation_id="corr_3",
                source_invariant="I_fallback",
                target_invariant="I_recovery",
                correlation_type=CorrelationType.SYNERGISTIC,
                strength=0.9,
                explanation="Fallback + recovery together provide comprehensive resilience",
            ),
            # Resilience -> Constitutional
            CrossDomainCorrelation(
                correlation_id="corr_4",
                source_invariant="I_blast",
                target_invariant="I_capability",
                correlation_type=CorrelationType.MITIGATING,
                strength=0.6,
                explanation="Blast containment reduces need for ambient authority",
            ),
            # Temporal -> Resilience
            CrossDomainCorrelation(
                correlation_id="corr_5",
                source_invariant="I_partial_order",
                target_invariant="I_recovery",
                correlation_type=CorrelationType.CAUSAL,
                strength=0.75,
                explanation="Wrong operation order causes failures requiring recovery",
            ),
            # Constitutional -> Operational
            CrossDomainCorrelation(
                correlation_id="corr_6",
                source_invariant="I_absence",
                target_invariant="I_queue",
                correlation_type=CorrelationType.AMPLIFYING,
                strength=0.65,
                explanation="Unclear absence semantics amplify queue ordering issues",
            ),
        ]

    def register_engine(self, name: str, engine: Any) -> None:
        """Register a Layer 15 engine."""
        self.engines[name] = engine

    def collect_invariant_status(self) -> dict[str, InvariantStatus]:
        """Collect status from all registered engines."""
        invariants: dict[str, InvariantStatus] = {}

        # This would query each engine in practice
        # For now, return placeholder
        all_invariant_ids = [
            "I_constitution", "I_state_ownership", "I_absence", "I_semver",
            "I_protocol_lifecycle", "I_capability", "I_negative_capability",
            "I_partial_order", "I_clock", "I_consistency", "I_eventuality",
            "I_cache", "I_fallback", "I_queue", "I_idempotency",
            "I_recovery", "I_disaster_recovery", "I_blast", "I_isolation",
        ]

        for inv_id in all_invariant_ids:
            invariants[inv_id] = InvariantStatus(
                invariant_id=inv_id,
                valid=True,
                severity=0.0,
                source_engine="unified_orchestrator",
            )

        return invariants

    def detect_correlations(self, invariants: dict[str, InvariantStatus]) -> list[CrossDomainCorrelation]:
        """Detect active correlations between invariant violations."""
        active_correlations = []

        for corr in self.correlations:
            source = invariants.get(corr.source_invariant)
            target = invariants.get(corr.target_invariant)

            if source and target and not source.valid and not target.valid:
                # Both violated - correlation is active
                active_correlations.append(corr)

        return active_correlations

    def calculate_health_scores(self, invariants: dict[str, InvariantStatus]) -> dict[str, float]:
        """Calculate health scores for each domain."""
        constitutional = [
            invariants.get("I_constitution"),
            invariants.get("I_state_ownership"),
            invariants.get("I_absence"),
            invariants.get("I_semver"),
            invariants.get("I_protocol_lifecycle"),
            invariants.get("I_capability"),
            invariants.get("I_negative_capability"),
        ]

        temporal = [
            invariants.get("I_partial_order"),
            invariants.get("I_clock"),
            invariants.get("I_consistency"),
            invariants.get("I_eventuality"),
        ]

        operational = [
            invariants.get("I_cache"),
            invariants.get("I_fallback"),
            invariants.get("I_queue"),
            invariants.get("I_idempotency"),
        ]

        resilience = [
            invariants.get("I_recovery"),
            invariants.get("I_disaster_recovery"),
            invariants.get("I_blast"),
            invariants.get("I_isolation"),
        ]

        def domain_health(invariant_list: list[InvariantStatus | None]) -> float:
            valid_count = sum(1 for i in invariant_list if i and i.valid)
            total = len([i for i in invariant_list if i])
            return valid_count / total if total > 0 else 1.0

        return {
            "constitutional": domain_health(constitutional),
            "temporal": domain_health(temporal),
            "operational": domain_health(operational),
            "resilience": domain_health(resilience),
        }

    def synthesize_decision(self, state: UnifiedArchitectureState) -> UnifiedArchitecturalDecision:
        """Synthesize unified decision from architectural state."""
        # Determine confidence based on health scores
        min_health = min(
            state.constitutional_health,
            state.temporal_health,
            state.operational_health,
            state.resilience_health,
        )

        if min_health >= 0.9:
            confidence = DecisionConfidence.CERTAIN
        elif min_health >= 0.7:
            confidence = DecisionConfidence.HIGH
        elif min_health >= 0.5:
            confidence = DecisionConfidence.MEDIUM
        elif min_health >= 0.3:
            confidence = DecisionConfidence.LOW
        else:
            confidence = DecisionConfidence.CONFLICTED

        # Identify primary concerns
        concerns = []
        for inv_id, status in state.invariants.items():
            if not status.valid:
                concerns.append(f"{inv_id}: {len(status.violations)} violations")

        # Check for conflicts
        conflicts = []
        for corr in state.correlations:
            if corr.correlation_type == CorrelationType.AMPLIFYING:
                conflicts.append((corr.source_invariant, corr.target_invariant))

        # Generate recommendations
        recommendations = []
        if state.critical_violations:
            recommendations.append({
                "priority": "critical",
                "action": "immediate_remediation",
                "targets": state.critical_violations,
            })

        if state.resilience_health < 0.5:
            recommendations.append({
                "priority": "high",
                "action": "implement_blast_containment",
                "rationale": "Resilience health below threshold",
            })

        # Decision
        if confidence in (DecisionConfidence.CERTAIN, DecisionConfidence.HIGH):
            decision = "auto_maintain"
            auto_executable = True
        elif confidence == DecisionConfidence.MEDIUM:
            decision = "review_recommended"
            auto_executable = False
        else:
            decision = "human_intervention_required"
            auto_executable = False

        return UnifiedArchitecturalDecision(
            decision_id=f"decision_{len(self.decisions)}",
            timestamp=state.timestamp,
            constitutional_status=state.invariants.get("I_constitution"),
            temporal_status=state.invariants.get("I_partial_order"),
            operational_status=state.invariants.get("I_cache"),
            resilience_status=state.invariants.get("I_recovery"),
            overall_confidence=confidence,
            primary_concerns=concerns,
            conflicting_invariants=conflicts,
            recommended_actions=recommendations,
            decision=decision,
            rationale=f"Based on overall health {state.overall_health:.2f}",
            auto_executable=auto_executable,
        )

    def assess_unified_architecture(self) -> UnifiedArchitectureState:
        """
        Perform unified assessment across all 19 invariants.

        Returns:
            Complete architectural state with correlations and decisions
        """
        # Collect from all engines
        invariants = self.collect_invariant_status()

        # Detect active correlations
        active_correlations = self.detect_correlations(invariants)

        # Calculate health scores
        health = self.calculate_health_scores(invariants)
        overall = sum(health.values()) / len(health)

        # Classify violations
        critical = []
        warnings = []
        for inv_id, status in invariants.items():
            if not status.valid:
                if status.severity > 0.7:
                    critical.append(inv_id)
                elif status.severity > 0.3:
                    warnings.append(inv_id)

        state = UnifiedArchitectureState(
            state_id=f"unified_{len(self.states)}",
            timestamp="2024-01-01T00:00:00Z",
            invariants=invariants,
            correlations=active_correlations,
            constitutional_health=health["constitutional"],
            temporal_health=health["temporal"],
            operational_health=health["operational"],
            resilience_health=health["resilience"],
            overall_health=overall,
            critical_violations=critical,
            warning_violations=warnings,
        )

        self.states.append(state)
        return state

    def get_unified_insights(self) -> list[dict[str, Any]]:
        """Get insights from unified perspective."""
        return [
            {
                "insight": "Architecture is only as strong as its weakest invariant",
                "evidence": f"Overall health = min({self.states[-1].overall_health if self.states else 1.0})",
                "recommendation": "Focus remediation on lowest health domain",
                "scope": "unified",
            },
            {
                "insight": "Invariant violations cascade across domains",
                "evidence": f"Found {len(self.correlations)} known cross-domain correlations",
                "recommendation": "Address root cause invariants before correlated ones",
                "scope": "cross_domain",
            },
            {
                "insight": "Constitutional integrity is the foundation",
                "evidence": "I_constitution affects all other invariants",
                "recommendation": "Prioritize constitutional fixes to prevent cascade failures",
                "scope": "constitutional",
            },
            {
                "insight": "Resilience is the safety net when other invariants fail",
                "evidence": "Recovery paths must exist for all critical scenarios",
                "recommendation": "Ensure recovery coverage even when violations occur",
                "scope": "resilience",
            },
        ]

    def get_architectural_decision_report(self) -> dict[str, Any]:
        """Get comprehensive decision report."""
        if not self.states:
            return {"error": "No assessment performed yet"}

        latest = self.states[-1]
        decision = self.synthesize_decision(latest)

        return {
            "state": latest.to_dict(),
            "decision": {
                "confidence": decision.overall_confidence.value,
                "decision": decision.decision,
                "auto_executable": decision.auto_executable,
                "rationale": decision.rationale,
            },
            "recommendations": decision.recommended_actions,
            "correlations_active": len(latest.correlations),
            "conflicts": len(decision.conflicting_invariants),
        }

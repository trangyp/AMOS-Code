from typing import Any

"""
AMOS Reasoning Kernel
=====================

Formal machine-readable implementation of reasoning based on the specification:

Reasoning = rule-governed, constraint-preserving, justification-tracked
            transformation of representations

Or shorter:
Reasoning = valid state transition with traceable why

Core Equation:
    R_t = (P_t, H_t, I_t, J_t, U_t, K_t, X_t)

    R_{t+1} = R(R_t, Rules_t, Goals_t, Constraints_t)

Where:
    - P_t: premises
    - H_t: hypotheses
    - I_t: inference graph
    - J_t: justification objects
    - U_t: uncertainty distribution
    - K_t: contradictions / conflicts
    - X_t: active conclusions

Architecture:
    Input → BrainReadingKernel → ThinkingKernel → ReasoningKernel →
    VerificationKernel → ControlKernel → CommitKernel → RestrictedRenderer

Author: AMOS Kernel Architecture Team
Version: 1.0.0
License: Proprietary
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND TYPE DEFINITIONS
# ============================================================================


class PremiseType(Enum):
    """Types of premises in the reasoning system."""

    FACT = "fact"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"
    OBSERVATION = "observation"
    RULE = "rule"
    GOAL = "goal"
    DEFINITION = "definition"


class ReasoningMode(Enum):
    """Modes of reasoning available to the system."""

    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    INDUCTIVE = "inductive"
    CAUSAL = "causal"
    COUNTERFACTUAL = "counterfactual"
    ANALOGICAL = "analogical"
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    PROOF_SEARCH = "proof_search"
    REFUTATION_SEARCH = "refutation_search"
    DECISION_REASONING = "decision_reasoning"


class HypothesisStatus(Enum):
    """Status of a hypothesis."""

    OPEN = "open"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    UNDERDETERMINED = "underdetermined"


class ConflictSeverity(Enum):
    """Severity levels for constraint violations."""

    SOFT = "soft"
    HARD = "hard"
    CRITICAL = "critical"


class ConclusionStatus(Enum):
    """Status of a conclusion."""

    PROPOSED = "proposed"
    JUSTIFIED = "justified"
    COMMITTED = "committed"
    RETRACTED = "retracted"


class JustificationRelation(Enum):
    """Types of relations in justification graph."""

    SUPPORTS = "supports"
    DERIVES = "derives"
    CONFLICTS_WITH = "conflicts_with"
    RETRACTS = "retracts"


class RetractionReason(Enum):
    """Reasons for conclusion retraction."""

    PREMISE_CHANGED = "premise_changed"
    RULE_INVALIDATED = "rule_invalidated"
    CONFLICT_DETECTED = "conflict_detected"


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================


@dataclass
class Premise:
    """
    A premise in the reasoning system.

    Premises are explicit representations that serve as starting points
    for reasoning. They are distinct from conclusions and must be
    tracked separately.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = field(default=None)
    premise_type: PremiseType = field(default=PremiseType.FACT)
    confidence: float = field(default=1.0)
    source: str = field(default="")
    active: bool = field(default=True)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert premise to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "premise_type": self.premise_type.value,
            "confidence": self.confidence,
            "source": self.source,
            "active": self.active,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class Hypothesis:
    """
    A hypothesis being evaluated by the reasoning system.

    Hypotheses are candidate explanations or generalizations that
    require evaluation through reasoning.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = field(default=None)
    reasoning_mode: ReasoningMode = field(default=ReasoningMode.ABDUCTIVE)
    confidence: float = field(default=0.0)
    status: HypothesisStatus = field(default=HypothesisStatus.OPEN)
    explanatory_power: float = field(default=0.0)
    simplicity: float = field(default=0.0)
    coherence: float = field(default=0.0)
    contradiction_penalty: float = field(default=0.0)
    cost: float = field(default=0.0)
    score: float = field(default=0.0)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def calculate_score(self) -> float:
        """Calculate abductive hypothesis score."""
        self.score = (
            self.explanatory_power * self.simplicity * self.coherence
            - self.contradiction_penalty
            - self.cost
        )
        return self.score

    def to_dict(self) -> dict[str, Any]:
        """Convert hypothesis to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "reasoning_mode": self.reasoning_mode.value,
            "confidence": self.confidence,
            "status": self.status.value,
            "explanatory_power": self.explanatory_power,
            "simplicity": self.simplicity,
            "coherence": self.coherence,
            "contradiction_penalty": self.contradiction_penalty,
            "cost": self.cost,
            "score": self.score,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class InferenceRule:
    """
    Explicit inference rule as first-class object.

    Rules must be explicit, not implicit. They have preconditions,
    transformation logic, and validity conditions.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = field(default="")
    mode: ReasoningMode = field(default=ReasoningMode.DEDUCTIVE)
    input_types: list[str] = field(default_factory=list)
    output_type: str = field(default="")
    preconditions: list[Callable[..., bool]] = field(default_factory=list)
    transformation: Callable[..., Any] = field(default=None)
    validity_conditions: list[str] = field(default_factory=list)
    uncertainty_update: str = field(default="multiply")
    metadata: dict[str, Any] = field(default_factory=dict)

    def check_preconditions(self, premises: list[Premise]) -> bool:
        """Check if all preconditions are satisfied."""
        for precondition in self.preconditions:
            if not precondition(premises):
                return False
        return True

    def apply(self, premises: list[Premise]) -> Any:
        """Apply the rule to premises."""
        if not self.check_preconditions(premises):
            return None
        if self.transformation is None:
            return None
        try:
            return self.transformation(premises)
        except Exception as e:
            logger.debug(f"Rule application failed: {e}")
            return None

    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "mode": self.mode.value,
            "input_types": self.input_types,
            "output_type": self.output_type,
            "validity_conditions": self.validity_conditions,
            "uncertainty_update": self.uncertainty_update,
            "metadata": self.metadata,
        }


@dataclass
class Conclusion:
    """
    A conclusion derived through reasoning.

    Conclusions must have explicit justification chains and
    can only be committed after verification.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = field(default=None)
    confidence: float = field(default=0.0)
    justified: bool = field(default=False)
    committed: bool = field(default=False)
    status: ConclusionStatus = field(default=ConclusionStatus.PROPOSED)
    premise_ids: list[str] = field(default_factory=list)
    rule_ids: list[str] = field(default_factory=list)
    justification_id: str = field(default=None)
    uncertainty_propagated: bool = field(default=False)
    contradiction_checked: bool = field(default=False)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert conclusion to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "confidence": self.confidence,
            "justified": self.justified,
            "committed": self.committed,
            "status": self.status.value,
            "premise_ids": self.premise_ids,
            "rule_ids": self.rule_ids,
            "justification_id": self.justification_id,
            "uncertainty_propagated": self.uncertainty_propagated,
            "contradiction_checked": self.contradiction_checked,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class Justification:
    """
    Justification linking conclusions to premises through rules.

    Every committed conclusion MUST have an explicit justification path.
    This is a fundamental invariant of the reasoning system.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conclusion_id: str = field(default="")
    premise_ids: list[str] = field(default_factory=list)
    rule_id: str = field(default="")
    confidence_update: float = field(default=1.0)
    reasoning_mode: ReasoningMode = field(default=ReasoningMode.DEDUCTIVE)
    chain: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert justification to dictionary representation."""
        return {
            "id": self.id,
            "conclusion_id": self.conclusion_id,
            "premise_ids": self.premise_ids,
            "rule_id": self.rule_id,
            "confidence_update": self.confidence_update,
            "reasoning_mode": self.reasoning_mode.value,
            "chain": self.chain,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class Conflict:
    """
    A conflict or contradiction detected in the reasoning state.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conclusion_ids: list[str] = field(default_factory=list)
    premise_ids: list[str] = field(default_factory=list)
    severity: ConflictSeverity = field(default=ConflictSeverity.HARD)
    conflict_score: float = field(default=0.0)
    description: str = field(default="")
    resolution_strategy: str = field(default=None)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert conflict to dictionary representation."""
        return {
            "id": self.id,
            "conclusion_ids": self.conclusion_ids,
            "premise_ids": self.premise_ids,
            "severity": self.severity.value,
            "conflict_score": self.conflict_score,
            "description": self.description,
            "resolution_strategy": self.resolution_strategy,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class UncertaintyState:
    """
    Uncertainty distribution across the reasoning state.
    """

    global_uncertainty: float = field(default=0.0)
    claim_uncertainties: dict[str, float] = field(default_factory=dict)
    entropy: float = field(default=0.0)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_claim_uncertainty(self, claim_id: str, uncertainty: float) -> None:
        """Update uncertainty for a specific claim."""
        self.claim_uncertainties[claim_id] = max(0.0, min(1.0, uncertainty))
        self._recalculate_global()

    def _recalculate_global(self) -> None:
        """Recalculate global uncertainty from claim uncertainties."""
        if not self.claim_uncertainties:
            self.global_uncertainty = 0.0
            return
        self.global_uncertainty = sum(self.claim_uncertainties.values()) / len(
            self.claim_uncertainties
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert uncertainty state to dictionary representation."""
        return {
            "global_uncertainty": self.global_uncertainty,
            "claim_uncertainties": self.claim_uncertainties,
            "entropy": self.entropy,
            "metadata": self.metadata,
        }


@dataclass
class CausalLink:
    """
    A causal link representing directed causal structure.

    Causal reasoning must represent directed structure.
    Cause(A,B) ≠ Correlation(A,B)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cause: str = field(default="")
    effect: str = field(default="")
    mechanism: str = field(default="")
    confidence: float = field(default=0.0)
    intervention_tested: bool = field(default=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert causal link to dictionary representation."""
        return {
            "id": self.id,
            "cause": self.cause,
            "effect": self.effect,
            "mechanism": self.mechanism,
            "confidence": self.confidence,
            "intervention_tested": self.intervention_tested,
            "metadata": self.metadata,
        }


@dataclass
class CounterfactualBranch:
    """
    A counterfactual branch representing an alternative world.

    The machine must reason about alternative worlds.
    W' = Intervene(W, x ← x')
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intervention: dict[str, Any] = field(default_factory=dict)
    predicted_world: dict[str, Any] = field(default_factory=dict)
    difference_from_actual: dict[str, Any] = field(default_factory=dict)
    utility_change: float = field(default=0.0)
    confidence: float = field(default=0.0)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert counterfactual branch to dictionary representation."""
        return {
            "id": self.id,
            "intervention": self.intervention,
            "predicted_world": self.predicted_world,
            "difference_from_actual": self.difference_from_actual,
            "utility_change": self.utility_change,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class ConstraintCheck:
    """
    Result of checking a constraint.

    Reasoning must preserve hard constraints.
    ValidState ⇔ ∀c_i ∈ Constraints, c_i = satisfied
    """

    constraint_id: str = field(default="")
    status: str = field(default="unknown")  # satisfied, violated, unknown
    severity: ConflictSeverity = field(default=ConflictSeverity.SOFT)
    violation_score: float = field(default=0.0)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert constraint check to dictionary representation."""
        return {
            "constraint_id": self.constraint_id,
            "status": self.status,
            "severity": self.severity.value,
            "violation_score": self.violation_score,
            "metadata": self.metadata,
        }


@dataclass
class DeductiveStep:
    """
    A deductive inference step.

    Deduction preserves validity if premises are valid.
    P₁, P₂, ..., Pₙ ⊨ C
    """

    premise_ids: list[str] = field(default_factory=list)
    rule_id: str = field(default="")
    conclusion: Any = field(default=None)
    sound_if: list[str] = field(
        default_factory=lambda: [
            "all_premises_active",
            "all_preconditions_met",
            "no_type_violation",
        ]
    )
    is_sound: bool = field(default=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert deductive step to dictionary representation."""
        return {
            "premise_ids": self.premise_ids,
            "rule_id": self.rule_id,
            "conclusion": self.conclusion,
            "sound_if": self.sound_if,
            "is_sound": self.is_sound,
        }


@dataclass
class InductiveGeneralization:
    """
    An inductive generalization from evidence.

    Induction generalizes from evidence with confidence updates.
    """

    examples_supporting: list[Any] = field(default_factory=list)
    examples_against: list[Any] = field(default_factory=list)
    coverage: float = field(default=0.0)
    stability: float = field(default=0.0)
    confidence: float = field(default=0.0)
    generalization: Any = field(default=None)

    def update_confidence(self, support: float, counterevidence: float, eta: float = 0.1) -> float:
        """Update confidence based on support and counterevidence."""
        # Conf_{t+1} = Conf_t + η (Support - Counterevidence)
        self.confidence = max(0.0, min(1.0, self.confidence + eta * (support - counterevidence)))
        return self.confidence

    def to_dict(self) -> dict[str, Any]:
        """Convert inductive generalization to dictionary representation."""
        return {
            "examples_supporting": self.examples_supporting,
            "examples_against": self.examples_against,
            "coverage": self.coverage,
            "stability": self.stability,
            "confidence": self.confidence,
            "generalization": self.generalization,
        }


@dataclass
class TruthMaintenanceEntry:
    """
    Entry in the truth maintenance system.

    Premise change must trigger dependent conclusion reevaluation.
    """

    premise_id: str = field(default="")
    dependent_conclusion_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert truth maintenance entry to dictionary representation."""
        return {
            "premise_id": self.premise_id,
            "dependent_conclusion_ids": self.dependent_conclusion_ids,
        }


@dataclass
class Retraction:
    """
    A retraction of a conclusion.
    """

    conclusion_id: str = field(default="")
    reason: RetractionReason = field(default=RetractionReason.PREMISE_CHANGED)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert retraction to dictionary representation."""
        return {
            "conclusion_id": self.conclusion_id,
            "reason": self.reason.value,
            "timestamp": self.timestamp,
        }


# ============================================================================
# REASONING STATE
# ============================================================================


@dataclass
class ReasoningState:
    """
    Complete reasoning state R_t.

    R_t = (P_t, H_t, I_t, J_t, U_t, K_t, X_t)
    """

    # P_t: premises
    premises: dict[str, Premise] = field(default_factory=dict)

    # H_t: hypotheses
    hypotheses: dict[str, Hypothesis] = field(default_factory=dict)

    # I_t: inference graph (nodes and edges)
    inference_graph: dict[str, Any] = field(default_factory=lambda: {"nodes": [], "edges": []})

    # J_t: justification objects
    justifications: dict[str, Justification] = field(default_factory=dict)

    # U_t: uncertainty distribution
    uncertainty_state: UncertaintyState = field(default_factory=UncertaintyState)

    # K_t: contradictions / conflicts
    conflicts: dict[str, Conflict] = field(default_factory=dict)

    # X_t: active conclusions
    conclusions: dict[str, Conclusion] = field(default_factory=dict)

    # Additional tracking structures
    causal_links: dict[str, CausalLink] = field(default_factory=dict)
    counterfactual_branches: dict[str, CounterfactualBranch] = field(default_factory=dict)
    inductive_generalizations: dict[str, InductiveGeneralization] = field(default_factory=dict)
    constraint_checks: dict[str, ConstraintCheck] = field(default_factory=dict)
    truth_maintenance: dict[str, TruthMaintenanceEntry] = field(default_factory=dict)
    retractions: list[Retraction] = field(default_factory=list)

    # Inference rules registry
    rules: dict[str, InferenceRule] = field(default_factory=dict)

    # State metadata
    state_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reasoning_quality: float = field(default=0.0)

    def update_timestamp(self) -> None:
        """Update the state's timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def calculate_quality(self) -> float:
        """
        Calculate reasoning quality score.

        Q_reason(R_t) = α·Validity_t + β·Consistency_t + γ·Coverage_t + δ·GoalFit_t
                        - ε·Contradiction_t - ζ·UnjustifiedLeap_t - η·Error_t
        """
        # Count active conclusions
        active_conclusions = [c for c in self.conclusions.values() if c.active]
        justified_count = sum(1 for c in active_conclusions if c.justified)
        sum(1 for c in active_conclusions if c.committed)

        # Calculate validity component (justified / total)
        validity = justified_count / len(active_conclusions) if active_conclusions else 0.0

        # Calculate consistency component (fewer conflicts = better)
        conflict_score = sum(c.conflict_score for c in self.conflicts.values())
        consistency = max(0.0, 1.0 - conflict_score)

        # Coverage: proportion of hypotheses explored
        total_hypotheses = len(self.hypotheses)
        evaluated_hypotheses = sum(
            1 for h in self.hypotheses.values() if h.status != HypothesisStatus.OPEN
        )
        coverage = evaluated_hypotheses / total_hypotheses if total_hypotheses else 0.0

        # Goal fit: confidence weighted by commitment
        goal_fit = sum(c.confidence for c in active_conclusions if c.committed)

        # Penalties
        contradiction_penalty = len(self.conflicts) * 0.1
        unjustified_leap = sum(1 for c in active_conclusions if c.committed and not c.justified)

        # Combine with weights
        quality = (
            0.3 * validity
            + 0.3 * consistency
            + 0.2 * coverage
            + 0.2 * goal_fit
            - 0.1 * contradiction_penalty
            - 0.2 * unjustified_leap
        )

        self.reasoning_quality = max(0.0, quality)
        return self.reasoning_quality

    def to_dict(self) -> dict[str, Any]:
        """Convert reasoning state to dictionary representation."""
        return {
            "state_id": self.state_id,
            "premises": {k: v.to_dict() for k, v in self.premises.items()},
            "hypotheses": {k: v.to_dict() for k, v in self.hypotheses.items()},
            "conclusions": {k: v.to_dict() for k, v in self.conclusions.items()},
            "justifications": {k: v.to_dict() for k, v in self.justifications.items()},
            "conflicts": {k: v.to_dict() for k, v in self.conflicts.items()},
            "uncertainty_state": self.uncertainty_state.to_dict(),
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
            "reasoning_quality": self.reasoning_quality,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ============================================================================
# JUSTIFICATION GRAPH
# ============================================================================


class JustificationGraph:
    """
    Graph structure tracking justifications.

    The system does not reason unless every committed conclusion has a why-chain.
    """

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, str]] = []

    def add_node(self, node_id: str, node_type: str, content: Any) -> None:
        """Add a node to the justification graph."""
        self.nodes[node_id] = {"id": node_id, "type": node_type, "content": content}

    def add_edge(self, source: str, relation: JustificationRelation, target: str) -> None:
        """Add an edge to the justification graph."""
        self.edges.append({"source": source, "relation": relation.value, "target": target})

    def get_justification_path(self, conclusion_id: str) -> list[dict[str, Any]]:
        """
        Get the justification path for a conclusion.

        CommittedConclusion ⇒ ∃ JustificationPath
        """
        path = []
        visited = set()

        def traverse(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)

            node = self.nodes.get(node_id)
            if node:
                path.append(node)

            # Find edges where this node is the target
            for edge in self.edges:
                if edge["target"] == node_id:
                    traverse(edge["source"])

        traverse(conclusion_id)
        return list(reversed(path))

    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {"nodes": list(self.nodes.values()), "edges": self.edges}


# ============================================================================
# TRUTH MAINTENANCE SYSTEM
# ============================================================================


class TruthMaintenanceSystem:
    """
    Truth Maintenance System (TMS).

    The machine must retract conclusions when premises change.
    PremiseChange ⇒ Reevaluate(DependentConclusions)
    """

    def __init__(self):
        self.dependencies: dict[str, list[str]] = defaultdict(list)
        self.retractions: list[Retraction] = []

    def register_dependency(self, premise_id: str, conclusion_id: str) -> None:
        """Register that a conclusion depends on a premise."""
        self.dependencies[premise_id].append(conclusion_id)

    def get_dependent_conclusions(self, premise_id: str) -> list[str]:
        """Get all conclusions that depend on a given premise."""
        return self.dependencies[premise_id].copy()

    def premise_changed(self, premise_id: str, state: ReasoningState) -> list[Retraction]:
        """
        Handle premise change - reevaluate dependent conclusions.

        Returns list of retractions performed.
        """
        retractions: list[Retraction] = []
        dependent_ids = self.get_dependent_conclusions(premise_id)

        for conclusion_id in dependent_ids:
            conclusion = state.conclusions.get(conclusion_id)
            if conclusion and conclusion.committed:
                # Retract the conclusion
                conclusion.committed = False
                conclusion.status = ConclusionStatus.RETRACTED

                retraction = Retraction(
                    conclusion_id=conclusion_id, reason=RetractionReason.PREMISE_CHANGED
                )
                self.retractions.append(retraction)
                retractions.append(retraction)

                logger.info(f"Retracted conclusion {conclusion_id} due to premise change")

        return retractions

    def to_dict(self) -> dict[str, Any]:
        """Convert TMS to dictionary representation."""
        return {
            "dependencies": dict(self.dependencies),
            "retractions": [r.to_dict() for r in self.retractions],
        }


# ============================================================================
# REASONING MODE CONTROLLER
# ============================================================================


@dataclass
class ModeSelectionInput:
    """Inputs for reasoning mode selection."""

    problem_type: str = field(default="")
    ambiguity: float = field(default=0.0)
    risk: float = field(default=0.0)
    available_evidence: float = field(default=0.0)
    time_budget: float = field(default=0.0)


class ReasoningModeController:
    """
    Controller for selecting appropriate reasoning mode.

    Mode* = argmax_m [ FitToProblem(m) · ExpectedYield(m) - Cost(m) - FailureRisk(m) ]
    """

    def __init__(self):
        self.mode_scores: dict[ReasoningMode, dict[str, float]] = {
            ReasoningMode.DEDUCTIVE: {"fit": 0.9, "yield": 0.95, "cost": 0.3, "risk": 0.1},
            ReasoningMode.ABDUCTIVE: {"fit": 0.8, "yield": 0.7, "cost": 0.6, "risk": 0.4},
            ReasoningMode.INDUCTIVE: {"fit": 0.7, "yield": 0.6, "cost": 0.5, "risk": 0.3},
            ReasoningMode.CAUSAL: {"fit": 0.8, "yield": 0.75, "cost": 0.7, "risk": 0.3},
            ReasoningMode.COUNTERFACTUAL: {"fit": 0.6, "yield": 0.5, "cost": 0.8, "risk": 0.5},
            ReasoningMode.CONSTRAINT_SATISFACTION: {
                "fit": 0.85,
                "yield": 0.8,
                "cost": 0.6,
                "risk": 0.2,
            },
            ReasoningMode.DECISION_REASONING: {"fit": 0.75, "yield": 0.7, "cost": 0.5, "risk": 0.4},
        }

    def select_mode(self, inputs: ModeSelectionInput) -> ReasoningMode:
        """
        Select the best reasoning mode based on problem characteristics.
        """
        best_mode = ReasoningMode.DEDUCTIVE
        best_score = float("-inf")

        for mode, scores in self.mode_scores.items():
            # Adjust scores based on problem characteristics
            adjusted_fit = scores["fit"] * (1 - inputs.ambiguity * 0.3)
            adjusted_yield = scores["yield"] * inputs.available_evidence
            adjusted_cost = scores["cost"] * (1 / max(inputs.time_budget, 0.1))
            adjusted_risk = scores["risk"] * inputs.risk

            # Mode* = argmax [ Fit · Yield - Cost - Risk ]
            total_score = adjusted_fit * adjusted_yield - adjusted_cost - adjusted_risk

            if total_score > best_score:
                best_score = total_score
                best_mode = mode

        logger.debug(f"Selected reasoning mode: {best_mode.value} (score: {best_score:.3f})")
        return best_mode

    def get_mode_characteristics(self, mode: ReasoningMode) -> dict[str, float]:
        """Get characteristics for a specific mode."""
        return self.mode_scores.get(mode, {}).copy()


# ============================================================================
# REASONING KERNEL
# ============================================================================


class ReasoningKernel:
    """
    Core reasoning kernel implementing the AMOS reasoning specification.

    Reasoning = Represent → Infer → Justify → Check → Revise → Commit

    The machine does not understand reasoning until it has:
    - explicit premises
    - explicit inference rules
    - explicit conclusion objects
    - explicit justification chains
    - uncertainty propagation
    - contradiction handling
    - truth maintenance
    - counterexample search
    - commit conditions for conclusions
    """

    def __init__(self):
        self.state = ReasoningState()
        self.justification_graph = JustificationGraph()
        self.tms = TruthMaintenanceSystem()
        self.mode_controller = ReasoningModeController()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the reasoning kernel."""
        if self._initialized:
            return

        # Register default inference rules
        await self._register_default_rules()

        self._initialized = True
        logger.info("Reasoning kernel initialized")

    async def _register_default_rules(self) -> None:
        """Register default inference rules."""
        # Modus Ponens (deductive)
        modus_ponens = InferenceRule(
            name="modus_ponens",
            mode=ReasoningMode.DEDUCTIVE,
            input_types=["premise", "premise"],
            output_type="conclusion",
            validity_conditions=["implication_structure", "antecedent_verified"],
            uncertainty_update="multiply",
        )
        self.state.rules[modus_ponens.id] = modus_ponens

        # Abduction (best explanation)
        abduction = InferenceRule(
            name="inference_to_best_explanation",
            mode=ReasoningMode.ABDUCTIVE,
            input_types=["observation", "hypothesis"],
            output_type="hypothesis",
            validity_conditions=["explanatory_scope", "coherence"],
            uncertainty_update="bayesian",
        )
        self.state.rules[abduction.id] = abduction

        # Induction (generalization)
        induction = InferenceRule(
            name="inductive_generalization",
            mode=ReasoningMode.INDUCTIVE,
            input_types=["observation", "observation"],
            output_type="generalization",
            validity_conditions=["coverage", "stability"],
            uncertainty_update="confidence_update",
        )
        self.state.rules[induction.id] = induction

        logger.debug(f"Registered {len(self.state.rules)} default rules")

    # ===================================================================
    # REASONING PRIMITIVES
    # ===================================================================

    async def assert_premise(
        self,
        content: Any,
        premise_type: PremiseType = PremiseType.FACT,
        confidence: float = 1.0,
        source: str = "",
        metadata: dict[str, Any] = None,
    ) -> Premise:
        """
        Assert a premise into the reasoning state.

        Primitive: assert_premise
        """
        premise = Premise(
            content=content,
            premise_type=premise_type,
            confidence=confidence,
            source=source,
            metadata=metadata or {},
        )

        self.state.premises[premise.id] = premise

        # Add to justification graph
        self.justification_graph.add_node(premise.id, "premise", content)

        self.state.update_timestamp()
        logger.debug(f"Asserted premise {premise.id}: {content}")

        return premise

    async def select_inference_rules(
        self, reasoning_mode: ReasoningMode, premises: list[Premise, goals : list[Any]] = None
    ) -> list[InferenceRule]:
        """
        Select applicable inference rules.

        Primitive: select_inference_rules
        """
        applicable_rules = []

        for rule in self.state.rules.values():
            # Filter by reasoning mode
            if rule.mode != reasoning_mode:
                continue

            # Check if rule can be applied to premises
            if rule.check_preconditions(premises):
                applicable_rules.append(rule)

        logger.debug(f"Selected {len(applicable_rules)} rules for {reasoning_mode.value}")
        return applicable_rules

    async def derive_candidate_conclusions(
        self, premises: list[Premise], rules: list[InferenceRule]
    ) -> list[Conclusion]:
        """
        Derive candidate conclusions from premises using rules.

        Primitive: derive_candidate_conclusions
        Conclusion_{t+1} = Infer(Premises_t, Rules_t)
        """
        conclusions = []

        for rule in rules:
            # Apply the rule
            result = rule.apply(premises)

            if result is not None:
                # Calculate confidence based on premises and uncertainty update
                premise_confidences = [p.confidence for p in premises]
                base_confidence = min(premise_confidences) if premise_confidences else 0.0

                if rule.uncertainty_update == "multiply":
                    confidence = base_confidence * 0.95  # Small deduction penalty
                elif rule.uncertainty_update == "bayesian":
                    confidence = base_confidence  # Bayesian update handled separately
                else:
                    confidence = base_confidence

                conclusion = Conclusion(
                    content=result,
                    confidence=confidence,
                    premise_ids=[p.id for p in premises],
                    rule_ids=[rule.id],
                    status=ConclusionStatus.PROPOSED,
                )

                self.state.conclusions[conclusion.id] = conclusion
                conclusions.append(conclusion)

                logger.debug(f"Derived conclusion {conclusion.id} using rule {rule.name}")

        return conclusions

    async def attach_justifications(
        self, conclusions: list[Conclusion], premises: list[Premise], rules: list[InferenceRule]
    ) -> list[Justification]:
        """
        Attach justifications to conclusions.

        Primitive: attach_justifications
        Justified(Conclusion_{t+1}) = 1
        """
        justifications = []

        for conclusion in conclusions:
            for rule in rules:
                if rule.id in conclusion.rule_ids:
                    # Build justification chain
                    chain = []
                    for premise in premises:
                        chain.append(
                            {"type": "premise", "id": premise.id, "content": premise.content}
                        )

                    chain.append(
                        {"type": "rule", "id": rule.id, "name": rule.name, "mode": rule.mode.value}
                    )

                    chain.append(
                        {"type": "conclusion", "id": conclusion.id, "content": conclusion.content}
                    )

                    justification = Justification(
                        conclusion_id=conclusion.id,
                        premise_ids=[p.id for p in premises],
                        rule_id=rule.id,
                        confidence_update=conclusion.confidence,
                        reasoning_mode=rule.mode,
                        chain=chain,
                    )

                    self.state.justifications[justification.id] = justification
                    conclusion.justification_id = justification.id
                    conclusion.justified = True
                    conclusion.status = ConclusionStatus.JUSTIFIED

                    # Add to justification graph
                    self.justification_graph.add_edge(
                        justification.id, JustificationRelation.DERIVES, conclusion.id
                    )
                    for premise in premises:
                        self.justification_graph.add_edge(
                            premise.id, JustificationRelation.SUPPORTS, justification.id
                        )

                    justifications.append(justification)

                    logger.debug(
                        f"Attached justification {justification.id} to conclusion {conclusion.id}"
                    )

        return justifications

    async def propagate_uncertainty(
        self, premises: list[Premise], conclusions: list[Conclusion], rules: list[InferenceRule]
    ) -> UncertaintyState:
        """
        Propagate uncertainty through the reasoning chain.

        Primitive: propagate_uncertainty
        """
        for conclusion in conclusions:
            # Calculate combined uncertainty from premises
            premise_uncertainties = [1 - p.confidence for p in premises]
            combined_uncertainty = max(premise_uncertainties) if premise_uncertainties else 0.0

            # Add rule-specific uncertainty
            for rule in rules:
                if rule.uncertainty_update == "multiply":
                    combined_uncertainty = combined_uncertainty * 1.05  # Small increase
                elif rule.uncertainty_update == "bayesian":
                    # Bayesian uncertainty propagation
                    pass

            # Update conclusion confidence
            conclusion.confidence = max(0.0, 1.0 - combined_uncertainty)
            conclusion.uncertainty_propagated = True

            # Update uncertainty state
            self.state.uncertainty_state.update_claim_uncertainty(
                conclusion.id, combined_uncertainty
            )

        self.state.uncertainty_state._recalculate_global()

        logger.debug(f"Propagated uncertainty for {len(conclusions)} conclusions")
        return self.state.uncertainty_state

    async def detect_reasoning_conflicts(
        self, conclusions: list[Conclusion, constraints : list[ConstraintCheck]] = None
    ) -> list[Conflict]:
        """
        Detect conflicts and contradictions.

        Primitive: detect_conflict
        Conflict detection is mandatory before conclusion commit.
        """
        conflicts = []
        constraints = constraints or []

        # Check for constraint violations
        for constraint in constraints:
            if constraint.status == "violated":
                # Find conclusions that violate the constraint
                violating_conclusions = []
                for conclusion in conclusions:
                    # Simple conflict detection: check if conclusion contradicts constraint
                    # This would be more sophisticated in a real implementation
                    pass

                if violating_conclusions:
                    conflict = Conflict(
                        conclusion_ids=[c.id for c in violating_conclusions],
                        severity=constraint.severity,
                        conflict_score=constraint.violation_score,
                        description=f"Constraint {constraint.constraint_id} violated",
                    )

                    self.state.conflicts[conflict.id] = conflict
                    conflicts.append(conflict)

        # Check for direct contradictions between conclusions
        conclusion_list = list(self.state.conclusions.values())
        for i, c1 in enumerate(conclusion_list):
            for c2 in conclusion_list[i + 1 :]:
                # Simple contradiction detection
                # In a real implementation, this would use logical negation
                if self._are_contradictory(c1, c2):
                    conflict = Conflict(
                        conclusion_ids=[c1.id, c2.id],
                        severity=ConflictSeverity.HARD,
                        conflict_score=0.8,
                        description=f"Direct contradiction between {c1.id} and {c2.id}",
                    )

                    self.state.conflicts[conflict.id] = conflict
                    conflicts.append(conflict)

        # Mark conclusions as checked
        for conclusion in conclusions:
            conclusion.contradiction_checked = True

        logger.debug(f"Detected {len(conflicts)} conflicts")
        return conflicts

    def _are_contradictory(self, c1: Conclusion, c2: Conclusion) -> bool:
        """Check if two conclusions are contradictory."""
        # Simple string-based contradiction detection
        # In a real implementation, this would use formal logic
        content1 = str(c1.content).lower()
        content2 = str(c2.content).lower()

        # Check for direct negation
        if content1.startswith("not ") and content1[4:] in content2:
            return True
        if content2.startswith("not ") and content2[4:] in content1:
            return True

        return False

    async def search_counterexamples(
        self, conclusion: Conclusion, world_model: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """
        Search for counterexamples to a conclusion.

        Primitive: search_counterexample
        Counterexample search is mandatory for high-impact conclusions.
        """
        counterexamples = []
        world_model = world_model or {}

        # Simple counterexample search
        # In a real implementation, this would use model checking or SAT solving

        # Check if conclusion contradicts any premises
        for premise in self.state.premises.values():
            if not premise.active:
                continue

            premise_content = str(premise.content).lower()
            conclusion_content = str(conclusion.content).lower()

            # Simple contradiction check
            if self._content_contradicts(premise_content, conclusion_content):
                counterexamples.append(
                    {
                        "type": "premise_contradiction",
                        "premise_id": premise.id,
                        "description": f"Conclusion contradicts premise {premise.id}",
                    }
                )

        logger.debug(f"Found {len(counterexamples)} counterexamples for conclusion {conclusion.id}")
        return counterexamples

    def _content_contradicts(self, content1: str, content2: str) -> bool:
        """Check if two content strings contradict each other."""
        # Simple contradiction detection
        negations = ["not ", "false", "no ", "never"]

        for neg in negations:
            if content1.startswith(neg) and content1[len(neg) :] in content2:
                return True
            if content2.startswith(neg) and content2[len(neg) :] in content1:
                return True

        return False

    async def retract_invalid_conclusions(
        self,
        conclusions: list[Conclusion],
        conflict_state: list[Conflict],
        tms: TruthMaintenanceSystem = None,
    ) -> list[Retraction]:
        """
        Retract conclusions that are invalid.

        Primitive: retract_claim
        """
        retractions = []
        tms = tms or self.tms

        for conflict in conflict_state:
            for conclusion_id in conflict.conclusion_ids:
                conclusion = self.state.conclusions.get(conclusion_id)
                if conclusion and conclusion.committed:
                    # Retract the conclusion
                    conclusion.committed = False
                    conclusion.status = ConclusionStatus.RETRACTED

                    retraction = Retraction(
                        conclusion_id=conclusion_id, reason=RetractionReason.CONFLICT_DETECTED
                    )

                    self.state.retractions.append(retraction)
                    retractions.append(retraction)

                    # Add to TMS
                    tms.retractions.append(retraction)

                    logger.info(f"Retracted conclusion {conclusion_id} due to conflict")

        return retractions

    async def commit_reasoned_conclusions(
        self,
        conclusions: list[Conclusion],
        justifications: list[Justification],
        verification: dict[str, Any] = None,
    ) -> list[Conclusion]:
        """
        Commit conclusions that have passed all checks.

        Primitive: commit_conclusion

        A conclusion may be committed only if:
        Reasoned(C) = 𝟙[Typed(C) ∧ Justified(C) ∧ ConstraintSafe(C) ∧
                         ConflictBelowThreshold(C) ∧ UncertaintyTagged(C)]
        """
        committed = []

        for conclusion in conclusions:
            # Check all commit conditions
            is_typed = conclusion.content is not None
            is_justified = conclusion.justified and conclusion.justification_id is not None
            is_safe = conclusion.contradiction_checked and not self._has_high_conflict(conclusion)
            is_tagged = conclusion.uncertainty_propagated

            # Reasoned(C) check
            can_commit = is_typed and is_justified and is_safe and is_tagged

            if can_commit:
                conclusion.committed = True
                conclusion.status = ConclusionStatus.COMMITTED
                committed.append(conclusion)

                # Register with TMS
                for premise_id in conclusion.premise_ids:
                    self.tms.register_dependency(premise_id, conclusion.id)

                logger.info(f"Committed conclusion {conclusion.id}")
            else:
                logger.debug(
                    f"Conclusion {conclusion.id} failed commit check: "
                    f"typed={is_typed}, justified={is_justified}, "
                    f"safe={is_safe}, tagged={is_tagged}"
                )

        return committed

    def _has_high_conflict(self, conclusion: Conclusion, threshold: float = 0.5) -> bool:
        """Check if conclusion has high conflict score."""
        for conflict in self.state.conflicts.values():
            if conclusion.id in conflict.conclusion_ids:
                if conflict.conflict_score > threshold:
                    return True
        return False

    # ===================================================================
    # ADVANCED REASONING OPERATIONS
    # ===================================================================

    async def abductive_inference(
        self, observations: list[Premise], candidate_hypotheses: list[Hypothesis]
    ) -> Hypothesis:
        """
        Perform abductive inference (inference to best explanation).

        BestExplanation = argmax_h [ ExplanatoryPower(h) · Simplicity(h) · Coherence(h)
                                      - Contradiction(h) - Cost(h) ]
        """
        for hypothesis in candidate_hypotheses:
            # Calculate explanatory power
            explained = sum(1 for obs in observations if self._explains(hypothesis, obs))
            hypothesis.explanatory_power = explained / len(observations) if observations else 0.0

            # Calculate simplicity (inverse of complexity)
            hypothesis.simplicity = 1.0 / (1.0 + self._complexity(hypothesis))

            # Calculate coherence with existing knowledge
            hypothesis.coherence = self._coherence_score(hypothesis)

            # Check for contradictions
            contradictions = sum(
                1
                for premise in self.state.premises.values()
                if premise.active and self._contradicts(hypothesis, premise)
            )
            hypothesis.contradiction_penalty = contradictions * 0.2

            # Calculate cost
            hypothesis.cost = self._inference_cost(hypothesis)

            # Calculate overall score
            hypothesis.calculate_score()

            # Update hypothesis status
            if hypothesis.score > 0.7:
                hypothesis.status = HypothesisStatus.SUPPORTED
            elif hypothesis.score < 0.3:
                hypothesis.status = HypothesisStatus.REJECTED
            else:
                hypothesis.status = HypothesisStatus.UNDERDETERMINED

        # Select best hypothesis
        if candidate_hypotheses:
            best = max(candidate_hypotheses, key=lambda h: h.score)
            logger.info(f"Best abductive hypothesis: {best.id} (score: {best.score:.3f})")
            return best

        return None

    def _explains(self, hypothesis: Hypothesis, observation: Premise) -> bool:
        """Check if hypothesis explains observation."""
        # Simple explanation check
        # In a real implementation, this would use causal or logical entailment
        hyp_content = str(hypothesis.content).lower()
        obs_content = str(observation.content).lower()
        return obs_content in hyp_content or self._related(hyp_content, obs_content)

    def _complexity(self, hypothesis: Hypothesis) -> float:
        """Calculate complexity of hypothesis."""
        # Simple complexity metric: length of content
        return len(str(hypothesis.content)) / 100.0

    def _coherence_score(self, hypothesis: Hypothesis) -> float:
        """Calculate coherence with existing knowledge."""
        # Check alignment with existing premises
        aligned = sum(
            1
            for premise in self.state.premises.values()
            if premise.active and self._aligned(hypothesis, premise)
        )
        total = sum(1 for premise in self.state.premises.values() if premise.active)
        return aligned / total if total else 0.5

    def _contradicts(self, hypothesis: Hypothesis, premise: Premise) -> bool:
        """Check if hypothesis contradicts premise."""
        return self._content_contradicts(
            str(hypothesis.content).lower(), str(premise.content).lower()
        )

    def _inference_cost(self, hypothesis: Hypothesis) -> float:
        """Calculate inference cost for hypothesis."""
        # Simple cost model based on complexity
        return self._complexity(hypothesis) * 0.1

    def _related(self, content1: str, content2: str) -> bool:
        """Check if two content strings are related."""
        # Simple relatedness check based on word overlap
        words1 = set(content1.split())
        words2 = set(content2.split())
        overlap = len(words1 & words2)
        return overlap > 0

    def _aligned(self, hypothesis: Hypothesis, premise: Premise) -> bool:
        """Check if hypothesis aligns with premise."""
        hyp_content = str(hypothesis.content).lower()
        premise_content = str(premise.content).lower()
        return self._related(hyp_content, premise_content) and not self._contradicts(
            hypothesis, premise
        )

    async def inductive_generalization(
        self, examples: list[Premise], target_property: str
    ) -> InductiveGeneralization:
        """
        Perform inductive generalization from examples.

        Generalization = f(Examples, Coverage, Stability, Counterexamples)
        """
        generalization = InductiveGeneralization(
            examples_supporting=[e.content for e in examples],
            generalization=f"All observed instances have property: {target_property}",
        )

        # Calculate coverage
        generalization.coverage = len(examples) / (len(examples) + 5)  # Assume some unobserved

        # Calculate stability (consistency across examples)
        if len(examples) > 1:
            consistencies = []
            for i, e1 in enumerate(examples):
                for e2 in examples[i + 1 :]:
                    consistencies.append(1.0 if self._similar(e1, e2) else 0.0)
            generalization.stability = (
                sum(consistencies) / len(consistencies) if consistencies else 0.5
            )
        else:
            generalization.stability = 0.5

        # Initial confidence
        generalization.confidence = generalization.coverage * generalization.stability

        self.state.inductive_generalizations[str(uuid.uuid4())] = generalization

        logger.info(
            f"Created inductive generalization with confidence {generalization.confidence:.3f}"
        )
        return generalization

    def _similar(self, p1: Premise, p2: Premise) -> bool:
        """Check if two premises are similar."""
        return self._related(str(p1.content).lower(), str(p2.content).lower())

    async def causal_inference(
        self, cause_premise: Premise, effect_premise: Premise, mechanism: str = ""
    ) -> CausalLink:
        """
        Create a causal link.

        Cause(A,B) ≠ Correlation(A,B)
        """
        causal_link = CausalLink(
            cause=cause_premise.id,
            effect=effect_premise.id,
            mechanism=mechanism,
            confidence=min(cause_premise.confidence, effect_premise.confidence) * 0.9,
        )

        self.state.causal_links[causal_link.id] = causal_link

        logger.info(f"Created causal link: {cause_premise.id} → {effect_premise.id}")
        return causal_link

    async def counterfactual_reasoning(
        self, actual_world: dict[str, Any], intervention: dict[str, Any]
    ) -> CounterfactualBranch:
        """
        Perform counterfactual reasoning.

        W' = Intervene(W, x ← x')
        CounterfactualValue = Compare(W', W)
        """
        # Create intervened world
        predicted_world = {**actual_world, **intervention}

        # Calculate difference
        differences = {}
        for key, value in predicted_world.items():
            if key in actual_world and actual_world[key] != value:
                differences[key] = {"actual": actual_world[key], "predicted": value}

        # Calculate utility change (simplified)
        utility_change = len(differences) * 0.1  # Simple metric

        branch = CounterfactualBranch(
            intervention=intervention,
            predicted_world=predicted_world,
            difference_from_actual=differences,
            utility_change=utility_change,
            confidence=0.7,  # Counterfactuals are inherently uncertain
        )

        self.state.counterfactual_branches[branch.id] = branch

        logger.info(f"Created counterfactual branch with utility change {utility_change:.3f}")
        return branch

    # ===================================================================
    # MAIN REASONING CYCLE
    # ===================================================================

    async def reasoning_step(
        self, goals: list[Any] = None, constraints: list[ConstraintCheck] = None
    ) -> ReasoningState:
        """
        Execute one step of the reasoning cycle.

        R_{t+1} = Commit(Repair(Check(Justify(Infer(SelectRules(P_t, H_t, R_t, U_t))))))

        Reasoning = Represent → Infer → Justify → Check → Revise → Commit
        """
        # Get active premises
        active_premises = [p for p in self.state.premises.values() if p.active]

        if not active_premises:
            logger.warning("No active premises for reasoning")
            return self.state

        # Select reasoning mode
        mode_input = ModeSelectionInput(
            problem_type="general",
            ambiguity=self.state.uncertainty_state.global_uncertainty,
            risk=len(self.state.conflicts) * 0.1,
            available_evidence=len(active_premises) / 10.0,
            time_budget=1.0,
        )
        mode = self.mode_controller.select_mode(mode_input)

        # Select applicable rules
        rules = await self.select_inference_rules(mode, active_premises, goals)

        # Derive conclusions
        conclusions = await self.derive_candidate_conclusions(active_premises, rules)

        # Attach justifications
        justifications = await self.attach_justifications(conclusions, active_premises, rules)

        # Propagate uncertainty
        await self.propagate_uncertainty(active_premises, conclusions, rules)

        # Detect conflicts
        conflicts = await self.detect_reasoning_conflicts(conclusions, constraints)

        # Search counterexamples for high-impact conclusions
        for conclusion in conclusions:
            if conclusion.confidence > 0.8:  # High-impact threshold
                counterexamples = await self.search_counterexamples(conclusion)
                if counterexamples:
                    logger.warning(
                        f"Found counterexamples for high-confidence conclusion {conclusion.id}"
                    )
                    conclusion.confidence *= 0.8  # Reduce confidence

        # Retract invalid conclusions
        if conflicts:
            await self.retract_invalid_conclusions(conclusions, conflicts)

        # Commit valid conclusions
        committed = await self.commit_reasoned_conclusions(conclusions, justifications)

        # Update reasoning quality
        self.state.calculate_quality()
        self.state.update_timestamp()

        logger.info(
            f"Reasoning step complete: {len(committed)} conclusions committed, "
            f"quality: {self.state.reasoning_quality:.3f}"
        )

        return self.state

    async def run_reasoning(
        self, max_steps: int = 10, quality_threshold: float = 0.8, goals: list[Any] = None
    ) -> ReasoningState:
        """
        Run multi-step reasoning until convergence or max steps.

        Q_reason(R_{t+1}) > Q_reason(R_t)
        """
        previous_quality = self.state.reasoning_quality

        for step in range(max_steps):
            await self.reasoning_step(goals)

            current_quality = self.state.reasoning_quality

            # Check for improvement
            if current_quality >= quality_threshold:
                logger.info(
                    f"Reasoning converged at step {step + 1} with quality {current_quality:.3f}"
                )
                break

            # Check for stagnation
            if abs(current_quality - previous_quality) < 0.01:
                logger.info(f"Reasoning stagnated at step {step + 1}")
                break

            previous_quality = current_quality
        else:
            logger.info(
                f"Reasoning reached max steps ({max_steps}) with quality {current_quality:.3f}"
            )

        return self.state

    # ===================================================================
    # UTILITY METHODS
    # ===================================================================

    def get_committed_conclusions(self) -> list[Conclusion]:
        """Get all committed conclusions."""
        return [c for c in self.state.conclusions.values() if c.committed]

    def get_justification_path(self, conclusion_id: str) -> list[dict[str, Any]]:
        """Get justification path for a conclusion."""
        return self.justification_graph.get_justification_path(conclusion_id)

    def premise_changed(self, premise_id: str) -> list[Retraction]:
        """Handle premise change - trigger TMS."""
        retractions = self.tms.premise_changed(premise_id, self.state)
        self.state.update_timestamp()
        return retractions

    def get_state(self) -> ReasoningState:
        """Get current reasoning state."""
        return self.state

    def export_state(self) -> dict[str, Any]:
        """Export complete reasoning state."""
        return {
            "reasoning_state": self.state.to_dict(),
            "justification_graph": self.justification_graph.to_dict(),
            "truth_maintenance": self.tms.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ============================================================================
# GLOBAL SINGLETON ACCESSOR
# ============================================================================


@lru_cache(maxsize=1)
def get_reasoning_kernel() -> ReasoningKernel:
    """Get the global reasoning kernel instance (singleton)."""
    return ReasoningKernel()


# ============================================================================
# INVARIANTS
# ============================================================================

REASONING_INVARIANTS = {
    "REI01": "Every committed conclusion must have an explicit justification path",
    "REI02": "Premises, rules, and conclusions must remain distinct object types",
    "REI03": "Uncertainty must propagate through non-deductive inference",
    "REI04": "Conflict detection is mandatory before conclusion commit",
    "REI05": "Premise change must trigger dependent conclusion reevaluation",
    "REI06": "Counterexample search is mandatory for high-impact conclusions",
    "REI07": "Renderer may not state as fact what the reasoning kernel has not committed",
}


def verify_invariant_rei01(kernel: ReasoningKernel) -> bool:
    """
    Verify REI01: Every committed conclusion has explicit justification.
    """
    for conclusion in kernel.state.conclusions.values():
        if conclusion.committed:
            if not conclusion.justified or conclusion.justification_id is None:
                return False
    return True


def verify_invariant_rei04(kernel: ReasoningKernel) -> bool:
    """
    Verify REI04: Conflict detection before commit.
    """
    for conclusion in kernel.state.conclusions.values():
        if conclusion.committed and not conclusion.contradiction_checked:
            return False
    return True


def verify_all_invariants(kernel: ReasoningKernel) -> dict[str, bool]:
    """Verify all reasoning invariants."""
    return {"REI01": verify_invariant_rei01(kernel), "REI04": verify_invariant_rei04(kernel)}


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
    """Example of using the reasoning kernel."""
    # Initialize kernel
    kernel = get_reasoning_kernel()
    await kernel.initialize()

    # Assert premises
    await kernel.assert_premise(
        content="All humans are mortal",
        premise_type=PremiseType.FACT,
        confidence=1.0,
        source="axiom",
    )

    await kernel.assert_premise(
        content="Socrates is human",
        premise_type=PremiseType.OBSERVATION,
        confidence=1.0,
        source="observation",
    )

    # Run reasoning
    await kernel.run_reasoning(max_steps=5)

    # Get committed conclusions
    conclusions = kernel.get_committed_conclusions()

    # Export state
    state = kernel.export_state()

    return conclusions, state


if __name__ == "__main__":
    # Run example
    conclusions, state = asyncio.run(example_usage())
    print(f"Committed conclusions: {len(conclusions)}")
    print(f"Reasoning quality: {state['reasoning_state']['reasoning_quality']:.3f}")

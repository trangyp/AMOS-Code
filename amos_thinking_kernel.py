from typing import Any, Dict, List, Optional, Tuple

"""
AMOS Thinking Kernel - Core State Transformation Engine

This module implements the formal thinking model defined in AMOS_THINKING_KERNEL_SPEC.md.

Key Insight:
    Thinking ≠ TextGeneration
    Thinking ≠ Parsing
    Thinking ≠ Retrieval
    Thinking ≠ SearchOnly

    Thinking = controlled internal state transformation under goals, constraints,
               uncertainty, and error correction

    Thinking = state transition over latent structure: S_t → S_{t+1}

Architecture:
    Input → Read → Think → Verify → Select → Act → Render

    Where "Think" is this kernel operating on internal structured state.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from functools import lru_cache

# ============================================================================
# Section 1: Enums and Type Definitions
# ============================================================================

class ThinkingMode(Enum):
    """Modes of thinking operation."""

    HOLD = "hold"  # Preserve current state
    CLARIFY = "clarify"  # Decompose and clarify
    DECOMPOSE = "decompose"  # Break into sub-problems
    COMPARE = "compare"  # Evaluate alternatives
    SIMULATE = "simulate"  # Project consequences
    VERIFY = "verify"  # Check against constraints
    REPAIR = "repair"  # Fix errors
    COMMIT = "commit"  # Finalize state update
    DEFER = "defer"  # Pause, await more info

class HypothesisStatus(Enum):
    """Status of a hypothesis in the belief state."""

    ACTIVE = "active"
    REJECTED = "rejected"
    COMMITTED = "committed"
    PENDING = "pending"

class ErrorType(Enum):
    """Types of errors detectable in thinking."""

    PREDICTION = "prediction"
    COHERENCE = "coherence"
    CONSTRAINT = "constraint"
    REASONING = "reasoning"
    CONVERGENCE = "convergence"

class FailureSignal(Enum):
    """Meta-thinking failure signals."""

    STAGNATION = "stagnation"  # No improvement over iterations
    OSCILLATION = "oscillation"  # Flipping between states
    ERROR_ACCUMULATION = "error_accumulation"
    MODE_MISMATCH = "mode_mismatch"

# ============================================================================
# Section 2: Data Structures (State Components)
# ============================================================================

@dataclass(frozen=True)
class WorkspaceItem:
    """Single item in the active workspace."""

    id: str
    content: Any
    activation: float = 1.0  # 0.0 to 1.0
    source: str = "input"  # input, memory, inference
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass(frozen=True)
class Hypothesis:
    """A candidate explanation or solution."""

    id: str
    content: Any
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.ACTIVE
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass(frozen=True)
class Goal:
    """An objective the thinking is working toward."""

    id: str
    description: str
    priority: float = 1.0  # 0.0 to 1.0
    deadline: Optional[str] = None
    satisfied: bool = False

@dataclass(frozen=True)
class Constraint:
    """A hard or soft constraint on thinking."""

    id: str
    type: str  # resource, time, logic, safety
    description: str
    hard: bool = True  # Hard constraints cannot be violated
    check_fn: Optional[str] = None  # Reference to validation function

@dataclass(frozen=True)
class ConstraintViolation:
    """A detected constraint violation."""

    constraint_id: str
    severity: str  # critical, warning
    message: str

@dataclass
class Workspace:
    """Active workspace component W_t."""

    active_items: List[WorkspaceItem] = field(default_factory=list)
    focus_items: List[str] = field(default_factory=list)  # IDs of focused items
    suppressed_items: List[str] = field(default_factory=list)
    capacity_limit: int = 7  # Working memory capacity (Miller's law)

@dataclass
class BeliefState:
    """Belief state component H_t (hypotheses)."""

    hypotheses: List[Hypothesis] = field(default_factory=list)
    active_model: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    uncertainty: float = 1.0
    entropy: float = 1.0

@dataclass
class GoalState:
    """Goal state component G_t."""

    primary_goal: Optional[Goal] = None
    secondary_goals: List[Goal] = field(default_factory=list)
    priority_weights: Dict[str, float] = field(default_factory=dict)
    satisfied_goals: List[str] = field(default_factory=list)

@dataclass
class ConstraintState:
    """Constraint state component C_t."""

    hard_constraints: List[Constraint] = field(default_factory=list)
    soft_constraints: List[Constraint] = field(default_factory=list)
    violations: List[ConstraintViolation] = field(default_factory=list)

@dataclass
class ErrorState:
    """Error state component E_t."""

    prediction_error: float = 0.0
    coherence_error: float = 0.0
    constraint_error: float = 0.0
    reasoning_error: float = 0.0
    detected_anomalies: List[dict[str, Any]] = field(default_factory=list)

    def total_error(self) -> float:
        """Aggregate error score."""
        return (
            self.prediction_error
            + self.coherence_error
            + self.constraint_error
            + self.reasoning_error
        ) / 4.0

@dataclass
class ControlState:
    """Control/policy state component Π_t."""

    mode: ThinkingMode = ThinkingMode.HOLD
    depth: str = "medium"  # low, medium, high
    search_budget: int = 100
    time_budget_ms: int = 5000
    iteration_count: int = 0
    max_iterations: int = 10

@dataclass
class TransitionState:
    """State tracking transitions."""

    last_operation: Optional[str] = None
    next_operation: Optional[str] = None
    improvement_score: float = 0.0
    convergence_detected: bool = False

@dataclass
class QualityMetrics:
    """Computed quality metrics for a state."""

    coherence: float = 0.0
    goal_alignment: float = 0.0
    constraint_satisfaction: float = 0.0
    predictive_power: float = 0.0
    overall_quality: float = 0.0

@dataclass
class ThinkingState:
    """
    Complete thinking state S_t = (W_t, M_t, H_t, G_t, C_t, U_t, E_t, Π_t)

    This is the core data structure that the thinking kernel operates on.
    All thinking operations transform this state.
    """

    version: str = "1.0"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Core state components
    workspace: Workspace = field(default_factory=Workspace)
    belief_state: BeliefState = field(default_factory=BeliefState)
    goal_state: GoalState = field(default_factory=GoalState)
    constraint_state: ConstraintState = field(default_factory=ConstraintState)
    error_state: ErrorState = field(default_factory=ErrorState)
    control_state: ControlState = field(default_factory=ControlState)
    transition_state: TransitionState = field(default_factory=TransitionState)
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)

    # Optional memory activation (M_t)
    memory_activations: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> ThinkingState:
        """Create a deep copy of the state."""
        return ThinkingState(
            version=self.version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            workspace=Workspace(
                active_items=list(self.workspace.active_items),
                focus_items=list(self.workspace.focus_items),
                suppressed_items=list(self.workspace.suppressed_items),
                capacity_limit=self.workspace.capacity_limit,
            ),
            belief_state=BeliefState(
                hypotheses=list(self.belief_state.hypotheses),
                active_model=dict(self.belief_state.active_model),
                confidence=self.belief_state.confidence,
                uncertainty=self.belief_state.uncertainty,
                entropy=self.belief_state.entropy,
            ),
            goal_state=GoalState(
                primary_goal=self.goal_state.primary_goal,
                secondary_goals=list(self.goal_state.secondary_goals),
                priority_weights=dict(self.goal_state.priority_weights),
                satisfied_goals=list(self.goal_state.satisfied_goals),
            ),
            constraint_state=ConstraintState(
                hard_constraints=list(self.constraint_state.hard_constraints),
                soft_constraints=list(self.constraint_state.soft_constraints),
                violations=list(self.constraint_state.violations),
            ),
            error_state=ErrorState(
                prediction_error=self.error_state.prediction_error,
                coherence_error=self.error_state.coherence_error,
                constraint_error=self.error_state.constraint_error,
                reasoning_error=self.error_state.reasoning_error,
                detected_anomalies=list(self.error_state.detected_anomalies),
            ),
            control_state=ControlState(
                mode=self.control_state.mode,
                depth=self.control_state.depth,
                search_budget=self.control_state.search_budget,
                time_budget_ms=self.control_state.time_budget_ms,
                iteration_count=self.control_state.iteration_count,
                max_iterations=self.control_state.max_iterations,
            ),
            transition_state=TransitionState(
                last_operation=self.transition_state.last_operation,
                next_operation=self.transition_state.next_operation,
                improvement_score=self.transition_state.improvement_score,
                convergence_detected=self.transition_state.convergence_detected,
            ),
            quality_metrics=QualityMetrics(
                coherence=self.quality_metrics.coherence,
                goal_alignment=self.quality_metrics.goal_alignment,
                constraint_satisfaction=self.quality_metrics.constraint_satisfaction,
                predictive_power=self.quality_metrics.predictive_power,
                overall_quality=self.quality_metrics.overall_quality,
            ),
            memory_activations=dict(self.memory_activations),
        )

# ============================================================================
# Section 3: Meta-Thinking State
# ============================================================================

@dataclass
class OperatorQualityRecord:
    """Record of an operator's performance."""

    operator: str
    quality_score: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class FailureSignalRecord:
    """Detected failure signal for meta-thinking."""

    type: FailureSignal
    severity: str  # low, medium, high
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class MetaThinkingState:
    """
    State for thinking about thinking itself.

    Meta_t = Model(T_t)
    """

    current_operator: Optional[str] = None
    operator_quality_history: List[OperatorQualityRecord] = field(default_factory=list)
    failure_signals: List[FailureSignalRecord] = field(default_factory=list)
    repair_candidate: Dict[str, str]  = None
    policy_update_required: bool = False
    policy_version: int = 1
    learning_rate: float = 0.1

# ============================================================================
# Section 4: Thinking Operators (Ω)
# ============================================================================

class ThinkingOperators:
    """
    Primitive thinking operations ω_i : S_t → S_{t+1}

    These are the atomic operations that transform thinking state.
    They are closer to real thinking than language generation is.
    """

    @staticmethod
    def hold(state: ThinkingState) -> ThinkingState:
        """
        ω_hold(S_t) = S_t

        Preserve the current state without collapse.
        Useful when awaiting more information or when the current
        state is already optimal.
        """
        new_state = state.copy()
        new_state.control_state.mode = ThinkingMode.HOLD
        new_state.transition_state.last_operation = "hold"
        new_state.transition_state.improvement_score = 0.0
        return new_state

    @staticmethod
    def focus(state: ThinkingState, item_ids: Optional[list[str]] = None) -> ThinkingState:
        """
        ω_focus(S_t) = Reweight(S_t, FocusMask)

        Increase activation weight on selected workspace items.
        Models selective attention.
        """
        new_state = state.copy()

        if item_ids:
            # Validate items exist
            valid_ids = {item.id for item in state.workspace.active_items}
            new_state.workspace.focus_items = [id for id in item_ids if id in valid_ids]
        else:
            # Auto-focus: select highest activation items
            sorted_items = sorted(
                state.workspace.active_items, key=lambda x: x.activation, reverse=True
            )
            new_state.workspace.focus_items = [
                item.id
                for item in sorted_items[:3]  # Top 3
            ]

        new_state.control_state.mode = ThinkingMode.CLARIFY
        new_state.transition_state.last_operation = "focus"
        return new_state

    @staticmethod
    def activate_memory(
        state: ThinkingState, memory_query: str, memory_store: Dict[str, Any]  = None
    ) -> ThinkingState:
        """
        Activate relevant memories based on query.

        M_t = RetrieveMemory(Query, LongTermStore)
        """
        new_state = state.copy()

        # Simple implementation: exact and partial matching
        if memory_store:
            activated = {}
            query_lower = memory_query.lower()

            for key, value in memory_store.items():
                if query_lower in key.lower() or query_lower in str(value).lower():
                    activated[key] = value

            new_state.memory_activations.update(activated)

        # Add to workspace if relevant
        for key, value in new_state.memory_activations.items():
            item = WorkspaceItem(id=f"mem_{key}", content=value, activation=0.7, source="memory")
            if len(new_state.workspace.active_items) < new_state.workspace.capacity_limit:
                new_state.workspace.active_items.append(item)

        new_state.transition_state.last_operation = "activate_memory"
        return new_state

    @staticmethod
    def form_hypothesis(
        state: ThinkingState, hypothesis_content: Optional[Any] = None
    ) -> ThinkingState:
        """
        Form a new hypothesis from current workspace and memory.

        H_new = GenerateHypothesis(W_t, M_t, G_t)
        """
        new_state = state.copy()

        # Generate hypothesis ID
        hyp_id = (
            f"hyp_{len(new_state.belief_state.hypotheses)}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
        )

        # If no content provided, synthesize from workspace
        if hypothesis_content is None:
            # Simple synthesis: combine focused items
            focused_content = [
                item.content
                for item in new_state.workspace.active_items
                if item.id in new_state.workspace.focus_items
            ]
            hypothesis_content = {"synthesis_of": focused_content, "basis": "workspace_focus"}

        hypothesis = Hypothesis(
            id=hyp_id,
            content=hypothesis_content,
            confidence=0.5,  # Neutral initial confidence
            evidence=[f"formed_from_{new_state.transition_state.last_operation or 'init'}"],
        )

        new_state.belief_state.hypotheses.append(hypothesis)

        # Update entropy
        n_hypotheses = len(new_state.belief_state.hypotheses)
        if n_hypotheses > 0:
            new_state.belief_state.entropy = -sum(
                (1.0 / n_hypotheses) * math.log(1.0 / n_hypotheses) for _ in range(n_hypotheses)
            )

        new_state.transition_state.last_operation = "form_hypothesis"
        return new_state

    @staticmethod
    def compare(state: ThinkingState) -> ThinkingState:
        """
        ω_compare(H_t) = PairwiseEval(H_t)

        Evaluate hypotheses against each other.
        Updates confidence scores based on comparison.
        """
        new_state = state.copy()
        hypotheses = new_state.belief_state.hypotheses

        if len(hypotheses) < 2:
            # Nothing to compare
            new_state.transition_state.last_operation = "compare"
            return new_state

        # Simple comparison: adjust confidence based on goal alignment
        if new_state.goal_state.primary_goal:
            goal_desc = new_state.goal_state.primary_goal.description.lower()

            for i, hyp in enumerate(hypotheses):
                hyp_content = str(hyp.content).lower()

                # Simple relevance scoring
                relevance = 0.5
                if any(word in hyp_content for word in goal_desc.split()):
                    relevance = 0.8

                # Update confidence (moving average)
                new_confidence = (hyp.confidence * 0.7) + (relevance * 0.3)

                # Create updated hypothesis
                new_hyp = Hypothesis(
                    id=hyp.id,
                    content=hyp.content,
                    confidence=min(1.0, max(0.0, new_confidence)),
                    evidence=hyp.evidence + ["compared"],
                    status=hyp.status,
                )
                new_state.belief_state.hypotheses[i] = new_hyp

        # Mark best hypothesis
        best = max(new_state.belief_state.hypotheses, key=lambda h: h.confidence)
        new_state.belief_state.active_model = {
            "best_hypothesis_id": best.id,
            "best_confidence": best.confidence,
        }

        new_state.control_state.mode = ThinkingMode.COMPARE
        new_state.transition_state.last_operation = "compare"
        return new_state

    @staticmethod
    def transform(state: ThinkingState, transform_type: str = "abstract") -> ThinkingState:
        """
        ω_transform(R_t) = R'_t

        Rewrite representation into more useful form.
        """
        new_state = state.copy()

        if transform_type == "abstract":
            # Abstract: extract key properties from workspace
            abstractions = {}
            for item in new_state.workspace.active_items:
                if isinstance(item.content, dict):
                    abstractions[item.id] = {
                        k: v
                        for k, v in item.content.items()
                        if k in ["type", "category", "priority", "status"]
                    }

            # Add abstraction to belief state
            new_state.belief_state.active_model["abstractions"] = abstractions

        elif transform_type == "concretize":
            # Concretize: expand abstract items with details
            pass  # Implementation depends on domain

        elif transform_type == "reframe":
            # Reframe: view from different perspective (goal-based)
            if new_state.goal_state.primary_goal:
                new_state.belief_state.active_model["frame"] = (
                    f"goal_perspective:{new_state.goal_state.primary_goal.id}"
                )

        new_state.control_state.mode = ThinkingMode.CLARIFY
        new_state.transition_state.last_operation = f"transform_{transform_type}"
        return new_state

    @staticmethod
    def simulate(state: ThinkingState, horizon: int = 1) -> ThinkingState:
        """
        ω_simulate(S_t) = Ŝ_{t+h}

        Project consequences of current state into the future.
        """
        new_state = state.copy()

        # Simple simulation: project what would happen if we commit current best hypothesis
        best_hyp_id = new_state.belief_state.active_model.get("best_hypothesis_id")
        if best_hyp_id:
            best_hyp = next(
                (h for h in new_state.belief_state.hypotheses if h.id == best_hyp_id), None
            )
            if best_hyp:
                # Simulate consequences
                simulation_result = {
                    "hypothesis_committed": best_hyp_id,
                    "projected_confidence": best_hyp.confidence * (0.95**horizon),
                    "horizon": horizon,
                    "risk_assessment": "low" if best_hyp.confidence > 0.7 else "medium",
                }
                new_state.belief_state.active_model["simulation"] = simulation_result

        new_state.control_state.mode = ThinkingMode.SIMULATE
        new_state.transition_state.last_operation = f"simulate_h{horizon}"
        return new_state

    @staticmethod
    def evaluate(state: ThinkingState) -> Tuple[ThinkingState, QualityMetrics]:
        """
        ω_eval(S_t) = Score_t

        Score current state relative to goals and constraints.
        """
        new_state = state.copy()

        # Calculate coherence
        coherence = 1.0 - new_state.error_state.total_error()

        # Calculate goal alignment
        if new_state.goal_state.primary_goal:
            best_conf = new_state.belief_state.active_model.get("best_confidence", 0.0)
            goal_alignment = best_conf * new_state.goal_state.primary_goal.priority
        else:
            goal_alignment = 0.5

        # Calculate constraint satisfaction
        n_violations = len(new_state.constraint_state.violations)
        n_constraints = len(new_state.constraint_state.hard_constraints)
        if n_constraints > 0:
            constraint_satisfaction = 1.0 - (n_violations / n_constraints)
        else:
            constraint_satisfaction = 1.0

        # Calculate predictive power (based on simulation quality)
        has_simulation = "simulation" in new_state.belief_state.active_model
        predictive_power = 0.8 if has_simulation else 0.4

        # Overall quality
        overall = (
            0.25 * coherence
            + 0.35 * goal_alignment
            + 0.25 * constraint_satisfaction
            + 0.15 * predictive_power
        )
        metrics = QualityMetrics(
            coherence=coherence,
            goal_alignment=goal_alignment,
            constraint_satisfaction=constraint_satisfaction,
            predictive_power=predictive_power,
            overall_quality=overall,
        )

        new_state.quality_metrics = metrics
        new_state.transition_state.last_operation = "evaluate"

        return new_state, metrics

    @staticmethod
    def detect_error(state: ThinkingState, expected: Optional[Any] = None) -> ErrorState:
        """
        Detect errors in current state.

        Returns error state without modifying main state.
        """
        errors = ErrorState()

        # Coherence error: contradictions in workspace
        if len(state.workspace.active_items) > 1:
            # Check for obvious contradictions
            contents = [str(item.content) for item in state.workspace.active_items]
            contradictions = []
            for i, c1 in enumerate(contents):
                for c2 in contents[i + 1 :]:
                    if c1.lower() == "not_" + c2.lower() or c2.lower() == "not_" + c1.lower():
                        contradictions.append((c1, c2))
            errors.coherence_error = min(1.0, len(contradictions) * 0.3)

        # Constraint error
        errors.constraint_error = min(1.0, len(state.constraint_state.violations) * 0.25)

        # Reasoning error: check hypothesis quality
        low_conf_hypotheses = [h for h in state.belief_state.hypotheses if h.confidence < 0.3]
        errors.reasoning_error = min(1.0, len(low_conf_hypotheses) * 0.2)

        # Prediction error (if expected provided)
        if expected is not None:
            best_hyp_id = state.belief_state.active_model.get("best_hypothesis_id")
            if best_hyp_id:
                best_hyp = next(
                    (h for h in state.belief_state.hypotheses if h.id == best_hyp_id), None
                )
                if best_hyp and str(best_hyp.content) != str(expected):
                    errors.prediction_error = 0.5

        return errors

    @staticmethod
    def repair(state: ThinkingState, error_state: ErrorState) -> ThinkingState:
        """
        ω_repair(S_t) = S'_t

        Fix state defects based on detected errors.
        """
        new_state = state.copy()

        # Repair coherence errors
        if error_state.coherence_error > 0.3:
            # Remove contradictory items
            kept_items = []
            for item in new_state.workspace.active_items:
                # Simple: keep higher activation items
                if item.activation > 0.5:
                    kept_items.append(item)
            new_state.workspace.active_items = kept_items[: new_state.workspace.capacity_limit]

        # Repair constraint errors
        if error_state.constraint_error > 0.3:
            # Adjust to reduce violations
            new_state.constraint_state.violations = [
                v for v in new_state.constraint_state.violations if v.severity != "critical"
            ]

        # Repair reasoning errors
        if error_state.reasoning_error > 0.3:
            # Remove low-confidence hypotheses
            new_state.belief_state.hypotheses = [
                h for h in new_state.belief_state.hypotheses if h.confidence >= 0.3
            ]

        # Update error state
        new_state.error_state = error_state
        new_state.control_state.mode = ThinkingMode.REPAIR
        new_state.transition_state.last_operation = "repair"
        return new_state

    @staticmethod
    def commit(state: ThinkingState) -> ThinkingState:
        """
        ω_commit(S_t) = S_{t+1}

        Make the state transition official.
        """
        new_state = state.copy()

        # Commit best hypothesis
        best_hyp_id = new_state.belief_state.active_model.get("best_hypothesis_id")
        if best_hyp_id:
            # Mark as committed
            for i, hyp in enumerate(new_state.belief_state.hypotheses):
                if hyp.id == best_hyp_id:
                    new_hyp = Hypothesis(
                        id=hyp.id,
                        content=hyp.content,
                        confidence=hyp.confidence,
                        evidence=hyp.evidence + ["committed"],
                        status=HypothesisStatus.COMMITTED,
                    )
                    new_state.belief_state.hypotheses[i] = new_hyp
                    break

        # Clear workspace (working memory refresh)
        new_state.workspace.active_items = []
        new_state.workspace.focus_items = []

        # Update control
        new_state.control_state.mode = ThinkingMode.COMMIT
        new_state.control_state.iteration_count += 1
        new_state.transition_state.last_operation = "commit"
        new_state.transition_state.convergence_detected = True

        return new_state

    @staticmethod
    def select_next_operator(
        state: ThinkingState, error_state: ErrorState, goals: List[Goal]
    ) -> str:
        """
        Select the next thinking operator based on state.

        Mode* = argmax_m [ExpectedImprovement(m) · Cost(m) · Risk(m)]
        """
        # Simple heuristic-based selection
        total_error = error_state.total_error()
        n_hypotheses = len(state.belief_state.hypotheses)
        iteration = state.control_state.iteration_count

        if total_error > 0.5:
            return "repair"

        if n_hypotheses < 2:
            return "form_hypothesis"

        if n_hypotheses >= 2 and iteration % 3 == 0:
            return "compare"

        if iteration % 4 == 0:
            return "simulate"

        if iteration > state.control_state.max_iterations * 0.7:
            return "evaluate"

        if iteration >= state.control_state.max_iterations:
            return "commit"

        return "focus"

# ============================================================================
# Section 5: Meta-Thinking Operators
# ============================================================================

class MetaThinkingOperators:
    """
    Operators for thinking about thinking itself.

    MetaThink = ObserveThinking → DetectFailure → SelectBetterOperator → UpdatePolicy
    """

    @staticmethod
    def observe_thinking(
        meta_state: MetaThinkingState, thinking_history: List[ThinkingState]
    ) -> MetaThinkingState:
        """Observe recent thinking operations."""
        new_meta = MetaThinkingState(
            current_operator=meta_state.current_operator,
            operator_quality_history=list(meta_state.operator_quality_history),
            failure_signals=list(meta_state.failure_signals),
            repair_candidate=meta_state.repair_candidate,
            policy_update_required=meta_state.policy_update_required,
            policy_version=meta_state.policy_version,
            learning_rate=meta_state.learning_rate,
        )

        if len(thinking_history) >= 2:
            # Observe last operation
            last_op = thinking_history[-1].transition_state.last_operation
            new_meta.current_operator = last_op

            # Record quality
            quality = thinking_history[-1].quality_metrics.overall_quality
            new_meta.operator_quality_history.append(
                OperatorQualityRecord(operator=last_op or "unknown", quality_score=quality)
            )
            # Keep only last 20
            new_meta.operator_quality_history = new_meta.operator_quality_history[-20:]

        return new_meta

    @staticmethod
    def detect_failure(
        meta_state: MetaThinkingState, thinking_history: List[ThinkingState]
    ) -> MetaThinkingState:
        """Detect failure signals in thinking process."""
        new_meta = MetaThinkingState(
            current_operator=meta_state.current_operator,
            operator_quality_history=list(meta_state.operator_quality_history),
            failure_signals=list(meta_state.failure_signals),
            repair_candidate=meta_state.repair_candidate,
            policy_update_required=meta_state.policy_update_required,
            policy_version=meta_state.policy_version,
            learning_rate=meta_state.learning_rate,
        )

        if len(thinking_history) < 3:
            return new_meta

        # Check for stagnation
        recent_qualities = [s.quality_metrics.overall_quality for s in thinking_history[-5:]]
        if len(recent_qualities) >= 3:
            if max(recent_qualities) - min(recent_qualities) < 0.05:
                new_meta.failure_signals.append(
                    FailureSignalRecord(
                        type=FailureSignal.STAGNATION,
                        severity="medium",
                        description="Quality not improving over last 5 iterations",
                    )
                )

        # Check for oscillation
        if len(thinking_history) >= 4:
            ops = [s.transition_state.last_operation for s in thinking_history[-4:]]
            if ops[0] == ops[2] and ops[1] == ops[3] and ops[0] != ops[1]:
                new_meta.failure_signals.append(
                    FailureSignalRecord(
                        type=FailureSignal.OSCILLATION,
                        severity="high",
                        description=f"Oscillation between {ops[0]} and {ops[1]}",
                    )
                )

        # Check for error accumulation
        recent_errors = [s.error_state.total_error() for s in thinking_history[-3:]]
        if all(e > 0.5 for e in recent_errors):
            new_meta.failure_signals.append(
                FailureSignalRecord(
                    type=FailureSignal.ERROR_ACCUMULATION,
                    severity="high",
                    description="Errors accumulating over last 3 iterations",
                )
            )

        # Keep only recent signals
        new_meta.failure_signals = new_meta.failure_signals[-10:]

        return new_meta

    @staticmethod
    def update_policy(meta_state: MetaThinkingState) -> MetaThinkingState:
        """Update thinking policy based on observations."""
        new_meta = MetaThinkingState(
            current_operator=meta_state.current_operator,
            operator_quality_history=list(meta_state.operator_quality_history),
            failure_signals=list(meta_state.failure_signals),
            repair_candidate=None,
            policy_update_required=False,
            policy_version=meta_state.policy_version + 1,
            learning_rate=meta_state.learning_rate,
        )

        # Check if high-severity failures exist
        high_severity = [f for f in new_meta.failure_signals if f.severity == "high"]

        if high_severity:
            # Suggest repair
            latest_failure = high_severity[-1]
            new_meta.repair_candidate = {
                "operator": "repair"
                if latest_failure.type == FailureSignal.ERROR_ACCUMULATION
                else "hold",
                "reason": latest_failure.description,
            }
            new_meta.policy_update_required = True

        return new_meta

# ============================================================================
# Section 6: Thinking Kernel (Main Engine)
# ============================================================================

@dataclass
class ThinkingResult:
    """Result of a thinking operation."""

    final_state: ThinkingState
    history: List[ThinkingState]
    converged: bool
    iterations: int
    quality_progression: List[float]
    meta_state: Optional[MetaThinkingState] = None

class ThinkingKernel:
    """
    Core thinking engine implementing the 6-stage thinking loop.

    Think(S_t, x_t) = Control(Revise(Evaluate(Transform(Compare(Represent(S_t, x_t))))))

    This is the main interface for machine thinking.
    """

    def __init__(self, enable_meta_thinking: bool = True):
        self.operators = ThinkingOperators()
        self.meta_operators = MetaThinkingOperators()
        self.enable_meta_thinking = enable_meta_thinking
        self.meta_state = MetaThinkingState()

    def initialize_state(
        self,
        goals: Optional[list[Goal]] = None,
        constraints: Optional[list[Constraint]] = None,
        initial_workspace: Optional[list[Any]] = None,
    ) -> ThinkingState:
        """Initialize a fresh thinking state."""
        state = ThinkingState()

        if goals:
                state.goal_state.primary_goal = goals[0]
                state.goal_state.secondary_goals = goals[1:]

        if constraints:
            state.constraint_state.hard_constraints = [c for c in constraints if c.hard]
            state.constraint_state.soft_constraints = [c for c in constraints if not c.hard]

        if initial_workspace:
            for i, content in enumerate(initial_workspace):
                item = WorkspaceItem(
                    id=f"init_{i}", content=content, activation=1.0, source="input"
                )
                state.workspace.active_items.append(item)

        return state

    def think_step(
        self,
        state: ThinkingState,
        input_data: Optional[Any] = None,
        mode: Optional[ThinkingMode] = None,
    ) -> ThinkingState:
        """
        Execute a single thinking step.

        This applies the 6-stage pipeline once:
        Represent → Compare → Transform → Evaluate → Revise → Control
        """
        # Stage 1: Represent (ingest input)
        if input_data is not None:
            # Add to workspace
            item = WorkspaceItem(
                id=f"input_{state.control_state.iteration_count}",
                content=input_data,
                activation=1.0,
                source="input",
            )
            state.workspace.active_items.append(item)

            # Enforce capacity limit
            if len(state.workspace.active_items) > state.workspace.capacity_limit:
                # Remove lowest activation
                state.workspace.active_items.sort(key=lambda x: x.activation)
                state.workspace.active_items = state.workspace.active_items[
                    -state.workspace.capacity_limit :
                ]

        # Stage 2-6: Apply thinking operator based on mode or selection
        if mode is None:
            # Auto-select mode
            error_state = self.operators.detect_error(state)
            mode_str = self.operators.select_next_operator(
                state, error_state, state.goal_state.secondary_goals
            )
            mode = (
                ThinkingMode(mode_str)
                if mode_str in [m.value for m in ThinkingMode]
                else ThinkingMode.CLARIFY
            )

        # Apply selected operator
        if mode == ThinkingMode.HOLD:
            new_state = self.operators.hold(state)
        elif mode == ThinkingMode.CLARIFY or mode == ThinkingMode.FOCUS:
            new_state = self.operators.focus(state)
        elif mode == ThinkingMode.COMPARE:
            new_state = self.operators.compare(state)
        elif mode == ThinkingMode.SIMULATE:
            new_state = self.operators.simulate(state, horizon=1)
        elif mode == ThinkingMode.VERIFY or mode == ThinkingMode.EVALUATE:
            new_state, _ = self.operators.evaluate(state)
        elif mode == ThinkingMode.REPAIR:
            error_state = self.operators.detect_error(state)
            new_state = self.operators.repair(state, error_state)
        elif mode == ThinkingMode.COMMIT:
            new_state = self.operators.commit(state)
        elif mode == ThinkingMode.DEFER:
            new_state = self.operators.hold(state)
        else:
            # Default: form hypothesis
            new_state = self.operators.form_hypothesis(state)

        return new_state

    def think(
        self,
        initial_state: ThinkingState,
        input_data: Optional[Any] = None,
        max_iterations: int = 10,
        convergence_threshold: float = 0.01,
    ) -> ThinkingResult:
        """
        Execute full thinking loop until convergence or max iterations.

        Q(S_{t+1}) > Q(S_t) must hold for good thinking.
        """
        history = [initial_state.copy()]
        state = initial_state.copy()
        quality_progression = [initial_state.quality_metrics.overall_quality]

        for iteration in range(max_iterations):
            # Execute thinking step
            state = self.think_step(state, input_data if iteration == 0 else None)

            # Evaluate quality
            state, metrics = self.operators.evaluate(state)
            quality_progression.append(metrics.overall_quality)

            # Check convergence
            if iteration > 0:
                quality_delta = quality_progression[-1] - quality_progression[-2]
                if abs(quality_delta) < convergence_threshold:
                    state.transition_state.convergence_detected = True
                    break

            # Meta-thinking
            if self.enable_meta_thinking:
                self.meta_state = self.meta_operators.observe_thinking(
                    self.meta_state, history + [state]
                )
                self.meta_state = self.meta_operators.detect_failure(
                    self.meta_state, history + [state]
                )
                self.meta_state = self.meta_operators.update_policy(self.meta_state)

                # Check for policy intervention
                if self.meta_state.policy_update_required and self.meta_state.repair_candidate:
                    # Apply repair
                    if self.meta_state.repair_candidate["operator"] == "repair":
                        error_state = self.operators.detect_error(state)
                        state = self.operators.repair(state, error_state)

            history.append(state.copy())
            state.control_state.iteration_count = iteration + 1

        return ThinkingResult(
            final_state=state,
            history=history,
            converged=state.transition_state.convergence_detected,
            iterations=len(history) - 1,
            quality_progression=quality_progression,
            meta_state=self.meta_state if self.enable_meta_thinking else None,
        )

    def evaluate_quality(self, state: ThinkingState) -> float:
        """Calculate overall quality score Q(S_t)."""
        _, metrics = self.operators.evaluate(state)
        return metrics.overall_quality

    def check_convergence(self, history: List[ThinkingState]) -> bool:
        """Check if thinking has converged."""
        if len(history) < 2:
            return False

        # Check quality improvement
        recent_qualities = [s.quality_metrics.overall_quality for s in history[-3:]]
        if len(recent_qualities) >= 2:
            deltas = [
                recent_qualities[i] - recent_qualities[i - 1]
                for i in range(1, len(recent_qualities))
            ]
            return all(abs(d) < 0.01 for d in deltas)

        return False

# ============================================================================
# Section 7: Convenience Functions and Integration
# ============================================================================

@lru_cache(maxsize=1)
def get_thinking_kernel(enable_meta: bool = True) -> ThinkingKernel:
    """Get or create global thinking kernel instance."""
    return ThinkingKernel(enable_meta_thinking=enable_meta)

def quick_think(
    problem: str | dict[str, Any], goal: Optional[str] = None, max_iterations: int = 5
) -> ThinkingResult:
    """
    Quick thinking function for simple problems.

    Usage:
        result = quick_think("How to optimize this code?", goal="find best approach")
        print(result.final_state.belief_state.active_model)
    """
    kernel = get_thinking_kernel()

    # Create simple goal
    goals = []
    if goal:
        goals.append(Goal(id="primary", description=goal, priority=1.0))

    # Initialize state
    state = kernel.initialize_state(goals=goals, initial_workspace=[problem])

    # Think
    return kernel.think(state, max_iterations=max_iterations)

def serialize_thinking_state(state: ThinkingState) -> Dict[str, Any]:
    """Convert thinking state to JSON-serializable dict."""
    return {
        "version": state.version,
        "timestamp": state.timestamp,
        "workspace": {
            "active_items": [
                {"id": i.id, "content": str(i.content), "activation": i.activation}
                for i in state.workspace.active_items
            ],
            "focus_items": state.workspace.focus_items,
            "capacity_limit": state.workspace.capacity_limit,
        },
        "belief_state": {
            "hypotheses": [
                {"id": h.id, "confidence": h.confidence, "status": h.status.value}
                for h in state.belief_state.hypotheses
            ],
            "confidence": state.belief_state.confidence,
            "uncertainty": state.belief_state.uncertainty,
            "active_model": state.belief_state.active_model,
        },
        "goal_state": {
            "primary": state.goal_state.primary_goal.description
            if state.goal_state.primary_goal
            else None,
            "n_secondary": len(state.goal_state.secondary_goals),
        },
        "constraint_state": {
            "n_hard": len(state.constraint_state.hard_constraints),
            "n_soft": len(state.constraint_state.soft_constraints),
            "n_violations": len(state.constraint_state.violations),
        },
        "error_state": {
            "total": state.error_state.total_error(),
            "prediction": state.error_state.prediction_error,
            "coherence": state.error_state.coherence_error,
            "constraint": state.error_state.constraint_error,
            "reasoning": state.error_state.reasoning_error,
        },
        "control_state": {
            "mode": state.control_state.mode.value,
            "iteration": state.control_state.iteration_count,
            "max_iterations": state.control_state.max_iterations,
        },
        "quality_metrics": {
            "overall": state.quality_metrics.overall_quality,
            "coherence": state.quality_metrics.coherence,
            "goal_alignment": state.quality_metrics.goal_alignment,
            "constraint_satisfaction": state.quality_metrics.constraint_satisfaction,
            "predictive_power": state.quality_metrics.predictive_power,
        },
        "transition_state": {
            "last_operation": state.transition_state.last_operation,
            "convergence": state.transition_state.convergence_detected,
            "improvement": state.transition_state.improvement_score,
        },
    }

# ============================================================================
# Section 8: Invariants Validation
# ============================================================================

class ThinkingInvariants:
    """
    Validate thinking invariants (THI01-THI07).
    """

    @staticmethod
    def validate_thi01(state: ThinkingState) -> Tuple[bool, str]:
        """
        THI01: Thinking must operate on internal state, not directly on text.

        Check that workspace items are structured, not raw strings.
        """
        for item in state.workspace.active_items:
            if isinstance(item.content, str) and len(item.content) > 1000:
                return False, f"Raw text detected in workspace item {item.id}"
        return True, "THI01 satisfied"

    @staticmethod
    def validate_thi02(state: ThinkingState) -> Tuple[bool, str]:
        """
        THI02: Every thinking step must be a state transformation.

        Check that last operation modified the state.
        """
        if state.transition_state.last_operation is None:
            return False, "No operation recorded"
        return True, "THI02 satisfied"

    @staticmethod
    def validate_thi03(history: List[ThinkingState]) -> Tuple[bool, str]:
        """
        THI03: State quality should improve across successful transitions.

        Q(S_{t+1}) > Q(S_t)
        """
        if len(history) < 2:
            return True, "Insufficient history"

        recent = history[-5:]
        qualities = [s.quality_metrics.overall_quality for s in recent]

        # Check overall trend
        if qualities[-1] > qualities[0] * 0.9:  # Allow 10% tolerance
            return True, "THI03 satisfied"
        return False, f"Quality degraded: {qualities[0]:.3f} -> {qualities[-1]:.3f}"

    @staticmethod
    def validate_all(
        state: ThinkingState, history: Optional[list[ThinkingState]] = None
    ) -> Dict[str, tuple[bool, str]]:
        """Run all invariant checks."""
        results = {
            "THI01": ThinkingInvariants.validate_thi01(state),
            "THI02": ThinkingInvariants.validate_thi02(state),
        }

        if history:
            results["THI03"] = ThinkingInvariants.validate_thi03(history)

        return results

# ============================================================================
# Section 9: Demo and Testing
# ============================================================================

def demo_thinking_kernel():
    """Demonstrate the thinking kernel capabilities."""
    print("=" * 70)
    print("AMOS THINKING KERNEL DEMONSTRATION")
    print("=" * 70)
    print()

    # Create kernel
    kernel = ThinkingKernel(enable_meta_thinking=True)

    # Define a problem
    problem = {
        "type": "architecture_decision",
        "question": "Should we use microservices or monolith for new API?",
        "constraints": ["team_size: 5", "timeline: 3_months", "scale: medium"],
    }

    # Define goals
    goals = [
        Goal(id="g1", description="Ensure long-term maintainability", priority=0.9),
        Goal(id="g2", description="Minimize initial development time", priority=0.7),
        Goal(id="g3", description="Support future scaling", priority=0.6),
    ]

    # Define constraints
    constraints = [
        Constraint(id="c1", type="resource", description="Team of 5 developers", hard=True),
        Constraint(id="c2", type="time", description="3 month deadline", hard=True),
        Constraint(id="c3", type="logic", description="Must use existing tech stack", hard=False),
    ]

    # Initialize state
    print("Initializing thinking state...")
    state = kernel.initialize_state(
        goals=goals, constraints=constraints, initial_workspace=[problem]
    )
    print(f"Initial quality: {kernel.evaluate_quality(state):.3f}")
    print()

    # Think
    print("Thinking...")
    result = kernel.think(state, max_iterations=8, convergence_threshold=0.02)

    # Report results
    print()
    print("-" * 70)
    print("THINKING RESULTS")
    print("-" * 70)
    print(f"Iterations: {result.iterations}")
    print(f"Converged: {result.converged}")
    print()

    print("Quality Progression:")
    for i, q in enumerate(result.quality_progression):
        marker = "*" if i == len(result.quality_progression) - 1 else " "
        print(f"  {marker} Step {i}: {q:.3f}")
    print()

    print("Final Belief State:")
    print(f"  Active hypotheses: {len(result.final_state.belief_state.hypotheses)}")
    for hyp in result.final_state.belief_state.hypotheses:
        print(f"    - {hyp.id}: confidence={hyp.confidence:.2f}, status={hyp.status.value}")
    print()

    print("Active Model:")
    for key, value in result.final_state.belief_state.active_model.items():
        print(f"  {key}: {value}")
    print()

    print("Error State:")
    print(f"  Total error: {result.final_state.error_state.total_error():.3f}")
    print()

    # Validate invariants
    print("-" * 70)
    print("INVARIANT VALIDATION")
    print("-" * 70)
    validations = ThinkingInvariants.validate_all(result.final_state, result.history)
    for invariant, (passed, message) in validations.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {invariant}: {message}")
    print()

    # Meta-thinking summary
    if result.meta_state:
        print("-" * 70)
        print("META-THINKING SUMMARY")
        print("-" * 70)
        print(f"Policy version: {result.meta_state.policy_version}")
        print(f"Failure signals: {len(result.meta_state.failure_signals)}")
        for sig in result.meta_state.failure_signals:
            print(f"  - {sig.type.value}: {sig.description}")
        print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

    return result

if __name__ == "__main__":
    demo_thinking_kernel()

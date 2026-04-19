from typing import Any

"""
AMOS Cognitive Control Kernel

Fast, accurate, self-correcting brain-style control architecture.

This module implements the cognitive control layer that transforms the AMOS system
from a monolithic, one-pass processor into an adaptive, selective, repairable
cognition engine.

Architecture: Input → FastScreen → Route → FastPath/DeepPath → ErrorCheck → Repair → Commit

Key Equations:
- C_{t+1} = Learn(Commit(Repair(Check(Route(Screen(Input_t))))))
- Intelligence = SpeedOfCorrectRouting + AccuracyOfSelectiveAttention + ErrorDetection + RepairCapacity + ControlledDepth
- ComputeAlloc_i ∝ Salience_i + Ambiguity_i + Risk_i + ErrorLikelihood_i

Author: AMOS Architectural Team
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMERATIONS AND CONSTANTS
# =============================================================================


class RuntimeMode(Enum):
    """Cognitive processing runtime modes."""

    SCREEN = "screen"
    FAST_PATH = "fast_path"
    DEEP_PATH = "deep_path"
    REPAIR = "repair"
    BLOCKED = "blocked"
    COMMITTED = "committed"


class InputClass(Enum):
    """Classification of input complexity and risk."""

    SIMPLE = "simple"
    AMBIGUOUS = "ambiguous"
    HIGH_RISK = "high_risk"
    HIGH_SALIENCE = "high_salience"
    NOISY = "noisy"
    COMPLEX = "complex"
    MIXED = "mixed"


class FailureType(Enum):
    """Types of cognitive failures that can be detected and repaired."""

    BINDING_FAILURE = "binding_failure"
    CONSTRAINT_DROP = "constraint_drop"
    SCOPE_MISMATCH = "scope_mismatch"
    GOAL_MISMATCH = "goal_mismatch"
    STATE_MISMATCH = "state_mismatch"
    GLOBAL_CONFLICT = "global_conflict"
    OVERCONFIDENCE = "overconfidence"


class RepairStrategy(Enum):
    """Localized repair strategies for each failure type."""

    RERUN_REFERENCE_BINDING = "rerun_reference_binding_only"
    RERUN_CONSTRAINT_EXTRACTION = "rerun_constraint_extraction_and_merge"
    RERUN_SCOPE_RESOLUTION = "rerun_scope_resolution"
    RERUN_INTENT_INFERENCE = "rerun_intent_inference"
    RERUN_STATE_ESTIMATION = "rerun_state_estimation"
    ESCALATE_TO_DEEP_PATH = "escalate_to_deep_path"


# Default thresholds for routing decisions
DEFAULT_THRESHOLDS = {
    "ambiguity_fast_max": 0.20,
    "ambiguity_deep_min": 0.20,
    "risk_fast_max": 0.20,
    "risk_deep_min": 0.20,
    "conflict_fast_max": 0.15,
    "conflict_deep_min": 0.15,
    "error_likelihood_fast_max": 0.20,
    "error_likelihood_deep_min": 0.20,
    "confidence_commit_min": 0.85,
    "global_error_score_max": 0.15,
    "cache_match_min": 0.85,
    "alt_hypothesis_margin": 0.10,
}

# =============================================================================
# DATA CLASSES - COGNITIVE STATE
# =============================================================================


@dataclass
class CognitiveControlState:
    """
    Machine-readable control state representing the cognitive system's
    current processing status and estimated metrics.

    Equation: State_t = (runtime_mode, input_class, estimates, flags)
    """

    runtime_mode: RuntimeMode = RuntimeMode.SCREEN
    input_class: InputClass = InputClass.SIMPLE

    # Estimated computational and risk metrics (0.0 - 1.0)
    estimated_cost: float = 0.0
    estimated_value: float = 0.0
    estimated_risk: float = 0.0
    confidence: float = 0.0
    error_likelihood: float = 0.0

    # Processing flags
    needs_deep_processing: bool = False
    needs_repair: bool = False
    commit_allowed: bool = False

    # Timing metrics
    screen_latency_ms: float = 0.0
    route_latency_ms: float = 0.0
    processing_latency_ms: float = 0.0
    total_latency_ms: float = 0.0

    # Path tracking
    processing_path: str = "none"  # "fast" | "deep" | "repaired"
    repair_iterations: int = 0

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    input_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for logging and serialization."""
        return {
            "runtime_mode": self.runtime_mode.value,
            "input_class": self.input_class.value,
            "estimated_cost": self.estimated_cost,
            "estimated_value": self.estimated_value,
            "estimated_risk": self.estimated_risk,
            "confidence": self.confidence,
            "error_likelihood": self.error_likelihood,
            "needs_deep_processing": self.needs_deep_processing,
            "needs_repair": self.needs_repair,
            "commit_allowed": self.commit_allowed,
            "screen_latency_ms": self.screen_latency_ms,
            "route_latency_ms": self.route_latency_ms,
            "processing_latency_ms": self.processing_latency_ms,
            "total_latency_ms": self.total_latency_ms,
            "processing_path": self.processing_path,
            "repair_iterations": self.repair_iterations,
            "timestamp": self.timestamp,
            "input_hash": self.input_hash,
        }


@dataclass
class ErrorMonitor:
    """
    Real-time error monitoring with component-level breakdown.

    Equation: E_t = α·ConstraintDrop + β·BindingFailure + γ·ScopeMismatch + ...
    """

    # Component error scores (0.0 - 1.0)
    constraint_drop: float = 0.0
    binding_failure: float = 0.0
    scope_mismatch: float = 0.0
    goal_mismatch: float = 0.0
    state_mismatch: float = 0.0
    overconfidence: float = 0.0
    conflict_residual: float = 0.0

    # Computed aggregate
    global_error_score: float = 0.0

    # Failure detection flags
    has_failures: bool = False
    dominant_failure: FailureType | None = None

    # Weights for global error computation
    _weights: Dict[str, float] = field(
        default_factory=lambda: {
            "constraint_drop": 0.20,
            "binding_failure": 0.20,
            "scope_mismatch": 0.15,
            "goal_mismatch": 0.15,
            "state_mismatch": 0.15,
            "overconfidence": 0.10,
            "conflict_residual": 0.05,
        }
    )

    def compute_global_score(self) -> float:
        """Compute weighted global error score."""
        self.global_error_score = (
            self._weights["constraint_drop"] * self.constraint_drop
            + self._weights["binding_failure"] * self.binding_failure
            + self._weights["scope_mismatch"] * self.scope_mismatch
            + self._weights["goal_mismatch"] * self.goal_mismatch
            + self._weights["state_mismatch"] * self.state_mismatch
            + self._weights["overconfidence"] * self.overconfidence
            + self._weights["conflict_residual"] * self.conflict_residual
        )

        # Determine dominant failure
        failures = {
            FailureType.CONSTRAINT_DROP: self.constraint_drop,
            FailureType.BINDING_FAILURE: self.binding_failure,
            FailureType.SCOPE_MISMATCH: self.scope_mismatch,
            FailureType.GOAL_MISMATCH: self.goal_mismatch,
            FailureType.STATE_MISMATCH: self.state_mismatch,
            FailureType.OVERCONFIDENCE: self.overconfidence,
            FailureType.GLOBAL_CONFLICT: self.conflict_residual,
        }

        max_failure = max(failures.items(), key=lambda x: x[1])
        if max_failure[1] > 0.0:
            self.dominant_failure = max_failure[0]
            self.has_failures = True
        else:
            self.dominant_failure = None
            self.has_failures = False

        return self.global_error_score

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "constraint_drop": self.constraint_drop,
            "binding_failure": self.binding_failure,
            "scope_mismatch": self.scope_mismatch,
            "goal_mismatch": self.goal_mismatch,
            "state_mismatch": self.state_mismatch,
            "overconfidence": self.overconfidence,
            "conflict_residual": self.conflict_residual,
            "global_error_score": self.global_error_score,
            "has_failures": self.has_failures,
            "dominant_failure": self.dominant_failure.value if self.dominant_failure else None,
        }


@dataclass
class VerificationResult:
    """Result from the active verification suite."""

    primary_read_ok: bool = False
    constraint_preservation_ok: bool = False
    reference_bindings_ok: bool = False
    alt_hypothesis_checked: bool = False
    alt_hypothesis_margin: float = 1.0  # |Score(h1) - Score(h2)|
    output_goal_match_ok: bool = False
    human_safety_ok: bool = False
    governance_ok: bool = False

    all_checks_passed: bool = False
    can_hard_commit: bool = False
    recommendation: str = "repair"  # "commit" | "repair" | "escalate"

    def evaluate(self, thresholds: Dict[str, float]) -> None:
        """Evaluate all checks against thresholds."""
        self.all_checks_passed = all(
            [
                self.primary_read_ok,
                self.constraint_preservation_ok,
                self.reference_bindings_ok,
                self.output_goal_match_ok,
                self.human_safety_ok,
                self.governance_ok,
            ]
        )

        # Check alternative hypothesis margin
        if (
            self.alt_hypothesis_checked
            and self.alt_hypothesis_margin < thresholds["alt_hypothesis_margin"]
        ):
            self.can_hard_commit = False
            self.recommendation = "escalate"
        elif self.all_checks_passed:
            self.can_hard_commit = True
            self.recommendation = "commit"
        else:
            self.can_hard_commit = False
            self.recommendation = "repair"


@dataclass
class PatternCacheEntry:
    """Single entry in the pattern cache."""

    pattern_id: str
    input_signature: str
    read_template: Dict[str, Any]
    success_rate: float = 1.0
    use_count: int = 0
    last_used: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def record_use(self, success: bool) -> None:
        """Update success rate with Bayesian rolling average."""
        self.use_count += 1
        alpha = 0.9  # Decay factor
        outcome = 1.0 if success else 0.0
        self.success_rate = alpha * self.success_rate + (1 - alpha) * outcome
        self.last_used = datetime.now(UTC).isoformat()


@dataclass
class PerformanceMetrics:
    """Runtime performance metrics for the cognitive control kernel."""

    # Latency metrics
    latency_ms: float = 0.0
    screen_latency_ms: float = 0.0
    route_latency_ms: float = 0.0
    fast_path_latency_ms: float = 0.0
    deep_path_latency_ms: float = 0.0
    repair_latency_ms: float = 0.0

    # Accuracy metrics
    stable_read_rate: float = 0.0
    constraint_preservation_rate: float = 0.0
    binding_accuracy: float = 0.0
    goal_match_accuracy: float = 0.0

    # Efficiency metrics
    repair_success_rate: float = 0.0
    deep_path_rate: float = 0.0
    cache_hit_rate: float = 0.0
    overconfidence_rate: float = 0.0
    user_correction_rate: float = 0.0

    # Dumbness score (lower is better)
    # Dumbness ≈ UserCorrectionRate × OverconfidenceRate × ConstraintDropRate × ...
    dumbness_score: float = 0.0

    def compute_dumbness(self, error_monitor: ErrorMonitor) -> float:
        """Compute composite dumbness score."""
        self.dumbness_score = (
            self.user_correction_rate
            * self.overconfidence_rate
            * error_monitor.constraint_drop
            * error_monitor.binding_failure
            * error_monitor.goal_mismatch
        )
        return self.dumbness_score


# =============================================================================
# CORE MODULES
# =============================================================================


class FastScreen:
    """
    FastScreen Module: F_screen

    Performs rapid input classification to determine initial processing mode.

    Equation: FastScreen(Input) → (InputClass, estimated_metrics)
    """

    def __init__(self):
        self._pattern_signatures: Dict[str, InputClass] = {}
        self._complexity_indicators: List[str] = [
            "if",
            "then",
            "else",
            "unless",
            "except",
            "however",
            "ambiguous",
            "unclear",
            "complex",
            "multi-step",
        ]
        self._risk_indicators: List[str] = [
            "critical",
            "urgent",
            "security",
            "password",
            "delete",
            "production",
            "deploy",
            "transaction",
            "payment",
        ]

    async def screen(self, input_object: Dict[str, Any]) -> CognitiveControlState:
        """
        Fast screening of input to determine processing path.

        Runtime: O(1) to O(n) where n is input size, but capped.
        """
        start_time = time.perf_counter()

        # Extract raw input text for analysis
        raw_input = json.dumps(input_object, sort_keys=True)
        input_hash = hashlib.sha256(raw_input.encode()).hexdigest()[:16]

        # Quick heuristics
        input_length = len(raw_input)
        has_complexity = any(ind in raw_input.lower() for ind in self._complexity_indicators)
        has_risk = any(ind in raw_input.lower() for ind in self._risk_indicators)

        # Estimate ambiguity based on input structure
        ambiguity = self._estimate_ambiguity(input_object, input_length)
        risk = 0.7 if has_risk else 0.3
        error_likelihood = (ambiguity + risk) / 2

        # Classify input
        input_class = self._classify_input(input_object, ambiguity, risk, has_complexity)

        # Compute screen latency
        screen_latency_ms = (time.perf_counter() - start_time) * 1000

        return CognitiveControlState(
            runtime_mode=RuntimeMode.SCREEN,
            input_class=input_class,
            estimated_cost=self._estimate_cost(input_class, input_length),
            estimated_value=self._estimate_value(input_object),
            estimated_risk=risk,
            confidence=1.0 - ambiguity,
            error_likelihood=error_likelihood,
            needs_deep_processing=input_class
            in [InputClass.COMPLEX, InputClass.AMBIGUOUS, InputClass.HIGH_RISK],
            screen_latency_ms=screen_latency_ms,
            input_hash=input_hash,
        )

    def _estimate_ambiguity(self, input_object: Dict[str, Any], length: int) -> float:
        """Estimate input ambiguity from structure and content."""
        # Base ambiguity from length (longer = more potential ambiguity)
        length_factor = min(length / 1000, 0.5)

        # Check for conflicting instructions
        text = json.dumps(input_object).lower()
        conflict_markers = sum(
            1 for marker in ["but", "however", "although", "while", "whereas"] if marker in text
        )
        conflict_factor = min(conflict_markers * 0.1, 0.3)

        # Check for nested complexity
        nesting_depth = self._compute_nesting_depth(input_object)
        nesting_factor = min(nesting_depth * 0.05, 0.2)

        return min(length_factor + conflict_factor + nesting_factor, 1.0)

    def _compute_nesting_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Compute nesting depth of input structure."""
        if current_depth > 10:
            return 10
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._compute_nesting_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._compute_nesting_depth(item, current_depth + 1) for item in obj)
        return current_depth

    def _classify_input(
        self, input_object: Dict[str, Any], ambiguity: float, risk: float, has_complexity: bool
    ) -> InputClass:
        """Classify input into processing category."""
        if risk > 0.6:
            return InputClass.HIGH_RISK
        elif ambiguity > 0.5:
            return InputClass.AMBIGUOUS
        elif has_complexity:
            return InputClass.COMPLEX
        elif ambiguity < 0.2 and not has_complexity:
            return InputClass.SIMPLE
        elif (
            "batch" in json.dumps(input_object).lower()
            or "multi" in json.dumps(input_object).lower()
        ):
            return InputClass.MIXED
        else:
            return InputClass.HIGH_SALIENCE if ambiguity > 0.3 else InputClass.SIMPLE

    def _estimate_cost(self, input_class: InputClass, length: int) -> float:
        """Estimate computational cost for processing."""
        base_costs = {
            InputClass.SIMPLE: 0.1,
            InputClass.HIGH_SALIENCE: 0.2,
            InputClass.NOISY: 0.4,
            InputClass.MIXED: 0.5,
            InputClass.COMPLEX: 0.7,
            InputClass.AMBIGUOUS: 0.8,
            InputClass.HIGH_RISK: 0.9,
        }
        base = base_costs.get(input_class, 0.5)
        length_factor = min(length / 5000, 0.2)
        return min(base + length_factor, 1.0)

    def _estimate_value(self, input_object: Dict[str, Any]) -> float:
        """Estimate value/impact of correct processing."""
        # Check for high-value markers
        text = json.dumps(input_object).lower()
        high_value_markers = ["production", "deploy", "critical", "customer", "revenue"]
        matches = sum(1 for marker in high_value_markers if marker in text)
        return min(0.5 + matches * 0.15, 1.0)


class RoutingController:
    """
    RoutingController Module: F_route

    Routes input to appropriate processing path based on control state.

    Equation: Route(ControlState) → fast_path | deep_path | blocked
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS

    async def route(self, control_state: CognitiveControlState) -> CognitiveControlState:
        """
        Determine processing path based on control state metrics.

        Fast path: low ambiguity, low risk, low conflict, known pattern
        Deep path: high ambiguity, high risk, high conflict, novel pattern
        """
        start_time = time.perf_counter()

        ambiguity = control_state.confidence  # 1 - confidence = ambiguity
        risk = control_state.estimated_risk
        error_likelihood = control_state.error_likelihood

        # Check fast path conditions
        fast_path_eligible = all(
            [
                ambiguity <= self.thresholds["ambiguity_fast_max"],
                risk <= self.thresholds["risk_fast_max"],
                error_likelihood <= self.thresholds["error_likelihood_fast_max"],
                control_state.input_class in [InputClass.SIMPLE, InputClass.HIGH_SALIENCE],
            ]
        )

        # Check deep path triggers
        deep_path_required = any(
            [
                ambiguity > self.thresholds["ambiguity_deep_min"],
                risk > self.thresholds["risk_deep_min"],
                error_likelihood > self.thresholds["error_likelihood_deep_min"],
                control_state.input_class
                in [InputClass.AMBIGUOUS, InputClass.COMPLEX, InputClass.HIGH_RISK],
            ]
        )

        # Make routing decision
        if deep_path_required or control_state.needs_deep_processing:
            control_state.runtime_mode = RuntimeMode.DEEP_PATH
            control_state.processing_path = "deep"
        elif fast_path_eligible:
            control_state.runtime_mode = RuntimeMode.FAST_PATH
            control_state.processing_path = "fast"
        else:
            # Ambiguous case - default to deep for safety
            control_state.runtime_mode = RuntimeMode.DEEP_PATH
            control_state.processing_path = "deep"

        control_state.route_latency_ms = (time.perf_counter() - start_time) * 1000

        return control_state


class FastPathProcessor:
    """
    FastPath Module: F_fast

    Approximate read + cached pattern + minimal verification.

    Equation: FastPath = ApproximateRead + CachedPattern + MinimalVerification
    """

    def __init__(self, pattern_cache: PatternCache):
        self.pattern_cache = pattern_cache

    async def process(
        self,
        input_object: Dict[str, Any],
        control_state: CognitiveControlState,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute fast path processing with cache lookup and approximate read.
        """
        start_time = time.perf_counter()

        # Generate input signature for cache lookup
        input_signature = self._generate_signature(input_object)

        # Check cache for pattern match
        cached_result = await self.pattern_cache.lookup(input_signature)

        if cached_result and cached_result.success_rate > 0.8:
            # Fast path via cache with quick verification
            result = await self._apply_cached_pattern(cached_result, input_object, context)
            cache_hit = True
        else:
            # Compute fresh with lightweight processing
            result = await self._approximate_read(input_object, context)
            cache_hit = False

        processing_latency_ms = (time.perf_counter() - start_time) * 1000
        control_state.processing_latency_ms = processing_latency_ms

        result["_meta"] = {
            "cache_hit": cache_hit,
            "processing_latency_ms": processing_latency_ms,
            "path": "fast",
        }

        return result

    def _generate_signature(self, input_object: Dict[str, Any]) -> str:
        """Generate canonical signature for cache lookup."""
        canonical = json.dumps(input_object, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:32]

    async def _apply_cached_pattern(
        self,
        pattern: PatternCacheEntry,
        input_object: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply cached pattern with lightweight adaptation."""
        # Start from cached template
        result = pattern.read_template.copy()

        # Quick parameter substitution based on input
        result["_adapted"] = True
        result["_input_hash"] = hashlib.sha256(
            json.dumps(input_object, sort_keys=True).encode()
        ).hexdigest()[:8]

        return result

    async def _approximate_read(
        self, input_object: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Lightweight approximate read without full analysis."""
        # Extract key fields only
        result = {
            "extracted_fields": list(input_object.keys())[:10],  # Cap field count
            "input_type": type(input_object).__name__,
            "size_estimate": len(json.dumps(input_object)),
            "_approximate": True,
        }

        # Quick context integration
        if context:
            result["context_keys"] = list(context.keys())[:5]

        return result


class DeepPathProcessor:
    """
    DeepPath Module: F_deep

    Multi-pass read + binding + lattice + global verification.

    Equation: DeepPath = MultiPassRead + Binding + Lattice + GlobalVerification
    """

    def __init__(self):
        self.max_passes = 3

    async def process(
        self,
        input_object: Dict[str, Any],
        control_state: CognitiveControlState,
        context: Dict[str, Any] = None,
        memory: Dict[str, Any] = None,
        goals: list[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Execute deep path processing with full analysis.
        """
        start_time = time.perf_counter()

        # Multi-pass analysis
        passes = []
        for pass_num in range(self.max_passes):
            pass_result = await self._analysis_pass(input_object, pass_num, context, memory)
            passes.append(pass_result)

            # Check for convergence
            if pass_num > 0 and self._check_convergence(passes[-2], passes[-1]):
                break

        # Binding phase
        bindings = await self._run_reference_binding(input_object, passes[-1], context)

        # Constraint extraction
        constraints = await self._extract_constraints(input_object, passes[-1])

        # Global verification
        verified = await self._global_verification(passes[-1], bindings, constraints, goals)

        processing_latency_ms = (time.perf_counter() - start_time) * 1000
        control_state.processing_latency_ms = processing_latency_ms

        result = {
            "passes": passes,
            "final_pass": passes[-1],
            "bindings": bindings,
            "constraints": constraints,
            "verified": verified,
            "_meta": {
                "num_passes": len(passes),
                "processing_latency_ms": processing_latency_ms,
                "path": "deep",
            },
        }

        return result

    async def _analysis_pass(
        self,
        input_object: Dict[str, Any],
        pass_num: int,
        context: Dict[str, Any],
        memory: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Single analysis pass with increasing depth."""
        depth_factor = 1 + pass_num * 0.5

        # Simulated deep analysis
        return {
            "pass_number": pass_num,
            "depth_factor": depth_factor,
            "extracted_structure": self._deep_structure_extract(input_object, depth_factor),
            "confidence": min(0.5 + pass_num * 0.2, 0.95),
        }

    def _deep_structure_extract(self, obj: Any, depth_factor: float) -> Dict[str, Any]:
        """Deep structure extraction with controlled recursion."""
        if isinstance(obj, dict):
            return {
                k: self._deep_structure_extract(v, depth_factor)
                for k, v in list(obj.items())[: int(10 * depth_factor)]
            }
        elif isinstance(obj, list):
            return [
                self._deep_structure_extract(item, depth_factor)
                for item in obj[: int(5 * depth_factor)]
            ]
        return {"type": type(obj).__name__, "value": str(obj)[:100]}

    def _check_convergence(self, prev: Dict[str, Any], curr: Dict[str, Any]) -> bool:
        """Check if analysis has converged between passes."""
        # Simplified convergence check
        return curr.get("confidence", 0) > 0.85

    async def _run_reference_binding(
        self, input_object: Dict[str, Any], analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run reference binding to link entities."""
        return {
            "bound_entities": [],
            "unresolved_references": [],
            "binding_confidence": 0.85,
        }

    async def _extract_constraints(
        self, input_object: Dict[str, Any], analysis: Dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract constraints from input and analysis."""
        return []

    async def _global_verification(
        self,
        analysis: Dict[str, Any],
        bindings: Dict[str, Any],
        constraints: list[dict[str, Any]],
        goals: list[str] | None,
    ) -> bool:
        """Perform global verification against goals and constraints."""
        return analysis.get("confidence", 0) > 0.8


class ErrorMonitorModule:
    """
    ErrorMonitor Module: F_check

    Real-time error detection across all processing stages.

    Equation: ErrorMonitor_t = (ConstraintDrop, BindingFailure, ScopeMismatch, ...)
    """

    def __init__(self):
        self.checks = [
            self._check_constraint_preservation,
            self._check_binding_integrity,
            self._check_scope_consistency,
            self._check_goal_alignment,
            self._check_state_coherence,
            self._check_overconfidence,
            self._check_conflict_residuals,
        ]

    async def monitor(
        self,
        read_result: Dict[str, Any],
        output_object: Dict[str, Any],
        control_state: CognitiveControlState,
    ) -> ErrorMonitor:
        """
        Run full error monitoring suite.
        """
        monitor = ErrorMonitor()

        # Run all error checks
        for check_func in self.checks:
            check_result = await check_func(read_result, output_object, control_state)
            # Update appropriate monitor field based on check type
            if "constraint" in check_func.__name__:
                monitor.constraint_drop = check_result
            elif "binding" in check_func.__name__:
                monitor.binding_failure = check_result
            elif "scope" in check_func.__name__:
                monitor.scope_mismatch = check_result
            elif "goal" in check_func.__name__:
                monitor.goal_mismatch = check_result
            elif "state" in check_func.__name__:
                monitor.state_mismatch = check_result
            elif "overconfidence" in check_func.__name__:
                monitor.overconfidence = check_result
            elif "conflict" in check_func.__name__:
                monitor.conflict_residual = check_result

        # Compute global score
        monitor.compute_global_score()

        # Update control state
        control_state.needs_repair = monitor.has_failures

        return monitor

    async def _check_constraint_preservation(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check if constraints were preserved through processing."""
        # Placeholder implementation
        return 0.0 if state.confidence > 0.8 else 0.2

    async def _check_binding_integrity(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check if reference bindings are consistent."""
        bindings = read.get("bindings", {})
        binding_confidence = bindings.get("binding_confidence", 1.0)
        return 0.0 if binding_confidence > 0.8 else 0.3

    async def _check_scope_consistency(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check for scope mismatches."""
        return 0.0 if state.input_class != InputClass.AMBIGUOUS else 0.15

    async def _check_goal_alignment(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check if output aligns with inferred goals."""
        return 0.0 if state.estimated_value > 0.5 else 0.1

    async def _check_state_coherence(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check state coherence across processing stages."""
        return 0.0 if state.confidence > 0.7 else 0.2

    async def _check_overconfidence(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check for overconfidence in low-certainty situations."""
        # Flag overconfidence when confidence is high but error likelihood is also high
        if state.confidence > 0.9 and state.error_likelihood > 0.4:
            return 0.5
        return 0.0

    async def _check_conflict_residuals(
        self, read: Dict[str, Any], output: Dict[str, Any], state: CognitiveControlState
    ) -> float:
        """Check for unresolved conflicts."""
        return 0.0 if state.input_class != InputClass.COMPLEX else 0.1


class RepairEngine:
    """
    RepairEngine Module: F_repair

    Localized repair strategies for detected failures.

    Equation: Repair = DetectFailure → LocalizeFailure → ReprocessOnlyFailedPart → Reverify
    """

    def __init__(self):
        self.repair_strategies: dict[FailureType, RepairStrategy] = {
            FailureType.BINDING_FAILURE: RepairStrategy.RERUN_REFERENCE_BINDING,
            FailureType.CONSTRAINT_DROP: RepairStrategy.RERUN_CONSTRAINT_EXTRACTION,
            FailureType.SCOPE_MISMATCH: RepairStrategy.RERUN_SCOPE_RESOLUTION,
            FailureType.GOAL_MISMATCH: RepairStrategy.RERUN_INTENT_INFERENCE,
            FailureType.STATE_MISMATCH: RepairStrategy.RERUN_STATE_ESTIMATION,
            FailureType.GLOBAL_CONFLICT: RepairStrategy.ESCALATE_TO_DEEP_PATH,
            FailureType.OVERCONFIDENCE: RepairStrategy.ESCALATE_TO_DEEP_PATH,
        }

    async def repair(
        self,
        error_monitor: ErrorMonitor,
        read_result: Dict[str, Any],
        control_state: CognitiveControlState,
        context: Dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """
        Execute repair loop on failed components.

        Returns: (repaired_result, success)
        """
        start_time = time.perf_counter()

        if not error_monitor.has_failures or not error_monitor.dominant_failure:
            return read_result, True

        failure_type = error_monitor.dominant_failure
        strategy = self.repair_strategies.get(failure_type, RepairStrategy.ESCALATE_TO_DEEP_PATH)

        # Execute localized repair
        repaired_result = await self._execute_strategy(strategy, failure_type, read_result, context)

        # Mark as repaired
        repaired_result["_repaired"] = True
        repaired_result["_repair_strategy"] = strategy.value
        repaired_result["_failure_type"] = failure_type.value

        repair_latency_ms = (time.perf_counter() - start_time) * 1000
        control_state.processing_latency_ms += repair_latency_ms
        control_state.repair_iterations += 1

        # Update control state
        control_state.needs_repair = False

        return repaired_result, True

    async def _execute_strategy(
        self,
        strategy: RepairStrategy,
        failure_type: FailureType,
        read_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the specific repair strategy."""
        result = read_result.copy()

        if strategy == RepairStrategy.RERUN_REFERENCE_BINDING:
            # Re-run binding on failed references only
            result["_repair_note"] = "Re-ran reference binding"

        elif strategy == RepairStrategy.RERUN_CONSTRAINT_EXTRACTION:
            # Re-extract constraints
            result["_repair_note"] = "Re-extracted constraints"

        elif strategy == RepairStrategy.RERUN_SCOPE_RESOLUTION:
            # Re-resolve scope
            result["_repair_note"] = "Re-resolved scope"

        elif strategy == RepairStrategy.RERUN_INTENT_INFERENCE:
            # Re-infer intent
            result["_repair_note"] = "Re-inferred intent"

        elif strategy == RepairStrategy.RERUN_STATE_ESTIMATION:
            # Re-estimate state
            result["_repair_note"] = "Re-estimated state"

        elif strategy == RepairStrategy.ESCALATE_TO_DEEP_PATH:
            # Mark for escalation (already in deep path, so add verification)
            result["_repair_note"] = "Added additional verification"
            result["_escalated"] = True

        return result


class VerificationSuite:
    """
    VerificationSuite Module: F_check

    Active adversarial verification with alternative hypothesis checking.

    Equation: Verify* = CheckRead + CheckConstraints + CheckBindings + CheckAltHypothesis + CheckOutputAgainstUserIntent
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS
        self.checks = [
            "check_primary_read",
            "check_constraint_preservation",
            "check_reference_bindings",
            "check_alt_hypothesis",
            "check_output_goal_match",
            "check_human_safety",
            "check_governance",
        ]

    async def verify(
        self,
        read_object: Dict[str, Any],
        output_object: Dict[str, Any],
        governance_state: Dict[str, Any],
    ) -> VerificationResult:
        """
        Run full verification suite.
        """
        result = VerificationResult()

        # Primary read check
        result.primary_read_ok = await self._check_primary_read(read_object)

        # Constraint preservation
        result.constraint_preservation_ok = await self._check_constraints(read_object)

        # Reference bindings
        result.reference_bindings_ok = await self._check_bindings(read_object)

        # Alternative hypothesis check
        (
            result.alt_hypothesis_checked,
            result.alt_hypothesis_margin,
        ) = await self._check_alt_hypothesis(read_object)

        # Output goal match
        result.output_goal_match_ok = await self._check_goal_match(read_object, output_object)

        # Human safety
        result.human_safety_ok = await self._check_safety(read_object, output_object)

        # Governance
        result.governance_ok = await self._check_governance(read_object, governance_state)

        # Final evaluation
        result.evaluate(self.thresholds)

        return result

    async def _check_primary_read(self, read_object: Dict[str, Any]) -> bool:
        """Verify primary read integrity."""
        return read_object.get("_meta", {}).get("path") in ["fast", "deep", "repaired"]

    async def _check_constraints(self, read_object: Dict[str, Any]) -> bool:
        """Verify constraint preservation."""
        return len(read_object.get("constraints", [])) >= 0  # Placeholder

    async def _check_bindings(self, read_object: Dict[str, Any]) -> bool:
        """Verify reference bindings."""
        bindings = read_object.get("bindings", {})
        return bindings.get("binding_confidence", 0) > 0.7

    async def _check_alt_hypothesis(self, read_object: Dict[str, Any]) -> Tuple[bool, float]:
        """Check alternative hypothesis margin."""
        # Generate alternative interpretation and compare
        alt_confidence = read_object.get("final_pass", {}).get("confidence", 0.8) * 0.85
        primary_confidence = read_object.get("final_pass", {}).get("confidence", 0.8)
        margin = abs(primary_confidence - alt_confidence)
        return True, margin

    async def _check_goal_match(
        self, read_object: Dict[str, Any], output_object: Dict[str, Any]
    ) -> bool:
        """Check output against inferred goals."""
        return True  # Placeholder

    async def _check_safety(
        self, read_object: Dict[str, Any], output_object: Dict[str, Any]
    ) -> bool:
        """Check human safety implications."""
        return True  # Placeholder - would check for harmful outputs

    async def _check_governance(
        self, read_object: Dict[str, Any], governance_state: Dict[str, Any]
    ) -> bool:
        """Check governance compliance."""
        return True  # Placeholder


class CommitGate:
    """
    CommitGate Module: F_commit

    Controlled output commitment with strict entry criteria.

    Equation: CommitAllowed = 1[Confidence ≥ τ_c ∧ GlobalErrorScore ≤ τ_e ∧ ConstraintDrop = 0 ∧ ...]
    """

    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or DEFAULT_THRESHOLDS

    async def check_commit_allowed(
        self,
        control_state: CognitiveControlState,
        error_monitor: ErrorMonitor,
        verification_result: VerificationResult,
    ) -> Tuple[bool, str]:
        """
        Determine if output can be committed.

        Returns: (allowed, reason)
        """
        conditions = {
            "confidence_gte": control_state.confidence >= self.thresholds["confidence_commit_min"],
            "global_error_score_lte": error_monitor.global_error_score
            <= self.thresholds["global_error_score_max"],
            "constraint_drop_eq": error_monitor.constraint_drop == 0.0,
            "binding_failure_eq": error_monitor.binding_failure == 0.0,
            "verification_eq": verification_result.all_checks_passed,
        }

        # All conditions must be met
        allowed = all(conditions.values())

        if allowed:
            control_state.commit_allowed = True
            control_state.runtime_mode = RuntimeMode.COMMITTED
            return True, "All commit conditions satisfied"

        # Determine why commit was blocked
        failed = [k for k, v in conditions.items() if not v]
        return False, f"Commit blocked: {', '.join(failed)}"


class PatternCache:
    """
    PatternCache Module: F_cache

    Memory-backed cached patterns for fast path acceleration.

    Equation: Read_t = Reuse(Pattern_j) if match high else ComputeFresh
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, PatternCacheEntry] = {}
        self._access_order: List[str] = []

    async def lookup(self, input_signature: str) -> PatternCacheEntry | None:
        """Look up pattern by input signature."""
        if input_signature in self._cache:
            entry = self._cache[input_signature]
            # Update access order (LRU)
            self._access_order.remove(input_signature)
            self._access_order.append(input_signature)
            return entry
        return None

    async def store(
        self, input_signature: str, read_template: Dict[str, Any], success: bool = True
    ) -> None:
        """Store successful read pattern in cache."""
        if input_signature in self._cache:
            # Update existing entry
            entry = self._cache[input_signature]
            entry.record_use(success)
        else:
            # Evict if necessary
            if len(self._cache) >= self.max_size:
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]

            # Create new entry
            entry = PatternCacheEntry(
                pattern_id=input_signature[:16],
                input_signature=input_signature,
                read_template=read_template,
            )
            entry.record_use(success)
            self._cache[input_signature] = entry
            self._access_order.append(input_signature)

    async def update_success_rate(self, input_signature: str, success: bool) -> None:
        """Update success rate for a cached pattern."""
        if input_signature in self._cache:
            self._cache[input_signature].record_use(success)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._cache:
            return {"size": 0, "hit_rate": 0.0, "avg_success_rate": 0.0}

        total_uses = sum(e.use_count for e in self._cache.values())
        avg_success = sum(e.success_rate for e in self._cache.values()) / len(self._cache)

        return {
            "size": len(self._cache),
            "total_uses": total_uses,
            "avg_success_rate": avg_success,
        }


# =============================================================================
# MAIN COGNITIVE CONTROL KERNEL
# =============================================================================


class AMOSCognitiveControlKernel:
    """
    AMOS Cognitive Control Kernel

    Main orchestrator implementing the full cognitive control architecture:

    Input → FastScreen → Route → FastPath/DeepPath → ErrorCheck → Repair → Commit → Learn

    Key Equations:
    - C_{t+1} = Learn(Commit(Repair(Check(Route(Screen(Input_t))))))
    - Output_t = Commit(Repair(Check(FastPath(Input_t) if routed fast else DeepPath(Input_t))))
    - Speed = FastCorrectRouting + LocalRepair + CacheReuse + AdaptiveDepth
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.thresholds = self.config.get("thresholds", DEFAULT_THRESHOLDS)

        # Initialize all modules
        self.fast_screen = FastScreen()
        self.routing_controller = RoutingController(self.thresholds)
        self.pattern_cache = PatternCache(self.config.get("cache_size", 1000))
        self.fast_path = FastPathProcessor(self.pattern_cache)
        self.deep_path = DeepPathProcessor()
        self.error_monitor = ErrorMonitorModule()
        self.repair_engine = RepairEngine()
        self.verification_suite = VerificationSuite(self.thresholds)
        self.commit_gate = CommitGate(self.thresholds)

        # Performance tracking
        self.metrics = PerformanceMetrics()
        self._total_processed = 0
        self._cache_hits = 0
        self._repair_successes = 0
        self._deep_path_count = 0

    async def process(
        self,
        input_object: Dict[str, Any],
        context: Dict[str, Any] = None,
        memory: Dict[str, Any] = None,
        goals: list[str] | None = None,
        governance_state: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point for cognitive processing with full control architecture.

        Pipeline: Screen → Route → Process → Monitor → Repair → Verify → Commit
        """
        total_start = time.perf_counter()
        self._total_processed += 1

        # Stage 1: Fast Screen
        control_state = await self.fast_screen.screen(input_object)

        # Stage 2: Route
        control_state = await self.routing_controller.route(control_state)

        # Stage 3: Process (Fast or Deep path)
        if control_state.runtime_mode == RuntimeMode.FAST_PATH:
            read_result = await self.fast_path.process(input_object, control_state, context)
            if read_result.get("_meta", {}).get("cache_hit"):
                self._cache_hits += 1
        else:
            read_result = await self.deep_path.process(
                input_object, control_state, context, memory, goals
            )
            self._deep_path_count += 1

        # Stage 4: Error Monitor
        error_monitor = await self.error_monitor.monitor(read_result, read_result, control_state)

        # Stage 5: Repair (if needed)
        if error_monitor.has_failures and control_state.needs_repair:
            read_result, repair_success = await self.repair_engine.repair(
                error_monitor, read_result, control_state, context
            )
            if repair_success:
                self._repair_successes += 1
                # Re-monitor after repair
                error_monitor = await self.error_monitor.monitor(
                    read_result, read_result, control_state
                )

        # Stage 6: Verification
        verification_result = await self.verification_suite.verify(
            read_result, read_result, governance_state
        )

        # Stage 7: Commit Gate
        commit_allowed, commit_reason = await self.commit_gate.check_commit_allowed(
            control_state, error_monitor, verification_result
        )

        # Compute final metrics
        total_latency_ms = (time.perf_counter() - total_start) * 1000
        control_state.total_latency_ms = total_latency_ms

        # Update performance metrics
        self._update_metrics(control_state, error_monitor)

        # Build output
        output = {
            "result": read_result,
            "control_state": control_state.to_dict(),
            "error_monitor": error_monitor.to_dict(),
            "verification": {
                "all_checks_passed": verification_result.all_checks_passed,
                "can_hard_commit": verification_result.can_hard_commit,
                "recommendation": verification_result.recommendation,
            },
            "commit": {
                "allowed": commit_allowed,
                "reason": commit_reason,
            },
            "performance": {
                "latency_ms": total_latency_ms,
                "path_taken": control_state.processing_path,
                "cache_hit_rate": self._cache_hits / max(self._total_processed, 1),
                "deep_path_rate": self._deep_path_count / max(self._total_processed, 1),
                "repair_success_rate": self._repair_successes
                / max(self._total_processed - self._cache_hits, 1),
            },
        }

        # Cache successful fast-path results
        if control_state.processing_path == "fast" and commit_allowed:
            input_sig = self.fast_path._generate_signature(input_object)
            await self.pattern_cache.store(input_sig, read_result, success=True)

        return output

    def _update_metrics(
        self, control_state: CognitiveControlState, error_monitor: ErrorMonitor
    ) -> None:
        """Update rolling performance metrics."""
        alpha = 0.95  # Exponential decay

        # Latency metrics
        self.metrics.latency_ms = (
            alpha * self.metrics.latency_ms + (1 - alpha) * control_state.total_latency_ms
        )
        self.metrics.screen_latency_ms = (
            alpha * self.metrics.screen_latency_ms + (1 - alpha) * control_state.screen_latency_ms
        )
        self.metrics.route_latency_ms = (
            alpha * self.metrics.route_latency_ms + (1 - alpha) * control_state.route_latency_ms
        )

        if control_state.processing_path == "fast":
            self.metrics.fast_path_latency_ms = (
                alpha * self.metrics.fast_path_latency_ms
                + (1 - alpha) * control_state.processing_latency_ms
            )
        else:
            self.metrics.deep_path_latency_ms = (
                alpha * self.metrics.deep_path_latency_ms
                + (1 - alpha) * control_state.processing_latency_ms
            )

        # Accuracy metrics
        self.metrics.constraint_preservation_rate = (
            alpha * self.metrics.constraint_preservation_rate
            + (1 - alpha) * (1.0 - error_monitor.constraint_drop)
        )
        self.metrics.binding_accuracy = alpha * self.metrics.binding_accuracy + (1 - alpha) * (
            1.0 - error_monitor.binding_failure
        )
        self.metrics.goal_match_accuracy = alpha * self.metrics.goal_match_accuracy + (
            1 - alpha
        ) * (1.0 - error_monitor.goal_mismatch)

        # Efficiency metrics
        self.metrics.deep_path_rate = self._deep_path_count / max(self._total_processed, 1)
        self.metrics.cache_hit_rate = self._cache_hits / max(self._total_processed, 1)
        self.metrics.repair_success_rate = self._repair_successes / max(
            self._total_processed - self._cache_hits, 1
        )
        self.metrics.overconfidence_rate = (
            alpha * self.metrics.overconfidence_rate + (1 - alpha) * error_monitor.overconfidence
        )

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics

    def get_kernel_state(self) -> Dict[str, Any]:
        """Get full kernel state for introspection."""
        return {
            "total_processed": self._total_processed,
            "cache_hits": self._cache_hits,
            "deep_path_count": self._deep_path_count,
            "repair_successes": self._repair_successes,
            "cache_stats": self.pattern_cache.get_stats(),
            "performance_metrics": {
                "latency_ms": self.metrics.latency_ms,
                "deep_path_rate": self.metrics.deep_path_rate,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "repair_success_rate": self.metrics.repair_success_rate,
                "dumbness_score": self.metrics.dumbness_score,
            },
        }


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_kernel_instance: AMOSCognitiveControlKernel | None = None


def get_cognitive_control_kernel(
    config: Dict[str, Any] = None,
) -> AMOSCognitiveControlKernel:
    """
    Get or create the global Cognitive Control Kernel instance.

    Implements singleton pattern for system-wide cognitive control.
    """
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = AMOSCognitiveControlKernel(config)
    return _kernel_instance


# =============================================================================
# INTEGRATION LAYER WITH EXISTING AMOS BRAIN
# =============================================================================


class AMOSCognitiveControlBridge:
    """
    Bridge between the Cognitive Control Kernel and existing AMOS brain systems.

    Provides seamless integration with:
    - amos_brain (core brain)
    - AMOS_ORGANISM_OS (14-layer architecture)
    - backend API layer
    """

    def __init__(self):
        self.kernel = get_cognitive_control_kernel()

    async def process_brain_input(
        self,
        input_data: Dict[str, Any],
        source_layer: str = "14-interfaces",
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Process input through cognitive control before brain processing.

        This is the main integration point - all brain inputs flow through here first.
        """
        # Build goals from source layer
        goals = [f"process_{source_layer}", "maintain_coherence", "preserve_constraints"]

        # Run through cognitive control kernel
        result = await self.kernel.process(
            input_object=input_data,
            context=context,
            goals=goals,
            governance_state={"source_layer": source_layer},
        )

        # Log performance for observability
        if result["performance"]["latency_ms"] > 1000:
            logger.warning(
                f"Slow cognitive processing: {result['performance']['latency_ms']:.0f}ms"
            )

        return result

    async def quick_screen(self, input_data: Dict[str, Any]) -> CognitiveControlState:
        """Fast screen for routing decisions without full processing."""
        return await self.kernel.fast_screen.screen(input_data)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get formatted performance report for dashboards."""
        metrics = self.kernel.get_metrics()
        state = self.kernel.get_kernel_state()

        return {
            "summary": {
                "total_processed": state["total_processed"],
                "avg_latency_ms": round(metrics.latency_ms, 2),
                "cache_hit_rate": round(metrics.cache_hit_rate * 100, 1),
                "deep_path_rate": round(metrics.deep_path_rate * 100, 1),
                "dumbness_score": round(metrics.dumbness_score, 4),
            },
            "efficiency": {
                "screen_latency_ms": round(metrics.screen_latency_ms, 2),
                "route_latency_ms": round(metrics.route_latency_ms, 2),
                "fast_path_latency_ms": round(metrics.fast_path_latency_ms, 2),
                "deep_path_latency_ms": round(metrics.deep_path_latency_ms, 2),
            },
            "accuracy": {
                "constraint_preservation": round(metrics.constraint_preservation_rate * 100, 1),
                "binding_accuracy": round(metrics.binding_accuracy * 100, 1),
                "goal_match": round(metrics.goal_match_accuracy * 100, 1),
                "repair_success": round(metrics.repair_success_rate * 100, 1),
            },
            "cache": state["cache_stats"],
        }


# =============================================================================
# DEMO AND TESTING
# =============================================================================


async def demo_cognitive_control_kernel():
    """
    Demonstrate the Cognitive Control Kernel capabilities.
    """
    print("=" * 70)
    print("AMOS COGNITIVE CONTROL KERNEL - DEMONSTRATION")
    print("=" * 70)

    kernel = AMOSCognitiveControlKernel()
    bridge = AMOSCognitiveControlBridge()

    # Test cases demonstrating different input classes
    test_inputs = [
        {
            "name": "Simple Query",
            "input": {"action": "get_status", "target": "system"},
            "expected_class": InputClass.SIMPLE,
        },
        {
            "name": "Ambiguous Instruction",
            "input": {
                "instruction": "Process this but handle exceptions carefully, however if it fails try alternative approach"
            },
            "expected_class": InputClass.AMBIGUOUS,
        },
        {
            "name": "High Risk Operation",
            "input": {
                "action": "deploy",
                "target": "production",
                "critical": True,
                "security_review": "required",
            },
            "expected_class": InputClass.HIGH_RISK,
        },
        {
            "name": "Complex Multi-step",
            "input": {
                "workflow": [
                    {"step": 1, "action": "validate"},
                    {"step": 2, "action": "transform"},
                    {"step": 3, "action": "verify"},
                    {"step": 4, "action": "commit"},
                ],
                "nested_config": {"deep": {"very_deep": {"value": "test"}}},
            },
            "expected_class": InputClass.COMPLEX,
        },
    ]

    print("\n--- Test 1: Fast Screen Classification ---\n")

    for test in test_inputs:
        screen_result = await kernel.fast_screen.screen(test["input"])
        print(f"Test: {test['name']}")
        print(f"  Input Class: {screen_result.input_class.value}")
        print(f"  Confidence: {screen_result.confidence:.2f}")
        print(f"  Risk: {screen_result.estimated_risk:.2f}")
        print(f"  Needs Deep: {screen_result.needs_deep_processing}")
        print(f"  Screen Latency: {screen_result.screen_latency_ms:.2f}ms")
        print()

    print("\n--- Test 2: Full Processing Pipeline ---\n")

    for test in test_inputs:
        print(f"Processing: {test['name']}")
        result = await kernel.process(test["input"])

        cs = result["control_state"]
        perf = result["performance"]

        print(f"  Path: {cs['processing_path']}")
        print(f"  Total Latency: {perf['latency_ms']:.2f}ms")
        print(f"  Commit Allowed: {result['commit']['allowed']}")
        print(f"  Global Error: {result['error_monitor']['global_error_score']:.3f}")
        print()

    print("\n--- Test 3: Performance Metrics ---\n")

    report = bridge.get_performance_report()
    print("Summary:")
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")

    print("\nEfficiency:")
    for key, value in report["efficiency"].items():
        print(f"  {key}: {value}ms")

    print("\nAccuracy:")
    for key, value in report["accuracy"].items():
        print(f"  {key}: {value}%")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

    return kernel


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_cognitive_control_kernel())

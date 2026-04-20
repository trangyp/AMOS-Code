"""
Compiled Numeric Kernel (CNK)

Separates semantic thinking from numeric calculation.

The CNK provides:
- Vectorized numeric operations (no Python loop overhead)
- Pre-compiled transition functions (no dynamic lookup)
- Cached projections (no reconstruction)
- Fast invariant evaluation (early rejection)

AMOS Equation:
    X_{t+1} = CNK_transition(X_t, U_t, Y_t)

Where CNK_transition is:
    1. Hash lookup (O(1)) - no reinterpretation
    2. Vectorized compute - no Python hot loop overhead
    3. Fast Gamma gate - invariants checked BEFORE branching
    4. Direct commit - no reconstruction

This is the "fast path" that bypasses semantic interpretation.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Optional, Protocol

import numpy as np

# ============================================================================
# Core Protocols
# ============================================================================


class NumericTransition(Protocol):
    """Protocol for compiled numeric transitions."""

    def __call__(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState: ...


class InvariantCheck(Protocol):
    """Protocol for fast invariant evaluation."""

    def __call__(self, state: CompiledState, action: NumericAction) -> InvariantResult: ...


# ============================================================================
# Data Structures
# ============================================================================


@dataclass(frozen=True)
class CompiledState:
    """
    Canonical compressed state representation.

    Uses __slots__ for memory efficiency and frozen for immutability.
    State transitions return new CompiledState instances.

    Canonical form: X_t = (hash, tensor, metadata)
    """

    # Canonical hash - computed once, reused everywhere
    canonical_hash: str

    # State tensor as numpy array for vectorized ops
    # Shape: (4, n) where 4 = mu, nu, alpha, beta axes
    tensor: np.ndarray

    # Feature vector - pre-extracted features for fast lookup
    features: np.ndarray

    # Metadata (immutable)
    timestamp: float
    version: int = 1

    def __post_init__(self) -> None:
        # Validate tensor shape
        if self.tensor.ndim != 2 or self.tensor.shape[0] != 4:
            raise ValueError(f"Tensor must be (4, n), got {self.tensor.shape}")

    @property
    def mu(self) -> np.ndarray:
        """Biological/load/regulation axis."""
        return self.tensor[0]

    @property
    def nu(self) -> np.ndarray:
        """Cognition/prediction axis."""
        return self.tensor[1]

    @property
    def alpha(self) -> np.ndarray:
        """Org-system/policy axis."""
        return self.tensor[2]

    @property
    def beta(self) -> np.ndarray:
        """Environment/context axis."""
        return self.tensor[3]


@dataclass(frozen=True)
class NumericInputs:
    """Numeric input vector - no semantic interpretation needed."""

    # Raw numeric inputs as numpy arrays
    vector: np.ndarray

    # Input hash for cache lookup
    input_hash: str

    # Input type for routing (pre-categorized)
    input_type: str  # "signal", "control", "query", "command"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NumericInputs:
        """Create from dict - one-time conversion, then compiled."""
        vector = np.array(
            [
                data.get("load", 0.0),
                data.get("signal", 0.0),
                data.get("confidence", 0.5),
                data.get("urgency", 0.0),
                data.get("priority", 0.5),
            ],
            dtype=np.float64,
        )

        # Compute hash
        hash_input = json.dumps(data, sort_keys=True, default=str)
        input_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        # Determine type
        input_type = data.get("type", "signal")

        return cls(vector=vector, input_hash=input_hash, input_type=input_type)


@dataclass(frozen=True)
class CompiledConstraints:
    """Pre-compiled constraint matrix."""

    # Constraint flags as bit mask for O(1) checking
    # Bits: 0=mode_valid, 1=schema_valid, 2=provenance_ok, 3=complete, 4=permission_ok
    constraint_mask: int

    # Numeric bounds (vectorized)
    min_bounds: np.ndarray
    max_bounds: np.ndarray

    # Allowed transitions (pre-computed set)
    allowed_hashes: frozenset[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompiledConstraints:
        """Compile constraints once, use many times."""
        mask = 0
        if data.get("mode_valid", False):
            mask |= 1 << 0
        if data.get("schema_valid", False):
            mask |= 1 << 1
        if data.get("provenance_ok", False):
            mask |= 1 << 2
        if data.get("complete", False):
            mask |= 1 << 3
        if data.get("permission_ok", False):
            mask |= 1 << 4

        min_bounds = np.array(data.get("min", [0.0] * 4), dtype=np.float64)
        max_bounds = np.array(data.get("max", [1.0] * 4), dtype=np.float64)

        allowed = frozenset(data.get("allowed", []))

        return cls(
            constraint_mask=mask,
            min_bounds=min_bounds,
            max_bounds=max_bounds,
            allowed_hashes=allowed,
        )

    def check_bit(self, bit: int) -> bool:
        """O(1) constraint bit check."""
        return (self.constraint_mask & (1 << bit)) != 0


@dataclass(frozen=True)
class NumericAction:
    """Numeric action - pre-categorized for fast routing."""

    action_hash: str
    action_type: str  # "transition", "query", "repair", "observe"
    target_hash: str
    params: np.ndarray


@dataclass(frozen=True)
class InvariantResult:
    """Result of invariant check."""

    passed: bool
    violations: list[str]
    score: float  # 0.0 to 1.0

    # Fast path: pre-computed rejection reasons
    rejection_flags: int = 0


@dataclass
class TransitionResult:
    """Result of state transition."""

    success: bool
    new_state: Optional[CompiledState]
    invariant_result: InvariantResult
    compute_time_ms: float
    cache_hit: bool


# ============================================================================
# Fast Invariant Gate (Gamma)
# ============================================================================


class FastInvariantGate:
    """
    Early invariant checking - reject unlawful paths BEFORE computation.

    This is the Gamma gate in AMOS notation:
        Candidate -> Gamma -> Commit (if passes)

    NOT:
        Candidate -> Compute -> Check -> Reject (waste)
    """

    # Pre-computed invariant functions (no dynamic lookup)
    _invariants: dict[str, Callable[[CompiledState, NumericAction], bool]]

    def __init__(self) -> None:
        self._invariants = {
            "mode_integrity": self._check_mode,
            "schema_integrity": self._check_schema,
            "provenance_valid": self._check_provenance,
            "state_complete": self._check_complete,
            "permission_valid": self._check_permission,
        }

    def evaluate(
        self,
        state: CompiledState,
        action: NumericAction,
        constraints: CompiledConstraints,
    ) -> InvariantResult:
        """
        Fast invariant evaluation.

        Returns immediately on first violation (fail-fast).
        """
        violations: list[str] = []
        score = 1.0

        # Check 1: Mode integrity (bit 0)
        if not constraints.check_bit(0):
            violations.append("mode_integrity: invalid mode")
            score *= 0.5

        # Check 2: Schema integrity (bit 1)
        if not constraints.check_bit(1):
            violations.append("schema_integrity: schema mismatch")
            score *= 0.5

        # Check 3: Provenance (bit 2)
        if not constraints.check_bit(2):
            violations.append("provenance_valid: untrusted source")
            score *= 0.5

        # Check 4: State completeness (bit 3)
        if not constraints.check_bit(3):
            violations.append("state_complete: incomplete state")
            score *= 0.5

        # Check 5: Permission (bit 4)
        if not constraints.check_bit(4):
            violations.append("permission_valid: insufficient permission")
            score *= 0.3

        # Check 6: Numeric bounds (vectorized)
        bounds_violations = self._check_bounds(state, constraints)
        if bounds_violations:
            violations.extend(bounds_violations)
            score *= 0.7

        # Check 7: Transition allowed
        if action.target_hash not in constraints.allowed_hashes:
            violations.append(f"transition: {action.target_hash[:8]}... not allowed")
            score *= 0.5

        passed = len(violations) == 0

        return InvariantResult(
            passed=passed,
            violations=violations,
            score=score,
            rejection_flags=self._compute_flags(violations),
        )

    def _check_mode(self, state: CompiledState, action: NumericAction) -> bool:
        """Mode integrity check."""
        return state.mu[0] > 0.0  # Load indicator valid

    def _check_schema(self, state: CompiledState, action: NumericAction) -> bool:
        """Schema integrity check."""
        return state.nu[2] > 0.0  # Confidence indicator valid

    def _check_provenance(self, state: CompiledState, action: NumericAction) -> bool:
        """Provenance check."""
        return state.alpha[0] > 0.0  # Policy state valid

    def _check_complete(self, state: CompiledState, action: NumericAction) -> bool:
        """State completeness check."""
        return not np.any(np.isnan(state.tensor))

    def _check_permission(self, state: CompiledState, action: NumericAction) -> bool:
        """Permission check."""
        return state.alpha[1] > 0.5  # Permission score

    def _check_bounds(self, state: CompiledState, constraints: CompiledConstraints) -> list[str]:
        """Vectorized bounds checking."""
        violations: list[str] = []

        # Check min bounds (vectorized)
        below_min = state.tensor < constraints.min_bounds[:, np.newaxis]
        if np.any(below_min):
            axes = ["mu", "nu", "alpha", "beta"]
            for i, axis in enumerate(axes):
                if np.any(below_min[i]):
                    violations.append(f"bounds: {axis} below minimum")

        # Check max bounds (vectorized)
        above_max = state.tensor > constraints.max_bounds[:, np.newaxis]
        if np.any(above_max):
            axes = ["mu", "nu", "alpha", "beta"]
            for i, axis in enumerate(axes):
                if np.any(above_max[i]):
                    violations.append(f"bounds: {axis} above maximum")

        return violations

    def _compute_flags(self, violations: list[str]) -> int:
        """Compute rejection flags for fast routing."""
        flags = 0
        for v in violations:
            if "mode" in v:
                flags |= 1 << 0
            elif "schema" in v:
                flags |= 1 << 1
            elif "provenance" in v:
                flags |= 1 << 2
            elif "complete" in v:
                flags |= 1 << 3
            elif "permission" in v:
                flags |= 1 << 4
            elif "bounds" in v:
                flags |= 1 << 5
            elif "transition" in v:
                flags |= 1 << 6
        return flags


# ============================================================================
# Compiled Numeric Kernel
# ============================================================================


class CompiledNumericKernel:
    """
    The fast deterministic kernel.

    Separates from semantic kernel:
    - Semantic: Intent parsing, ambiguity resolution, planning
    - Numeric: Calculations, scoring, routing, invariant evaluation

    The numeric kernel sits in the hot path with:
    - Pre-compiled transition functions
    - Vectorized operations
    - Cached projections
    - Early invariant rejection
    """

    _instance: Optional[CompiledNumericKernel] = None

    def __new__(cls) -> CompiledNumericKernel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        # Fast invariant gate (Gamma)
        self._gamma = FastInvariantGate()

        # Pre-compiled transition functions (no dynamic lookup)
        self._transitions: dict[str, NumericTransition] = {
            "identity": self._transition_identity,
            "load_update": self._transition_load_update,
            "confidence_update": self._transition_confidence_update,
            "policy_update": self._transition_policy_update,
            "environment_update": self._transition_environment_update,
            "vectorized_compute": self._transition_vectorized,
        }

        # State cache - canonical_hash -> CompiledState
        self._state_cache: dict[str, CompiledState] = {}

        # Projection cache - (state_hash, view) -> projection
        self._projection_cache: dict[tuple[str, str], np.ndarray] = {}

        # Transition statistics
        self._stats = {
            "transitions": 0,
            "cache_hits": 0,
            "invariant_rejections": 0,
            "total_time_ms": 0.0,
        }

        self._initialized = True

    # ========================================================================
    # Public API
    # ========================================================================

    def transition(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
        transition_type: str = "identity",
    ) -> TransitionResult:
        """
        Execute compiled state transition.

        Path:
            1. Check cache (O(1))
            2. Invariant gate (fast reject)
            3. Vectorized compute
            4. Cache result
            5. Commit
        """
        import time

        start_time = time.perf_counter()

        # 1. Cache check - O(1) hash lookup
        cache_key = f"{state.canonical_hash}:{inputs.input_hash}:{transition_type}"
        cached = self._state_cache.get(cache_key)
        if cached is not None:
            self._stats["cache_hits"] += 1
            self._stats["transitions"] += 1
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._stats["total_time_ms"] += elapsed_ms
            return TransitionResult(
                success=True,
                new_state=cached,
                invariant_result=InvariantResult(passed=True, violations=[], score=1.0),
                compute_time_ms=elapsed_ms,
                cache_hit=True,
            )

        # 2. Build action
        action = NumericAction(
            action_hash=hashlib.sha256(transition_type.encode()).hexdigest()[:16],
            action_type="transition",
            target_hash=state.canonical_hash,
            params=inputs.vector,
        )

        # 3. Invariant gate - EARLY REJECTION (don't waste compute)
        invariant_result = self._gamma.evaluate(state, action, constraints)
        if not invariant_result.passed:
            self._stats["invariant_rejections"] += 1
            self._stats["transitions"] += 1
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._stats["total_time_ms"] += elapsed_ms
            return TransitionResult(
                success=False,
                new_state=None,
                invariant_result=invariant_result,
                compute_time_ms=elapsed_ms,
                cache_hit=False,
            )

        # 4. Get compiled transition function (O(1) lookup)
        transition_fn = self._transitions.get(transition_type, self._transition_identity)

        # 5. Execute vectorized transition
        new_state = transition_fn(state, inputs, constraints)

        # 6. Cache result
        self._state_cache[cache_key] = new_state

        # 7. Stats
        self._stats["transitions"] += 1
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._stats["total_time_ms"] += elapsed_ms

        return TransitionResult(
            success=True,
            new_state=new_state,
            invariant_result=invariant_result,
            compute_time_ms=elapsed_ms,
            cache_hit=False,
        )

    def compute_projection(self, state: CompiledState, view: str) -> np.ndarray | None:
        """
        Compute state projection with caching.

        Views: "deterministic", "observational", "decision", "health"
        """
        cache_key = (state.canonical_hash, view)

        # Check cache
        if cache_key in self._projection_cache:
            return self._projection_cache[cache_key]

        # Compute projection (vectorized)
        projector = self._get_projector(view)
        if projector is None:
            return None

        projection = projector(state)

        # Cache
        self._projection_cache[cache_key] = projection

        return projection

    def batch_evaluate_invariants(
        self,
        states: list[CompiledState],
        actions: list[NumericAction],
        constraints: CompiledConstraints,
    ) -> list[InvariantResult]:
        """
        Batch invariant evaluation for multiple candidates.

        Vectorized rejection of unlawful branches.
        """
        return [
            self._gamma.evaluate(state, action, constraints)
            for state, action in zip(states, actions)
        ]

    def get_stats(self) -> dict[str, Any]:
        """Get kernel statistics."""
        total = self._stats["transitions"]
        cache_hits = self._stats["cache_hits"]
        rejections = self._stats["invariant_rejections"]

        return {
            "total_transitions": total,
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / total if total > 0 else 0.0,
            "invariant_rejections": rejections,
            "rejection_rate": rejections / total if total > 0 else 0.0,
            "avg_time_ms": (self._stats["total_time_ms"] / total if total > 0 else 0.0),
            "state_cache_size": len(self._state_cache),
            "projection_cache_size": len(self._projection_cache),
        }

    def clear_caches(self) -> None:
        """Clear all caches."""
        self._state_cache.clear()
        self._projection_cache.clear()

    # ========================================================================
    # Pre-compiled Transition Functions
    # ========================================================================

    def _transition_identity(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Identity transition - state unchanged."""
        return CompiledState(
            canonical_hash=state.canonical_hash,
            tensor=state.tensor.copy(),
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    def _transition_load_update(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Update load (mu axis) - vectorized."""
        new_tensor = state.tensor.copy()

        # Update mu axis with input signal (vectorized)
        new_tensor[0] = state.mu * 0.9 + inputs.vector[0] * 0.1

        # Clip to bounds (vectorized)
        new_tensor[0] = np.clip(new_tensor[0], constraints.min_bounds[0], constraints.max_bounds[0])

        # Compute new hash
        new_hash = self._compute_state_hash(new_tensor, state.features)

        return CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    def _transition_confidence_update(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Update confidence (nu axis) - vectorized."""
        new_tensor = state.tensor.copy()

        # Update nu axis with confidence input (vectorized)
        confidence_input = inputs.vector[2]  # confidence field
        new_tensor[1] = state.nu * 0.8 + confidence_input * 0.2

        # Clip to bounds
        new_tensor[1] = np.clip(new_tensor[1], constraints.min_bounds[1], constraints.max_bounds[1])

        new_hash = self._compute_state_hash(new_tensor, state.features)

        return CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    def _transition_policy_update(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Update policy (alpha axis) - vectorized."""
        new_tensor = state.tensor.copy()

        # Update alpha axis (vectorized)
        urgency = inputs.vector[3]
        new_tensor[2] = state.alpha * (1 - urgency * 0.1) + urgency * 0.1

        # Clip
        new_tensor[2] = np.clip(new_tensor[2], constraints.min_bounds[2], constraints.max_bounds[2])

        new_hash = self._compute_state_hash(new_tensor, state.features)

        return CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    def _transition_environment_update(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Update environment (beta axis) - vectorized."""
        new_tensor = state.tensor.copy()

        # Update beta axis (vectorized)
        priority = inputs.vector[4]
        new_tensor[3] = state.beta * 0.95 + priority * 0.05

        # Clip
        new_tensor[3] = np.clip(new_tensor[3], constraints.min_bounds[3], constraints.max_bounds[3])

        new_hash = self._compute_state_hash(new_tensor, state.features)

        return CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    def _transition_vectorized(
        self,
        state: CompiledState,
        inputs: NumericInputs,
        constraints: CompiledConstraints,
    ) -> CompiledState:
        """Full vectorized update - all axes at once."""
        new_tensor = state.tensor.copy()

        # Vectorized update all axes simultaneously
        weights = np.array([0.9, 0.8, 0.9, 0.95])  # Decay rates
        inputs_expanded = np.array(
            [
                inputs.vector[0],  # load -> mu
                inputs.vector[2],  # confidence -> nu
                inputs.vector[3],  # urgency -> alpha
                inputs.vector[4],  # priority -> beta
            ]
        )

        # Vectorized: new = old * decay + input * (1 - decay)
        new_tensor = new_tensor * weights[:, np.newaxis] + inputs_expanded[:, np.newaxis] * (
            1 - weights[:, np.newaxis]
        )

        # Vectorized clip to bounds
        for i in range(4):
            new_tensor[i] = np.clip(
                new_tensor[i], constraints.min_bounds[i], constraints.max_bounds[i]
            )

        new_hash = self._compute_state_hash(new_tensor, state.features)

        return CompiledState(
            canonical_hash=new_hash,
            tensor=new_tensor,
            features=state.features.copy(),
            timestamp=datetime.now(UTC).timestamp(),
            version=state.version + 1,
        )

    # ========================================================================
    # Projectors
    # ========================================================================

    def _get_projector(self, view: str) -> Callable[[CompiledState], np.ndarray] | None:
        """Get pre-compiled projector function."""
        projectors = {
            "deterministic": self._project_deterministic,
            "observational": self._project_observational,
            "decision": self._project_decision,
            "health": self._project_health,
        }
        return projectors.get(view)

    def _project_deterministic(self, state: CompiledState) -> np.ndarray:
        """Projection for deterministic core - minimal features."""
        return np.array(
            [
                np.mean(state.mu),
                np.mean(state.nu),
                np.mean(state.alpha),
                float(state.canonical_hash[:8], 16) / 2**32,  # Hash as feature
            ]
        )

    def _project_observational(self, state: CompiledState) -> np.ndarray:
        """Projection for self-observer - integrity features."""
        return np.array(
            [
                np.std(state.mu),  # Load variance
                np.std(state.nu),  # Cognition variance
                np.mean(state.alpha),  # Policy state
                np.max(state.beta) - np.min(state.beta),  # Environment range
            ]
        )

    def _project_decision(self, state: CompiledState) -> np.ndarray:
        """Projection for decision making."""
        load_capacity = np.mean(state.mu) / (np.max(state.features) + 1e-6)
        confidence = 1.0 - np.std(state.nu)
        return np.array(
            [
                load_capacity,
                confidence,
                np.mean(state.alpha),
                np.min(state.beta),
            ]
        )

    def _project_health(self, state: CompiledState) -> np.ndarray:
        """Projection for health monitoring."""
        return np.array(
            [
                np.mean(state.mu),  # Health score proxy
                np.max(state.mu),  # Stress proxy
                np.mean(state.nu),  # Cognitive load
                np.std(state.tensor),  # Overall variance
            ]
        )

    # ========================================================================
    # Utilities
    # ========================================================================

    def _compute_state_hash(self, tensor: np.ndarray, features: np.ndarray) -> str:
        """Compute canonical hash from tensor."""
        # Pack tensor into bytes
        tensor_bytes = tensor.tobytes()
        feature_bytes = features.tobytes()
        combined = tensor_bytes + feature_bytes
        return hashlib.sha256(combined).hexdigest()[:32]


# ============================================================================
# Factory
# ============================================================================


def get_compiled_numeric_kernel() -> CompiledNumericKernel:
    """Get the singleton compiled numeric kernel."""
    return CompiledNumericKernel()


def create_initial_state(tensor_shape: tuple[int, ...] = (4, 8)) -> CompiledState:
    """Create initial compiled state."""
    tensor = np.zeros(tensor_shape, dtype=np.float64)
    features = np.zeros(8, dtype=np.float64)

    # Initial hash
    hash_input = tensor.tobytes() + features.tobytes()
    canonical_hash = hashlib.sha256(hash_input).hexdigest()[:32]

    return CompiledState(
        canonical_hash=canonical_hash,
        tensor=tensor,
        features=features,
        timestamp=datetime.now(UTC).timestamp(),
        version=1,
    )

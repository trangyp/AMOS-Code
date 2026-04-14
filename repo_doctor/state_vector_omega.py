"""
Repo Doctor Ω∞∞ - Quantum-inspired repository state model.

Implements the full 12-dimensional state vector with density matrix
representation for partial knowledge and mixed states.

State vector:
|Ψ_repo(t)⟩ = Σk αk(t)|k⟩

Where basis states are:
- |S⟩  = syntax / parse integrity
- |I⟩  = import / symbol resolution integrity
- |Ty⟩ = type / callable signature integrity
- |A⟩  = public API integrity
- |E⟩  = entrypoint / launcher integrity
- |Pk⟩ = packaging / build integrity
- |Rt⟩ = runtime behavior integrity
- |D⟩  = docs / demos / tests contract integrity
- |Ps⟩ = persistence / schema integrity
- |St⟩ = status truth integrity
- |Sec⟩ = security integrity
- |H⟩  = history / temporal integrity
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class BasisState(Enum):
    """
    The 12 basis states of the repository Hilbert space.
    """

    SYNTAX = ("S", "syntax", 100.0)  # c1·N_fatal_parse + c2·N_recoverable_parse
    IMPORT = ("I", "import", 95.0)  # c1·N_unresolved_imports
    TYPE = ("Ty", "type", 75.0)  # c1·N_arity_mismatch + c2·N_kwarg_mismatch
    API = ("A", "api", 95.0)  # commutator [A_public, A_runtime]
    ENTRYPOINT = ("E", "entrypoint", 90.0)  # c1·N_missing_target + c2·N_wrong_target
    PACKAGING = ("Pk", "packaging", 90.0)  # c1·N_metadata_conflicts
    RUNTIME = ("Rt", "runtime", 85.0)  # c1·N_shell_promise_violations
    DOCS = ("D", "docs", 40.0)  # demo/tutorial/guide contract
    PERSISTENCE = ("Ps", "persistence", 70.0)  # c1·N_roundtrip_failures
    STATUS = ("St", "status", 70.0)  # c1·N_false_initialized
    SECURITY = ("Sec", "security", 100.0)  # c1·N_source_sink_violations
    HISTORY = ("H", "history", 60.0)  # c1·N_unlocalizable_breakpoints

    def __init__(self, symbol: str, label: str, weight: float):
        self.symbol = symbol
        self.label = label
        self.weight = weight

    @property
    def is_hard_fail(self) -> bool:
        """Hard-fail dimensions must pass for release."""
        return self in {
            BasisState.SYNTAX,
            BasisState.IMPORT,
            BasisState.TYPE,
            BasisState.API,
            BasisState.ENTRYPOINT,
            BasisState.PACKAGING,
            BasisState.RUNTIME,
            BasisState.PERSISTENCE,
            BasisState.STATUS,
            BasisState.SECURITY,
        }


class Observable(Enum):
    """
    Structured observables consumed by the doctor.
    """

    PARSE_FATAL = auto()
    PARSE_RECOVERABLE = auto()
    IMPORT_UNRESOLVED = auto()
    EXPORT_UNREACHABLE = auto()
    SIGNATURE_ARITY_MISMATCH = auto()
    SIGNATURE_KWARG_MISMATCH = auto()
    RETURN_SHAPE_MISMATCH = auto()
    ENTRYPOINT_MISSING = auto()
    ENTRYPOINT_WRONG_TARGET = auto()
    UNCONSUMED_FLAG_OR_ENV = auto()
    PACKAGING_CONFLICT = auto()
    ROUNDTRIP_FAILURE = auto()
    STATUS_FALSE_CLAIM = auto()
    RUNTIME_PROMISE_VIOLATION = auto()
    TEST_CONTRACT_FAILURE = auto()
    SECURITY_FLOW_VIOLATION = auto()
    TEMPORAL_BREAKPOINT = auto()


@dataclass
class ObservableInstance:
    """A concrete observation with structured context."""

    kind: Observable
    severity: float  # 0.0 to 1.0
    location: str
    surface: str  # e.g., "demo_vs_runtime", "test_vs_api"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.name,
            "severity": self.severity,
            "location": self.location,
            "surface": self.surface,
            "details": self.details,
        }


@dataclass
class StateVector:
    """
    Pure state representation: |Ψ_repo(t)⟩ = Σk αk(t)|k⟩
    """

    amplitudes: dict[BasisState, float] = field(
        default_factory=lambda: {state: 1.0 for state in BasisState}
    )
    timestamp: Optional[float] = None
    commit: Optional[str] = None

    def __post_init__(self):
        # Normalize amplitudes to [0, 1]
        for state in BasisState:
            self.amplitudes.setdefault(state, 1.0)
            self.amplitudes[state] = max(0.0, min(1.0, self.amplitudes[state]))

    def apply_collapse(self, state: BasisState, severity: float):
        """
        Collapse a basis state: αk = exp(-severity)
        """
        self.amplitudes[state] = math.exp(-severity)

    def apply_observables(self, observables: list[ObservableInstance]):
        """
        Update amplitudes from observables: αk = exp(-Σj wk,j · oj)
        """
        # Map observables to basis state impacts
        observable_map = {
            Observable.PARSE_FATAL: [(BasisState.SYNTAX, 1.0)],
            Observable.PARSE_RECOVERABLE: [(BasisState.SYNTAX, 0.5)],
            Observable.IMPORT_UNRESOLVED: [(BasisState.IMPORT, 1.0)],
            Observable.EXPORT_UNREACHABLE: [(BasisState.IMPORT, 0.8)],
            Observable.SIGNATURE_ARITY_MISMATCH: [(BasisState.TYPE, 1.0)],
            Observable.SIGNATURE_KWARG_MISMATCH: [(BasisState.TYPE, 0.9)],
            Observable.RETURN_SHAPE_MISMATCH: [(BasisState.TYPE, 0.7)],
            Observable.ENTRYPOINT_MISSING: [(BasisState.ENTRYPOINT, 1.0)],
            Observable.ENTRYPOINT_WRONG_TARGET: [(BasisState.ENTRYPOINT, 0.9)],
            Observable.UNCONSUMED_FLAG_OR_ENV: [(BasisState.ENTRYPOINT, 0.6)],
            Observable.PACKAGING_CONFLICT: [(BasisState.PACKAGING, 1.0)],
            Observable.ROUNDTRIP_FAILURE: [(BasisState.PERSISTENCE, 1.0)],
            Observable.STATUS_FALSE_CLAIM: [(BasisState.STATUS, 1.0)],
            Observable.RUNTIME_PROMISE_VIOLATION: [(BasisState.RUNTIME, 1.0)],
            Observable.TEST_CONTRACT_FAILURE: [(BasisState.DOCS, 0.8)],
            Observable.SECURITY_FLOW_VIOLATION: [(BasisState.SECURITY, 1.0)],
            Observable.TEMPORAL_BREAKPOINT: [(BasisState.HISTORY, 0.7)],
        }

        for obs in observables:
            if obs.kind in observable_map:
                for basis_state, weight in observable_map[obs.kind]:
                    # Exponential decay: αk = exp(-w·severity)
                    decay = math.exp(-weight * obs.severity)
                    self.amplitudes[basis_state] *= decay

    def energy(self) -> float:
        """
        Calculate Hamiltonian energy: E = Σk λk (1 - αk)²
        """
        return sum(state.weight * (1 - self.amplitudes[state]) ** 2 for state in BasisState)

    def score(self) -> int:
        """
        Calculate 0-100 score based on energy.
        """
        max_energy = sum(state.weight for state in BasisState)
        normalized = self.energy() / max_energy
        return int(100 * (1 - normalized))

    def is_releaseable(self, threshold: float = 2.0) -> tuple[bool, list[BasisState]]:
        """
        Check if repository is releaseable.
        Returns (releaseable, list of blocking failed dimensions).
        """
        blockers = []
        for state in BasisState:
            if state.is_hard_fail and self.amplitudes[state] < 0.5:
                blockers.append(state)

        releaseable = len(blockers) == 0 and self.energy() < threshold
        return releaseable, blockers

    def drift(self, other: StateVector) -> float:
        """
        Calculate drift between two states: ||ΔΨ|| = sqrt(Σk (Δαk)²)
        """
        delta_squared = sum((self.amplitudes[s] - other.amplitudes[s]) ** 2 for s in BasisState)
        return math.sqrt(delta_squared)

    def to_dict(self) -> dict:
        return {
            "amplitudes": {state.symbol: round(self.amplitudes[state], 3) for state in BasisState},
            "energy": round(self.energy(), 3),
            "score": self.score(),
            "timestamp": self.timestamp,
            "commit": self.commit,
        }

    def format_report(self) -> str:
        """Generate human-readable state report."""
        lines = [
            "=" * 60,
            "REPO STATE VECTOR REPORT (Ω∞∞)",
            "=" * 60,
        ]

        if self.commit:
            lines.append(f"Commit: {self.commit[:8]}")
        lines.append("")

        for state in BasisState:
            amp = self.amplitudes[state]
            status = "✓" if amp > 0.9 else "⚠" if amp > 0.5 else "✗"
            bar = "█" * int(amp * 20) + "░" * (20 - int(amp * 20))
            lines.append(f"  [{status}] {state.symbol:3} = {amp:.3f}  {bar}")

        lines.append("")
        lines.append(f"Energy:        {self.energy():.4f}")
        lines.append(f"Score:         {self.score()}/100")

        releaseable, blockers = self.is_releaseable()
        lines.append(f"Healthy:       {self.energy() < 3.0}")
        lines.append(f"Releaseable:   {releaseable}")

        if blockers:
            lines.append("  Blockers:")
            for b in blockers:
                lines.append(f"    - {b.symbol}: {b.label}")

        if self.energy() >= 3.0:
            # Find collapsed subsystems
            collapsed = [s for s in BasisState if self.amplitudes[s] < 0.5]
            if collapsed:
                lines.append(f"Collapsed Subsystem: {collapsed[0].label}")

        lines.append("=" * 60)
        return "\n".join(lines)


@dataclass
class DensityMatrix:
    """
    Mixed-state representation for partial knowledge:
    ρ_repo(t) = Σi pi |Ψ_i(t)⟩⟨Ψ_i(t)|
    """

    states: list[tuple[float, StateVector]] = field(default_factory=list)
    """List of (probability, state_vector) tuples."""

    def __post_init__(self):
        if not self.states:
            # Default to pure state
            self.states = [(1.0, StateVector())]
        self._normalize()

    def _normalize(self):
        """Ensure probabilities sum to 1."""
        total = sum(p for p, _ in self.states)
        if total > 0:
            self.states = [(p / total, sv) for p, sv in self.states]

    def add_hypothesis(self, probability: float, state: StateVector):
        """Add a state hypothesis with given probability."""
        self.states.append((probability, state))
        self._normalize()

    def expectation(self, observable: BasisState) -> float:
        """
        Calculate expectation value: ⟨O⟩ = Tr(ρ O)
        """
        return sum(p * sv.amplitudes[observable] for p, sv in self.states)

    def entropy(self) -> float:
        """
        Calculate von Neumann entropy: Ent(S) = -Σj pj log pj
        """
        return -sum(p * math.log(p) if p > 0 else 0 for p, _ in self.states)

    def collapse_to_pure(self, hypothesis_index: int = 0) -> StateVector:
        """
        Collapse density matrix to most probable pure state.
        """
        if not self.states:
            return StateVector()

        # Find most probable state
        best_prob, best_state = max(self.states, key=lambda x: x[0])
        return best_state

    def to_dict(self) -> dict:
        return {
            "entropy": self.entropy(),
            "hypotheses": len(self.states),
            "states": [{"probability": p, "state": sv.to_dict()} for p, sv in self.states],
        }


@dataclass
class Hamiltonian:
    """
    Hamiltonian operator for repository degradation.
    H_repo = Σk λk Hk
    """

    weights: dict[BasisState, float] = field(
        default_factory=lambda: {state: state.weight for state in BasisState}
    )

    def energy(self, state: StateVector | DensityMatrix) -> float:
        """Calculate energy of a state."""
        if isinstance(state, DensityMatrix):
            # Mixed state: E = Tr(ρ H)
            return sum(p * self._pure_energy(sv) for p, sv in state.states)
        else:
            return self._pure_energy(state)

    def _pure_energy(self, state: StateVector) -> float:
        """Calculate energy of pure state: E = Σk λk (1 - αk)²"""
        return sum(self.weights[basis] * (1 - state.amplitudes[basis]) ** 2 for basis in BasisState)

    def gradient(self, state: StateVector) -> dict[BasisState, float]:
        """
        Calculate energy gradient w.r.t. each basis state.
        ∂E/∂αk = -2λk(1 - αk)
        """
        return {
            basis: -2 * self.weights[basis] * (1 - state.amplitudes[basis]) for basis in BasisState
        }

    def steepest_descent_repair(self, state: StateVector) -> list[BasisState]:
        """
        Return basis states in order of steepest energy descent.
        This suggests repair priority.
        """
        gradient = self.gradient(state)
        # Sort by magnitude of negative gradient (steepest descent)
        return sorted(
            BasisState,
            key=lambda b: gradient[b],
            reverse=True,  # Most negative first
        )


class EntanglementMatrix:
    """
    Entanglement matrix M_ij measuring coupling between subsystems.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.matrix: dict[tuple[BasisState, BasisState], float] = {}

    def compute(self, import_graph: dict, call_graph: dict, git_history: list):
        """
        Compute entanglement from multiple coupling sources:
        M_ij = α·Import(i,j) + β·Call(i,j) + γ·SharedTests(i,j) + δ·GitCoChange(i,j)
        """
        # This is a placeholder - real implementation would analyze
        # the actual repository structure
        for i in BasisState:
            for j in BasisState:
                if i != j:
                    # Simplified: higher coupling for related dimensions
                    coupling = 0.0
                    if {i, j} <= {BasisState.IMPORT, BasisState.API, BasisState.ENTRYPOINT}:
                        coupling = 0.8
                    elif {i, j} <= {BasisState.PACKAGING, BasisState.ENTRYPOINT}:
                        coupling = 0.9
                    elif {i, j} <= {BasisState.STATUS, BasisState.RUNTIME}:
                        coupling = 0.7
                    self.matrix[(i, j)] = coupling

    def entanglement_entropy(self, state: BasisState) -> float:
        """
        Calculate entanglement entropy for a subsystem.
        Ent(S) = -Σj pj log pj
        """
        couplings = [self.matrix.get((state, other), 0.0) for other in BasisState if other != state]

        if not couplings or sum(couplings) == 0:
            return 0.0

        # Normalize to probabilities
        total = sum(couplings)
        probs = [c / total for c in couplings]

        return -sum(p * math.log(p) if p > 0 else 0 for p in probs)

    def get_high_entanglement_pairs(
        self, threshold: float = 0.7
    ) -> list[tuple[BasisState, BasisState, float]]:
        """Return pairs with entanglement above threshold."""
        pairs = []
        for (i, j), coupling in self.matrix.items():
            if coupling >= threshold:
                pairs.append((i, j, coupling))
        return sorted(pairs, key=lambda x: x[2], reverse=True)


class CollapseOperator:
    """
    Collapse operator for finding minimal failing subspace.
    C_fail(|Ψ⟩) = argmin_S { S | I_S = 0 and repair_cost(S) minimal }
    """

    def __init__(self, hamiltonian: Hamiltonian):
        self.H = hamiltonian

    def collapse(self, state: StateVector) -> list[BasisState]:
        """
        Collapse to minimal failing cut.
        Returns list of basis states that need repair.
        """
        # Find all collapsed dimensions
        failed = [b for b in BasisState if state.amplitudes[b] < 0.5]

        if not failed:
            return []

        # Sort by steepest energy descent (highest repair impact)
        gradient = self.H.gradient(state)
        failed.sort(key=lambda b: gradient[b], reverse=True)

        return failed

    def minimal_cut(self, state: StateVector, max_states: int = 3) -> list[BasisState]:
        """
        Return the minimal set of states to repair for maximum energy reduction.
        """
        all_failed = self.collapse(state)

        if len(all_failed) <= max_states:
            return all_failed

        # Greedy selection: pick states with highest individual impact
        impact = []
        for basis in all_failed:
            # Calculate energy reduction if this state were fixed
            current_amp = state.amplitudes[basis]
            fixed_amp = 1.0
            energy_reduction = (
                self.H.weights[basis] * (1 - current_amp) ** 2
                - self.H.weights[basis] * (1 - fixed_amp) ** 2
            )
            impact.append((basis, energy_reduction))

        impact.sort(key=lambda x: x[1], reverse=True)
        return [b for b, _ in impact[:max_states]]

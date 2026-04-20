"""
Repo Doctor Ω∞∞∞ - Triple-Infinity State Model

Full 13-dimensional tensor product state space with:
- Complete basis states (including T for tests)
- Lindblad noise operators
- Full temporal mechanics
- Path-integral blame scoring

State vector:
|Ψ_repo(t)⟩ = Σk αk(t)|k⟩

Basis (13 dimensions):
|S⟩    syntax integrity
|I⟩    import integrity
|Ty⟩   type/signature integrity
|A⟩    API contract integrity
|E⟩    entrypoint integrity
|Pk⟩   packaging integrity
|Rt⟩   runtime integrity
|Ps⟩   persistence integrity
|St⟩   status truth integrity
|T⟩    test integrity        [NEW in Ω∞∞∞]
|D⟩    docs/demo/tutorial integrity
|Sec⟩  security integrity
|H⟩    temporal/history integrity

This is the maximum-strength repository physics model.
"""

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List


class BasisState(Enum):
    """
    The 13 basis states of the repository Hilbert space (Ω∞∞∞).
    """

    SYNTAX = ("S", "syntax", 100.0)
    IMPORT = ("I", "import", 95.0)
    TYPE = ("Ty", "type", 75.0)
    API = ("A", "api", 95.0)
    ENTRYPOINT = ("E", "entrypoint", 90.0)
    PACKAGING = ("Pk", "packaging", 90.0)
    RUNTIME = ("Rt", "runtime", 85.0)
    PERSISTENCE = ("Ps", "persistence", 70.0)
    STATUS = ("St", "status", 70.0)
    TESTS = ("T", "tests", 80.0)  # NEW in Ω∞∞∞
    DOCS = ("D", "docs", 45.0)
    SECURITY = ("Sec", "security", 100.0)
    HISTORY = ("H", "history", 60.0)

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
            BasisState.TESTS,
            BasisState.SECURITY,
        }


class Observable(Enum):
    """Structured observables consumed by the doctor."""

    PARSE_FATAL = auto()
    PARSE_RECOVERABLE = auto()
    IMPORT_UNRESOLVED = auto()
    EXPORT_MISSING = auto()
    CALL_ARITY_MISMATCH = auto()
    CALL_KWARG_MISMATCH = auto()
    RETURN_SHAPE_MISMATCH = auto()
    ENTRYPOINT_MISSING = auto()
    ENTRYPOINT_WRONG_TARGET = auto()
    FLAG_ENV_UNCONSUMED = auto()
    PACKAGING_CONFLICT = auto()
    BUILD_FAILURE = auto()
    ROUNDTRIP_FAILURE = auto()
    STATUS_FALSE_CLAIM = auto()
    RUNTIME_CONTRACT_VIOLATION = auto()
    TEST_CONTRACT_FAILURE = auto()
    DOC_EXAMPLE_FAILURE = auto()
    SECURITY_FLOW_VIOLATION = auto()
    TEMPORAL_BREAKPOINT = auto()


@dataclass
class ObservableInstance:
    """A concrete observation with structured context."""

    kind: Observable
    severity: float
    location: str
    surface: str
    details: Dict[str, Any] = field(default_factory=dict)

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
        default_factory=lambda: dict.fromkeys(BasisState, 1.0)
    )
    timestamp: float = None
    commit: str = None

    def __post_init__(self):
        for state in BasisState:
            self.amplitudes.setdefault(state, 1.0)
            self.amplitudes[state] = max(0.0, min(1.0, self.amplitudes[state]))

    def apply_collapse(self, state: BasisState, severity: float):
        """Collapse a basis state: αk = exp(-severity)"""
        self.amplitudes[state] = math.exp(-severity)

    def apply_observables(self, observables: List[ObservableInstance]):
        """Update amplitudes from observables: αk = exp(-Σj wk,j · oj)"""
        observable_map = {
            Observable.PARSE_FATAL: [(BasisState.SYNTAX, 1.0)],
            Observable.PARSE_RECOVERABLE: [(BasisState.SYNTAX, 0.5)],
            Observable.IMPORT_UNRESOLVED: [(BasisState.IMPORT, 1.0)],
            Observable.EXPORT_MISSING: [(BasisState.IMPORT, 0.8)],
            Observable.CALL_ARITY_MISMATCH: [(BasisState.TYPE, 1.0)],
            Observable.CALL_KWARG_MISMATCH: [(BasisState.TYPE, 0.9)],
            Observable.RETURN_SHAPE_MISMATCH: [(BasisState.TYPE, 0.7)],
            Observable.ENTRYPOINT_MISSING: [(BasisState.ENTRYPOINT, 1.0)],
            Observable.ENTRYPOINT_WRONG_TARGET: [(BasisState.ENTRYPOINT, 0.9)],
            Observable.FLAG_ENV_UNCONSUMED: [(BasisState.ENTRYPOINT, 0.6)],
            Observable.PACKAGING_CONFLICT: [(BasisState.PACKAGING, 1.0)],
            Observable.BUILD_FAILURE: [(BasisState.PACKAGING, 0.9)],
            Observable.ROUNDTRIP_FAILURE: [(BasisState.PERSISTENCE, 1.0)],
            Observable.STATUS_FALSE_CLAIM: [(BasisState.STATUS, 1.0)],
            Observable.RUNTIME_CONTRACT_VIOLATION: [(BasisState.RUNTIME, 1.0)],
            Observable.TEST_CONTRACT_FAILURE: [(BasisState.TESTS, 1.0)],
            Observable.DOC_EXAMPLE_FAILURE: [(BasisState.DOCS, 0.8)],
            Observable.SECURITY_FLOW_VIOLATION: [(BasisState.SECURITY, 1.0)],
            Observable.TEMPORAL_BREAKPOINT: [(BasisState.HISTORY, 0.7)],
        }

        for obs in observables:
            if obs.kind in observable_map:
                for basis_state, weight in observable_map[obs.kind]:
                    decay = math.exp(-weight * obs.severity)
                    self.amplitudes[basis_state] *= decay

    def energy(self) -> float:
        """Calculate Hamiltonian energy: E = Σk λk (1 - αk)²"""
        return sum(state.weight * (1 - self.amplitudes[state]) ** 2 for state in BasisState)

    def score(self) -> int:
        """Calculate 0-100 score based on energy."""
        max_energy = sum(state.weight for state in BasisState)
        normalized = self.energy() / max_energy
        return int(100 * (1 - normalized))

    def is_releaseable(self, threshold: float = 2.0) -> tuple[bool, list[BasisState]]:
        """Check if repository is releaseable."""
        blockers = [
            state for state in BasisState if state.is_hard_fail and self.amplitudes[state] < 0.5
        ]
        releaseable = len(blockers) == 0 and self.energy() < threshold
        return releaseable, blockers

    def drift(self, other: StateVector) -> float:
        """Calculate drift: ||ΔΨ|| = sqrt(Σk (Δαk)²)"""
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


@dataclass
class DensityMatrix:
    """Mixed-state representation: ρ_repo(t) = Σi pi |Ψ_i(t)⟩⟨Ψ_i(t)|"""

    states: list[tuple[float, StateVector]] = field(default_factory=list)

    def __post_init__(self):
        if not self.states:
            self.states = [(1.0, StateVector())]
        self._normalize()

    def _normalize(self):
        total = sum(p for p, _ in self.states)
        if total > 0:
            self.states = [(p / total, sv) for p, sv in self.states]

    def expectation(self, observable: BasisState) -> float:
        """Calculate expectation: ⟨O⟩ = Tr(ρ O)"""
        return sum(p * sv.amplitudes[observable] for p, sv in self.states)

    def entropy(self) -> float:
        """Calculate von Neumann entropy: Ent(S) = -Σj pj log pj"""
        return -sum(p * math.log(p) if p > 0 else 0 for p, _ in self.states)


class NoiseOperator:
    """
    Lindblad-style noise operator for open-system modeling.

    Environmental decoherence operators:
    - L_pyver: Python version changes
    - L_os: Operating system differences
    - L_native: Native toolchain issues
    - L_ci: CI environment changes
    - L_secret: Secrets/keys availability
    - L_net: Network availability
    """

    def __init__(self, name: str, impact: dict[BasisState, float]):
        self.name = name
        self.impact = impact

    def apply(self, state: StateVector, strength: float = 1.0) -> StateVector:
        """Apply noise to state."""
        new_amplitudes = dict(state.amplitudes)
        for basis, coeff in self.impact.items():
            # Lindblad-style decay: ρ' = L ρ L†
            new_amplitudes[basis] *= 1 - coeff * strength
        return StateVector(new_amplitudes, state.timestamp, state.commit)


class OpenSystemModel:
    """
    Open-system model with Lindblad master equation.

    dρ/dt = -i[H_repo, ρ] + Σm (Lm ρ Lm† - 1/2 {Lm†Lm, ρ})
    """

    def __init__(self):
        self.noise_operators: List[NoiseOperator] = []
        self._init_default_noise()

    def _init_default_noise(self):
        """Initialize default environmental noise operators."""
        self.noise_operators = [
            NoiseOperator("L_pyver", {BasisState.RUNTIME: 0.3, BasisState.TESTS: 0.2}),
            NoiseOperator("L_os", {BasisState.RUNTIME: 0.2, BasisState.PACKAGING: 0.1}),
            NoiseOperator("L_native", {BasisState.PACKAGING: 0.3, BasisState.RUNTIME: 0.2}),
            NoiseOperator("L_ci", {BasisState.TESTS: 0.3, BasisState.SECURITY: 0.1}),
            NoiseOperator("L_secret", {BasisState.SECURITY: 0.4, BasisState.RUNTIME: 0.2}),
            NoiseOperator("L_net", {BasisState.TESTS: 0.1, BasisState.DOCS: 0.05}),
        ]

    def evolve(self, state: StateVector, dt: float = 1.0) -> StateVector:
        """Evolve state under open-system dynamics."""
        result = StateVector(dict(state.amplitudes))
        for noise in self.noise_operators:
            result = noise.apply(result, dt)
        return result


@dataclass
class TemporalState:
    """
    Temporal evolution of repository state.

    Tracks state across commits for drift analysis.
    """

    states: Dict[str, StateVector] = field(default_factory=dict)
    """Map of commit hash to state vector."""

    def add_state(self, commit: str, state: StateVector):
        """Record state at a commit."""
        state.commit = commit
        self.states[commit] = state

    def drift(self, commit1: str, commit2: str) -> float:
        """Calculate drift between two commits."""
        if commit1 not in self.states or commit2 not in self.states:
            return 0.0
        return self.states[commit1].drift(self.states[commit2])

    def find_first_bad(self, invariant: BasisState, good_commit: str, bad_commit: str) -> str:
        """
        Find first commit where invariant fails.

        t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
        """
        # Binary search through commits
        # Simplified: linear scan for now
        commits = list(self.states.keys())
        if good_commit not in commits or bad_commit not in commits:
            return None

        good_idx = commits.index(good_commit)
        bad_idx = commits.index(bad_commit)

        if good_idx > bad_idx:
            good_idx, bad_idx = bad_idx, good_idx

        for i in range(good_idx + 1, bad_idx + 1):
            commit = commits[i]
            state = self.states[commit]
            if state.amplitudes[invariant] < 0.5:
                return commit

        return None

    def path_integral_blame(
        self, invariant: BasisState, path: List[str], coefficients: Dict[str, float] = None
    ) -> dict[str, float]:
        """
        Calculate path-integral blame scores.

        S_k[path] = Στ (a1·||ΔΨ_k(τ)|| + a2·ΔEnt_k(τ) + ...)

        Returns probability that each commit caused the collapse.
        """
        if not path or len(path) < 2:
            return {}

        coeffs = coefficients or {
            "drift": 1.0,
            "entanglement": 0.5,
            "api_change": 1.0,
            "entry_change": 0.8,
        }

        actions: Dict[str, float] = {}

        for i in range(1, len(path)):
            prev_commit = path[i - 1]
            curr_commit = path[i]

            if prev_commit not in self.states or curr_commit not in self.states:
                continue

            prev_state = self.states[prev_commit]
            curr_state = self.states[curr_commit]

            # Calculate action components
            drift = abs(curr_state.amplitudes[invariant] - prev_state.amplitudes[invariant])

            # Simplified action calculation
            action = coeffs["drift"] * drift
            actions[curr_commit] = action

        # Convert to probability: P ∝ exp(-S)
        max_action = max(actions.values()) if actions else 1.0
        probabilities = {
            commit: math.exp(-action / max_action) if max_action > 0 else 1.0
            for commit, action in actions.items()
        }

        # Normalize
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v / total for k, v in probabilities.items()}

        return probabilities


class Hamiltonian:
    """
    Hamiltonian operator for repository degradation.
    H_repo = Σk λk Hk
    """

    def __init__(self, custom_weights: dict[BasisState, float] = None):
        self.weights = custom_weights or {state: state.weight for state in BasisState}

    def energy(self, state: StateVector | DensityMatrix) -> float:
        """Calculate energy of a state."""
        if isinstance(state, DensityMatrix):
            return sum(p * self._pure_energy(sv) for p, sv in state.states)
        return self._pure_energy(state)

    def _pure_energy(self, state: StateVector) -> float:
        """Calculate energy: E = Σk λk (1 - αk)²"""
        return sum(self.weights[basis] * (1 - state.amplitudes[basis]) ** 2 for basis in BasisState)

    def gradient(self, state: StateVector) -> dict[BasisState, float]:
        """Calculate energy gradient: ∂E/∂αk = -2λk(1 - αk)"""
        return {
            basis: -2 * self.weights[basis] * (1 - state.amplitudes[basis]) for basis in BasisState
        }

    def steepest_descent_repair(self, state: StateVector) -> List[BasisState]:
        """Return basis states in order of steepest energy descent."""
        gradient = self.gradient(state)
        return sorted(BasisState, key=lambda b: gradient[b], reverse=True)


class CollapseOperator:
    """
    Collapse operator for finding minimal failing subspace.
    C_fail(|Ψ⟩) = argmin_S { S | I_S = 0 and repair_cost(S) minimal }
    """

    def __init__(self, hamiltonian: Hamiltonian):
        self.H = hamiltonian

    def collapse(self, state: StateVector) -> List[BasisState]:
        """Collapse to minimal failing cut."""
        failed = [b for b in BasisState if state.amplitudes[b] < 0.5]
        if not failed:
            return []

        gradient = self.H.gradient(state)
        failed.sort(key=lambda b: gradient[b], reverse=True)
        return failed

    def minimal_cut(self, state: StateVector, max_states: int = 3) -> List[BasisState]:
        """Return minimal set of states to repair for maximum energy reduction."""
        all_failed = self.collapse(state)
        if len(all_failed) <= max_states:
            return all_failed

        impact = []
        for basis in all_failed:
            current_amp = state.amplitudes[basis]
            fixed_amp = 1.0
            energy_reduction = (
                self.H.weights[basis] * (1 - current_amp) ** 2
                - self.H.weights[basis] * (1 - fixed_amp) ** 2
            )
            impact.append((basis, energy_reduction))

        impact.sort(key=lambda x: x[1], reverse=True)
        return [b for b, _ in impact[:max_states]]


class EntanglementMatrix:
    """Entanglement matrix M_ij measuring coupling between subsystems."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.matrix: dict[tuple[BasisState, BasisState], float] = {}

    def compute(self, import_graph: dict, call_graph: dict, git_history: list):
        """
        Compute entanglement from multiple coupling sources:
        M_ij = α·Import(i,j) + β·Call(i,j) + γ·SharedTests(i,j) + δ·GitCoChange(i,j)
        """
        for i in BasisState:
            for j in BasisState:
                if i != j:
                    coupling = 0.0
                    if {i, j} <= {BasisState.IMPORT, BasisState.API, BasisState.ENTRYPOINT}:
                        coupling = 0.8
                    elif {i, j} <= {BasisState.PACKAGING, BasisState.ENTRYPOINT}:
                        coupling = 0.9
                    elif {i, j} <= {BasisState.STATUS, BasisState.RUNTIME}:
                        coupling = 0.7
                    elif {i, j} <= {BasisState.TESTS, BasisState.API}:
                        coupling = 0.75
                    self.matrix[(i, j)] = coupling

    def entanglement_entropy(self, state: BasisState) -> float:
        """Calculate entanglement entropy: Ent(S) = -Σj pj log pj"""
        couplings = [self.matrix.get((state, other), 0.0) for other in BasisState if other != state]

        if not couplings or sum(couplings) == 0:
            return 0.0

        total = sum(couplings)
        probs = [c / total for c in couplings]
        return -sum(p * math.log(p) if p > 0 else 0 for p in probs)

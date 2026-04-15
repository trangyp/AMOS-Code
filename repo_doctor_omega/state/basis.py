"""Repository state vector formalism.

Defines the 12-dimensional integrity space basis vectors
and the repository wavefunction.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto


class BasisVector(Enum):
    """12 basis vectors for repository integrity space."""

    SYNTAX = auto()  # |S⟩ - parse integrity
    IMPORT = auto()  # |I⟩ - import/resolution integrity
    TYPE = auto()  # |Ty⟩ - type and signature integrity
    API = auto()  # |A⟩ - public API integrity
    ENTRYPOINT = auto()  # |E⟩ - entrypoint/launcher integrity
    PACKAGING = auto()  # |Pk⟩ - packaging/build integrity
    RUNTIME = auto()  # |Rt⟩ - runtime integrity
    PERSISTENCE = auto()  # |Ps⟩ - persistence/schema integrity
    STATUS = auto()  # |St⟩ - status-truth integrity
    TEST = auto()  # |T⟩ - test integrity
    DOCS = auto()  # |D⟩ - docs/demos/tutorial integrity
    SECURITY = auto()  # |Sec⟩ - security integrity
    HISTORY = auto()  # |H⟩ - temporal/history integrity


@dataclass
class Amplitude:
    """Integrity coefficient for a basis vector."""

    basis: BasisVector
    value: float  # ∈ [0, 1], 1.0 = intact, 0.0 = collapsed
    confidence: float = 1.0  # measurement confidence

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class RepositoryState:
    """Repository wavefunction |Ψ_repo(t)⟩.

    Represents the repository as a superposition of integrity basis states:

    |Ψ_repo(t)⟩ = Σ αk(t)|k⟩

    where αk ∈ [0,1] are integrity amplitudes.
    """

    timestamp: float
    amplitudes: dict[BasisVector, Amplitude] = field(default_factory=dict)
    observables: list[ObservableRef] = field(default_factory=list)
    mixed_state_hypotheses: list[RepositoryState] = field(default_factory=list)

    def __post_init__(self):
        # Initialize all basis vectors if not present
        for basis in BasisVector:
            if basis not in self.amplitudes:
                self.amplitudes[basis] = Amplitude(basis, 1.0)

    def get_amplitude(self, basis: BasisVector) -> float:
        """Get integrity coefficient for basis vector."""
        return self.amplitudes.get(basis, Amplitude(basis, 1.0)).value

    def set_amplitude(self, basis: BasisVector, value: float, confidence: float = 1.0):
        """Set integrity coefficient for basis vector."""
        self.amplitudes[basis] = Amplitude(basis, value, confidence)

    def compute_energy(self, weights: dict[BasisVector, float] | None = None) -> float:
        """Compute repository energy E_repo(t).

        E_repo = Σ λk (1 - αk)²

        Higher energy = more degraded.
        """
        if weights is None:
            weights = self._default_weights()

        energy = 0.0
        for basis, amp in self.amplitudes.items():
            weight = weights.get(basis, 1.0)
            degradation = 1.0 - amp.value
            energy += weight * (degradation**2)

        return energy

    def is_releaseable(self, threshold: float = 10.0) -> bool:
        """Check if repository meets release criteria."""
        return self.compute_energy() < threshold

    def compute_drift(self, previous: RepositoryState) -> float:
        """Compute state drift ||ΔΨ(t)||.

        ||ΔΨ(t)|| = sqrt(Σ (Δαk)²)
        """
        total = 0.0
        for basis in BasisVector:
            delta = self.get_amplitude(basis) - previous.get_amplitude(basis)
            total += delta**2
        return math.sqrt(total)

    def collapsed_subsystems(self, threshold: float = 0.5) -> list[BasisVector]:
        """Return list of degraded subsystems below threshold."""
        return [basis for basis in BasisVector if self.get_amplitude(basis) < threshold]

    @staticmethod
    def _default_weights() -> dict[BasisVector, float]:
        """Default Hamiltonian weights λk."""
        return {
            BasisVector.SYNTAX: 100.0,
            BasisVector.IMPORT: 95.0,
            BasisVector.TYPE: 75.0,
            BasisVector.API: 95.0,
            BasisVector.ENTRYPOINT: 90.0,
            BasisVector.PACKAGING: 90.0,
            BasisVector.RUNTIME: 85.0,
            BasisVector.PERSISTENCE: 70.0,
            BasisVector.STATUS: 70.0,
            BasisVector.TEST: 80.0,
            BasisVector.DOCS: 45.0,
            BasisVector.SECURITY: 100.0,
            BasisVector.HISTORY: 60.0,
        }

    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "timestamp": self.timestamp,
            "amplitudes": {
                b.name: {"value": a.value, "confidence": a.confidence}
                for b, a in self.amplitudes.items()
            },
            "energy": self.compute_energy(),
            "releaseable": self.is_releaseable(),
            "collapsed": [b.name for b in self.collapsed_subsystems()],
        }


@dataclass
class ObservableRef:
    """Reference to an observable affecting this state."""

    observable_id: str
    kind: str
    severity: float
    basis_affected: list[BasisVector]

from __future__ import annotations

"""Repository state vector formalism.

Defines the 12-dimensional integrity space basis vectors
and the repository wavefunction.
"""

import math
from dataclasses import dataclass, field
from enum import Enum, auto


class BasisVector(Enum):
    """27 basis vectors for repository integrity space.

    Expanded to cover:
    - Implementation layers (syntax, import, type, API)
    - Operational layers (runtime, persistence, status, test)
    - Documentation layers (docs, packaging, entrypoint)
    - Security and temporal layers (security, history)
    - Meta-architecture layers (law, ecology, path, observer, evidence, topology, anti-objective)
    - Semantic layers (silence, invariant-order, emergency, constraint-provenance)
    - Institutional layers (model-transport, world-drift, legibility, commons)
    """

    # Implementation integrity
    SYNTAX = auto()  # |S⟩ - parse integrity
    IMPORT = auto()  # |I⟩ - import/resolution integrity
    TYPE = auto()  # |Ty⟩ - type and signature integrity
    API = auto()  # |A⟩ - public API integrity
    ENTRYPOINT = auto()  # |E⟩ - entrypoint/launcher integrity

    # Operational integrity
    PACKAGING = auto()  # |Pk⟩ - packaging/build integrity
    RUNTIME = auto()  # |Rt⟩ - runtime integrity
    PERSISTENCE = auto()  # |Ps⟩ - persistence/schema integrity
    STATUS = auto()  # |St⟩ - status-truth integrity
    TEST = auto()  # |T⟩ - test integrity

    # Documentation and security
    DOCS = auto()  # |D⟩ - docs/demos/tutorial integrity
    SECURITY = auto()  # |Sec⟩ - security integrity
    HISTORY = auto()  # |H⟩ - temporal/history integrity

    # Meta-architecture: Law hierarchy
    LAW_HIERARCHY = auto()  # |Law⟩ - invariant precedence and conflict resolution
    LAW_SCOPE = auto()  # |Scope⟩ - law applicability boundaries
    EMERGENCY_CONSTITUTION = auto()  # |Emerg⟩ - emergency mode integrity

    # Meta-architecture: Silence and semantics
    SILENCE = auto()  # |Sil⟩ - silence/absence semantics
    ABSTENTION = auto()  # |Abst⟩ - abstention vs denial distinction
    NEGATIVE_EVIDENCE = auto()  # |NegEvid⟩ - missing evidence as signal

    # Meta-architecture: Constraint provenance
    CONSTRAINT_PROVENANCE = auto()  # |Prov⟩ - constraint origin and rationale
    CONSTRAINT_TAINT = auto()  # |Taint⟩ - workaround-to-policy drift

    # Meta-architecture: Observer plurality
    OBSERVER_PLURALITY = auto()  # |ObsPl⟩ - multi-observer coherence
    OBSERVER_PRECEDENCE = auto()  # |ObsPr⟩ - observer conflict resolution

    # Meta-architecture: Evidence and survival
    EVIDENCE_SURVIVAL = auto()  # |EvidSur⟩ - evidence horizon preservation
    RECOVERY_EVIDENCE = auto()  # |RecEvid⟩ - recovery action traceability

    # Meta-architecture: Path and history
    PATH_DEPENDENCE = auto()  # |Path⟩ - history-shaped state equivalence
    NON_ERGODIC = auto()  # |NonErg⟩ - rare-event sensitivity

    # Meta-architecture: Topology
    TOPOLOGY_REWRITE = auto()  # |Topo⟩ - split/merge/extraction integrity
    TOPOLOGY_NEUTRALIZE = auto()  # |Neut⟩ - old topology retirement

    # Meta-architecture: Anti-objectives
    ANTI_OBJECTIVE = auto()  # |Anti⟩ - forbidden optimization directions
    PROXY_CAPTURE = auto()  # |Proxy⟩ - Goodhart's law protection

    # Meta-architecture: Model and world
    MODEL_TRANSPORT = auto()  # |ModTr⟩ - proof/model scope preservation
    WORLD_DRIFT = auto()  # |World⟩ - world-model alignment
    MODEL_FEDERATION = auto()  # |Fed⟩ - cross-model consistency

    # Meta-architecture: Institutional
    LEGIBILITY = auto()  # |Legib⟩ - reconstructability without tribal knowledge
    COMMONS = auto()  # |Comm⟩ - shared surface protection
    SHADOW_CONSTITUTION = auto()  # |Shadow⟩ - declared vs actual governance

    # Meta-architecture: Proof and assumption
    PROOF_TRANSPORT = auto()  # |ProofTr⟩ - assumption preservation across contexts
    ASSUMPTION_VISIBILITY = auto()  # |Assump⟩ - assumption metadata preservation

    # Ultimate meta-architecture: Modality system
    MODAL_INTEGRITY = auto()  # |Modal⟩ - required/allowed/forbidden/optional distinction
    MODAL_COLLAPSE = auto()  # |ModCol⟩ - modality confusion prevention

    # Ultimate meta-architecture: Obligation system
    OBLIGATION_LIFECYCLE = auto()  # |Obl⟩ - duty creation/maturity/discharge
    OBLIGATION_TRANSFER = auto()  # |OblTr⟩ - duty transfer integrity
    PROMISE_INTEGRITY = auto()  # |Prom⟩ - promise creation and fulfillment

    # Ultimate meta-architecture: Memory and forgetting
    MEMORY_DISCIPLINE = auto()  # |Mem⟩ - what must be remembered
    FORGETTING_SAFETY = auto()  # |Forget⟩ - safe forgetting with tombstones
    TOMBSTONE_INTEGRITY = auto()  # |Tomb⟩ - deletion evidence preservation

    # Ultimate meta-architecture: Substitution
    SUBSTITUTION_INTEGRITY = auto()  # |Subst⟩ - semantic preservation under substitution

    # Ultimate meta-architecture: Counterparty and externality
    COUNTERPARTY_INTEGRITY = auto()  # |Cpty⟩ - external obligation representation
    EXTERNALITY_BOUNDEDNESS = auto()  # |Ext⟩ - irretractable emission control
    RECIPROCITY_INTEGRITY = auto()  # |Recip⟩ - bilateral obligation preservation

    # Ultimate meta-architecture: Narrative and explanation
    NARRATIVE_COHERENCE = auto()  # |Narr⟩ - story consistency across surfaces
    EXPLAINABILITY = auto()  # |Expl⟩ - decision attribution and explanation

    # Ultimate meta-architecture: Undecidability and incompleteness
    UNDECIDABILITY_AWARENESS = auto()  # |Undec⟩ - explicit handling of unprovable claims
    SPECIFICATION_COMPLETENESS = auto()  # |Spec⟩ - explicit incompleteness marking

    # Ultimate meta-architecture: Bootstrap and genesis
    BOOTSTRAP_INTEGRITY = auto()  # |Boot⟩ - first-law and anchor semantics
    ANCHOR_SUCCESSION = auto()  # |Anchor⟩ - truth anchor rotation safety

    # Ultimate meta-architecture: Ecology and adaptation
    ECOLOGICAL_AWARENESS = auto()  # |Ecol⟩ - external participant modeling
    MORAL_HAZARD_RESISTANCE = auto()  # |Moral⟩ - incentive alignment protection

    # Ultimate meta-architecture: Retroactivity and time
    RETROACTIVITY_SAFETY = auto()  # |Retro⟩ - backward change safety


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

    def compute_energy(self, weights: dict[BasisVector, float] = None) -> float:
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
        """Default Hamiltonian weights λk.

        Weights reflect criticality to release and operational integrity:
        - 100: Security, Syntax (blocking)
        - 95: API, Import, Law Hierarchy (core contracts)
        - 90: Entrypoint, Packaging, Emergency Constitution
        - 85: Runtime, Observer Plurality
        - 80: Test, Evidence Survival
        - 75: Type, Constraint Provenance
        - 70: Persistence, Status, Topology Rewrite
        - 65: History, Path Dependence, Model Transport
        - 60: Silence, Legibility, World Drift
        - 55: Docs, Commons, Shadow Constitution
        - 50: Law Scope, Anti-Objective, Proof Transport
        - 45: Abstention, Recovery Evidence, Model Federation
        - 40: Negative Evidence, Constraint Taint, Non-Ergodic
        - 35: Observer Precedence, Topology Neutralize
        - 30: Proxy Capture, Assumption Visibility
        """
        return {
            # Core implementation (highest weight)
            BasisVector.SYNTAX: 100.0,
            BasisVector.IMPORT: 95.0,
            BasisVector.TYPE: 75.0,
            BasisVector.API: 95.0,
            BasisVector.ENTRYPOINT: 90.0,
            # Operational layers
            BasisVector.PACKAGING: 90.0,
            BasisVector.RUNTIME: 85.0,
            BasisVector.PERSISTENCE: 70.0,
            BasisVector.STATUS: 70.0,
            BasisVector.TEST: 80.0,
            # Documentation and security
            BasisVector.DOCS: 45.0,
            BasisVector.SECURITY: 100.0,
            BasisVector.HISTORY: 65.0,
            # Meta-architecture: Law hierarchy (critical for governance)
            BasisVector.LAW_HIERARCHY: 95.0,
            BasisVector.LAW_SCOPE: 50.0,
            BasisVector.EMERGENCY_CONSTITUTION: 90.0,
            # Meta-architecture: Silence and semantics
            BasisVector.SILENCE: 60.0,
            BasisVector.ABSTENTION: 45.0,
            BasisVector.NEGATIVE_EVIDENCE: 40.0,
            # Meta-architecture: Constraint provenance
            BasisVector.CONSTRAINT_PROVENANCE: 75.0,
            BasisVector.CONSTRAINT_TAINT: 40.0,
            # Meta-architecture: Observer plurality
            BasisVector.OBSERVER_PLURALITY: 85.0,
            BasisVector.OBSERVER_PRECEDENCE: 35.0,
            # Meta-architecture: Evidence and survival
            BasisVector.EVIDENCE_SURVIVAL: 80.0,
            BasisVector.RECOVERY_EVIDENCE: 45.0,
            # Meta-architecture: Path and history
            BasisVector.PATH_DEPENDENCE: 65.0,
            BasisVector.NON_ERGODIC: 40.0,
            # Meta-architecture: Topology
            BasisVector.TOPOLOGY_REWRITE: 70.0,
            BasisVector.TOPOLOGY_NEUTRALIZE: 35.0,
            # Meta-architecture: Anti-objectives
            BasisVector.ANTI_OBJECTIVE: 50.0,
            BasisVector.PROXY_CAPTURE: 30.0,
            # Meta-architecture: Model and world
            BasisVector.MODEL_TRANSPORT: 65.0,
            BasisVector.WORLD_DRIFT: 60.0,
            BasisVector.MODEL_FEDERATION: 45.0,
            # Meta-architecture: Institutional
            BasisVector.LEGIBILITY: 60.0,
            BasisVector.COMMONS: 55.0,
            BasisVector.SHADOW_CONSTITUTION: 55.0,
            # Meta-architecture: Proof and assumption
            BasisVector.PROOF_TRANSPORT: 50.0,
            BasisVector.ASSUMPTION_VISIBILITY: 30.0,
            # Ultimate meta-architecture: Modality (high - governs what is allowed)
            BasisVector.MODAL_INTEGRITY: 88.0,
            BasisVector.MODAL_COLLAPSE: 82.0,
            # Ultimate meta-architecture: Obligation (high - duties through time)
            BasisVector.OBLIGATION_LIFECYCLE: 87.0,
            BasisVector.OBLIGATION_TRANSFER: 78.0,
            BasisVector.PROMISE_INTEGRITY: 85.0,
            # Ultimate meta-architecture: Memory (medium-high - what must be remembered)
            BasisVector.MEMORY_DISCIPLINE: 76.0,
            BasisVector.FORGETTING_SAFETY: 74.0,
            BasisVector.TOMBSTONE_INTEGRITY: 72.0,
            # Ultimate meta-architecture: Substitution (medium - semantic preservation)
            BasisVector.SUBSTITUTION_INTEGRITY: 68.0,
            # Ultimate meta-architecture: Counterparty (high - external obligations)
            BasisVector.COUNTERPARTY_INTEGRITY: 86.0,
            BasisVector.EXTERNALITY_BOUNDEDNESS: 84.0,
            BasisVector.RECIPROCITY_INTEGRITY: 80.0,
            # Ultimate meta-architecture: Narrative (medium - story coherence)
            BasisVector.NARRATIVE_COHERENCE: 62.0,
            BasisVector.EXPLAINABILITY: 64.0,
            # Ultimate meta-architecture: Undecidability (medium - truth bounds)
            BasisVector.UNDECIDABILITY_AWARENESS: 58.0,
            BasisVector.SPECIFICATION_COMPLETENESS: 56.0,
            # Ultimate meta-architecture: Bootstrap (high - foundation integrity)
            BasisVector.BOOTSTRAP_INTEGRITY: 92.0,
            BasisVector.ANCHOR_SUCCESSION: 88.0,
            # Ultimate meta-architecture: Ecology (medium - external adaptation)
            BasisVector.ECOLOGICAL_AWARENESS: 54.0,
            BasisVector.MORAL_HAZARD_RESISTANCE: 52.0,
            # Ultimate meta-architecture: Retroactivity (high - backward change safety)
            BasisVector.RETROACTIVITY_SAFETY: 90.0,
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

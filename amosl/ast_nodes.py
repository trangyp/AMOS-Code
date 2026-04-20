"""AMOSL AST node definitions.

Implements the 9-tuple language structure:
(O, S, D, C, E, M, U, V, A, R)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Substrate(Enum):
    """Computational substrate types."""

    CLASSICAL = auto()
    QUANTUM = auto()
    BIOLOGICAL = auto()
    HYBRID = auto()


@dataclass
class Location:
    """Source code location."""

    line: int
    column: int
    file: str = "<stdin>"


@dataclass
class ASTNode:
    """Base AST node."""

    loc: Location = None


# =============================================================================
# Program
# =============================================================================


@dataclass
class Program(ASTNode):
    """Root program node.

    Represents: Program = Ontology + State + Dynamics + Constraints +
                          Observation + Evolution + Verification
    """

    ontology: OntologyDecl = field(default_factory=lambda: OntologyDecl())
    state: StateDecl = field(default_factory=lambda: StateDecl())
    dynamics: DynamicsDecl = field(default_factory=lambda: DynamicsDecl())
    constraints: list[ConstraintDecl] = field(default_factory=list)
    effects: list[EffectDecl] = field(default_factory=list)
    measures: list[MeasureDecl] = field(default_factory=list)
    uncertainties: list[UncertaintyDecl] = field(default_factory=list)
    verifies: list[VerifyDecl] = field(default_factory=list)
    adapts: list[AdaptDecl] = field(default_factory=list)
    realizes: RealizeDecl = field(default_factory=lambda: RealizeDecl())


# =============================================================================
# 9-Tuple Components
# =============================================================================


@dataclass
class OntologyDecl(ASTNode):
    """O - Ontology declaration.

    Defines what exists in the computational universe:
    O = O_c ⊕ O_q ⊕ O_b ⊕ O_h
    """

    classical: list[EntityDecl] = field(default_factory=list)
    quantum: list[QuantumEntityDecl] = field(default_factory=list)
    biological: list[BioEntityDecl] = field(default_factory=list)
    hybrid: list[HybridEntityDecl] = field(default_factory=list)


@dataclass
class StateDecl(ASTNode):
    """S - State space declaration.

    Σ = ⟨Σ_c, Σ_q, Σ_b, Σ_h, Σ_e, Σ_t⟩
    """

    classical: list[StateVar] = field(default_factory=list)
    quantum: list[QuantumState] = field(default_factory=list)
    biological: list[BioState] = field(default_factory=list)
    hybrid: list[HybridState] = field(default_factory=list)
    environment: list[EnvVar] = field(default_factory=list)
    time: TimeDecl = None


@dataclass
class DynamicsDecl(ASTNode):
    """D - Dynamics/transition declaration.

    Σ_{t+1} = F(Σ_t, α_t, μ_t, ε_t, τ_t)
    """

    transitions: list[Transition] = field(default_factory=list)
    actions: list[ActionDecl] = field(default_factory=list)
    evolutions: list[Evolution] = field(default_factory=list)


@dataclass
class ConstraintDecl(ASTNode):
    """C - Constraint declaration.

    C = {C_i : Σ → B_U}
    """

    name: str = ""
    expr: Expr = field(default_factory=lambda: Expr())
    substrate: Substrate = Substrate.CLASSICAL


@dataclass
class EffectDecl(ASTNode):
    """E - Effect declaration.

    E = E_c ⊕ E_q ⊕ E_b ⊕ E_h
    """

    name: str = ""
    effects: list[str] = field(default_factory=list)
    substrate: Substrate = Substrate.CLASSICAL


@dataclass
class MeasureDecl(ASTNode):
    """M - Observation/Measurement declaration.

    Observe : Σ → ⟨estimate, uncertainty, perturbation, Σ'⟩
    """

    target: str = ""
    uncertainty: UncertaintyDecl = field(default_factory=lambda: UncertaintyDecl())
    perturbation: Expr = None


@dataclass
class UncertaintyDecl(ASTNode):
    """U - Uncertainty declaration.

    U = ⟨p, γ, δ, κ⟩
    """

    probability: Expr = None
    confidence: Expr = None
    width: Expr = None
    context: Expr = None


@dataclass
class VerifyDecl(ASTNode):
    """V - Verification declaration.

    V = V_c ⊕ V_q ⊕ V_b ⊕ V_h
    """

    checks: list[str] = field(default_factory=list)
    substrate: Substrate = Substrate.CLASSICAL


@dataclass
class AdaptDecl(ASTNode):
    """A - Adaptation/Evolution declaration.

    X_{t+1} = A(X_t, feedback_t, environment_t, constraints)
    """

    target: str = ""
    mutation: Expr = None
    selection: Expr = None
    refinement: Expr = None


@dataclass
class RealizeDecl(ASTNode):
    """R - Realization/Runtime declaration.

    R = ⟨Frontend, Semantics, Graph, IR, Verify, Plan, Runtime, Trace⟩
    """

    frontend: str = "default"
    target: str = "python"
    trace: bool = True


# =============================================================================
# Ontology Components
# =============================================================================


@dataclass
class EntityDecl(ASTNode):
    """Classical entity declaration."""

    name: str = ""
    fields: list[Field] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)


@dataclass
class QuantumEntityDecl(ASTNode):
    """Quantum entity declaration."""

    name: str = ""
    qubits: int = 1
    registers: list[str] = field(default_factory=list)
    observables: list[str] = field(default_factory=list)
    circuit: Circuit = None


@dataclass
class BioEntityDecl(ASTNode):
    """Biological entity declaration."""

    name: str = ""
    dna: str = None
    rna: str = None
    protein: str = None
    reactions: list[Reaction] = field(default_factory=list)


@dataclass
class HybridEntityDecl(ASTNode):
    """Hybrid entity declaration."""

    name: str = ""
    bridges: list[Bridge] = field(default_factory=list)
    mappings: list[Mapping] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)


# =============================================================================
# State Components
# =============================================================================


@dataclass
class StateVar(ASTNode):
    """Classical state variable."""

    name: str = ""
    type_name: str = "Any"
    initial: Expr = None


@dataclass
class QuantumState(ASTNode):
    """Quantum state variable."""

    name: str = ""
    amplitude: Expr = None
    density: bool = False


@dataclass
class BioState(ASTNode):
    """Biological state variable."""

    name: str = ""
    concentration: Expr = None
    expression: Expr = None
    population: Expr = None


@dataclass
class HybridState(ASTNode):
    """Hybrid state variable."""

    name: str = ""
    source: str = ""
    target: str = ""
    threshold: Expr = None


@dataclass
class EnvVar(ASTNode):
    """Environment variable."""

    name: str = ""
    type_name: str = "Any"


@dataclass
class TimeDecl(ASTNode):
    """Time declaration."""

    discrete: bool = True
    step: Expr = None


# =============================================================================
# Dynamics Components
# =============================================================================


@dataclass
class Transition(ASTNode):
    """State transition."""

    from_state: str = ""
    to_state: str = ""
    condition: Expr = None
    action: str = None


@dataclass
class ActionDecl(ASTNode):
    """Action declaration."""

    name: str = ""
    pre: Expr = None
    post: Expr = None
    effects: list[str] = field(default_factory=list)


@dataclass
class Evolution(ASTNode):
    """Evolution rule."""

    target: str = ""
    rule: str = "mutate"
    rate: Expr = None


# =============================================================================
# Supporting Types
# =============================================================================


@dataclass
class Field(ASTNode):
    """Field declaration."""

    name: str = ""
    type_name: str = "Any"


@dataclass
class Circuit(ASTNode):
    """Quantum circuit."""

    gates: list[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class Reaction(ASTNode):
    """Biological reaction."""

    reactants: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    rate: Expr = None


@dataclass
class Bridge(ASTNode):
    """Hybrid bridge."""

    source: str = ""
    target: str = ""
    signal: str = ""
    compat_check: bool = True


@dataclass
class Mapping(ASTNode):
    """Hybrid mapping."""

    from_type: str = ""
    to_type: str = ""
    function: str = ""


@dataclass
class Signal(ASTNode):
    """Hybrid signal."""

    name: str = ""
    type_name: str = ""
    threshold: Expr = None


@dataclass
class Expr(ASTNode):
    """Expression placeholder."""

    text: str = ""

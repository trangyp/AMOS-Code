"""AMOSL AST node definitions.

Implements the 9-tuple language structure:
(O, S, D, C, E, M, U, V, A, R)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional


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

    loc: Optional[Location] = None


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
    constraints: List[ConstraintDecl] = field(default_factory=list)
    effects: List[EffectDecl] = field(default_factory=list)
    measures: List[MeasureDecl] = field(default_factory=list)
    uncertainties: List[UncertaintyDecl] = field(default_factory=list)
    verifies: List[VerifyDecl] = field(default_factory=list)
    adapts: List[AdaptDecl] = field(default_factory=list)
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

    classical: List[EntityDecl] = field(default_factory=list)
    quantum: List[QuantumEntityDecl] = field(default_factory=list)
    biological: List[BioEntityDecl] = field(default_factory=list)
    hybrid: List[HybridEntityDecl] = field(default_factory=list)


@dataclass
class StateDecl(ASTNode):
    """S - State space declaration.

    Σ = ⟨Σ_c, Σ_q, Σ_b, Σ_h, Σ_e, Σ_t⟩
    """

    classical: List[StateVar] = field(default_factory=list)
    quantum: List[QuantumState] = field(default_factory=list)
    biological: List[BioState] = field(default_factory=list)
    hybrid: List[HybridState] = field(default_factory=list)
    environment: List[EnvVar] = field(default_factory=list)
    time: Optional[TimeDecl] = None


@dataclass
class DynamicsDecl(ASTNode):
    """D - Dynamics/transition declaration.

    Σ_{t+1} = F(Σ_t, α_t, μ_t, ε_t, τ_t)
    """

    transitions: List[Transition] = field(default_factory=list)
    actions: List[ActionDecl] = field(default_factory=list)
    evolutions: List[Evolution] = field(default_factory=list)


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
    effects: List[str] = field(default_factory=list)
    substrate: Substrate = Substrate.CLASSICAL


@dataclass
class MeasureDecl(ASTNode):
    """M - Observation/Measurement declaration.

    Observe : Σ → ⟨estimate, uncertainty, perturbation, Σ'⟩
    """

    target: str = ""
    uncertainty: UncertaintyDecl = field(default_factory=lambda: UncertaintyDecl())
    perturbation: Optional[Expr] = None


@dataclass
class UncertaintyDecl(ASTNode):
    """U - Uncertainty declaration.

    U = ⟨p, γ, δ, κ⟩
    """

    probability: Optional[Expr] = None
    confidence: Optional[Expr] = None
    width: Optional[Expr] = None
    context: Optional[Expr] = None


@dataclass
class VerifyDecl(ASTNode):
    """V - Verification declaration.

    V = V_c ⊕ V_q ⊕ V_b ⊕ V_h
    """

    checks: List[str] = field(default_factory=list)
    substrate: Substrate = Substrate.CLASSICAL


@dataclass
class AdaptDecl(ASTNode):
    """A - Adaptation/Evolution declaration.

    X_{t+1} = A(X_t, feedback_t, environment_t, constraints)
    """

    target: str = ""
    mutation: Optional[Expr] = None
    selection: Optional[Expr] = None
    refinement: Optional[Expr] = None


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
    fields: List[Field] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)


@dataclass
class QuantumEntityDecl(ASTNode):
    """Quantum entity declaration."""

    name: str = ""
    qubits: int = 1
    registers: List[str] = field(default_factory=list)
    observables: List[str] = field(default_factory=list)
    circuit: Optional[Circuit] = None


@dataclass
class BioEntityDecl(ASTNode):
    """Biological entity declaration."""

    name: str = ""
    dna: str = None
    rna: str = None
    protein: str = None
    reactions: List[Reaction] = field(default_factory=list)


@dataclass
class HybridEntityDecl(ASTNode):
    """Hybrid entity declaration."""

    name: str = ""
    bridges: List[Bridge] = field(default_factory=list)
    mappings: List[Mapping] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)


# =============================================================================
# State Components
# =============================================================================


@dataclass
class StateVar(ASTNode):
    """Classical state variable."""

    name: str = ""
    type_name: str = "Any"
    initial: Optional[Expr] = None


@dataclass
class QuantumState(ASTNode):
    """Quantum state variable."""

    name: str = ""
    amplitude: Optional[Expr] = None
    density: bool = False


@dataclass
class BioState(ASTNode):
    """Biological state variable."""

    name: str = ""
    concentration: Optional[Expr] = None
    expression: Optional[Expr] = None
    population: Optional[Expr] = None


@dataclass
class HybridState(ASTNode):
    """Hybrid state variable."""

    name: str = ""
    source: str = ""
    target: str = ""
    threshold: Optional[Expr] = None


@dataclass
class EnvVar(ASTNode):
    """Environment variable."""

    name: str = ""
    type_name: str = "Any"


@dataclass
class TimeDecl(ASTNode):
    """Time declaration."""

    discrete: bool = True
    step: Optional[Expr] = None


# =============================================================================
# Dynamics Components
# =============================================================================


@dataclass
class Transition(ASTNode):
    """State transition."""

    from_state: str = ""
    to_state: str = ""
    condition: Optional[Expr] = None
    action: str = None


@dataclass
class ActionDecl(ASTNode):
    """Action declaration."""

    name: str = ""
    pre: Optional[Expr] = None
    post: Optional[Expr] = None
    effects: List[str] = field(default_factory=list)


@dataclass
class Evolution(ASTNode):
    """Evolution rule."""

    target: str = ""
    rule: str = "mutate"
    rate: Optional[Expr] = None


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

    gates: List[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class Reaction(ASTNode):
    """Biological reaction."""

    reactants: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    rate: Optional[Expr] = None


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
    threshold: Optional[Expr] = None


@dataclass
class Expr(ASTNode):
    """Expression placeholder."""

    text: str = ""

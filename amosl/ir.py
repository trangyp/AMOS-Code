"""AMOSL Intermediate Representations (IR).

IR_AMOS = CIR ⊕ QIR ⊕ BIR ⊕ HIR
"""

from dataclasses import dataclass, field
from typing import List, Tuple

# =============================================================================
# Classical IR (CIR)
# =============================================================================


@dataclass
class CIR:
    """Classical Intermediate Representation.

    CIR = ⟨Blocks, Ops, Effects, Guards⟩
    """

    blocks: List[CIRBlock] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)


@dataclass
class CIRBlock:
    """CIR Basic Block."""

    name: str = ""
    ops: List[CIROp] = field(default_factory=list)
    guard: CIRGuard = field(default_factory=lambda: CIRGuard())


@dataclass
class CIROp:
    """CIR Operation."""

    opcode: str = ""
    operands: List[str] = field(default_factory=list)
    result: str = ""


@dataclass
class CIRGuard:
    """CIR Guard condition."""

    condition: str = ""
    target: str = ""


# =============================================================================
# Quantum IR (QIR)
# =============================================================================


@dataclass
class QIR:
    """Quantum Intermediate Representation.

    QIR = ⟨Registers, Gates, Measures, Constraints⟩
    """

    registers: List[QIRRegister] = field(default_factory=list)
    gates: List[QIRGate] = field(default_factory=list)
    measures: List[QIRMeasure] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class QIRRegister:
    """QIR Quantum Register."""

    name: str = ""
    size: int = 1
    initial_state: str = "|0⟩"


@dataclass
class QIRGate:
    """QIR Quantum Gate."""

    name: str = ""
    targets: List[int] = field(default_factory=list)
    controls: List[int] = field(default_factory=list)
    params: List[float] = field(default_factory=list)


@dataclass
class QIRMeasure:
    """QIR Measurement."""

    register: str = ""
    basis: str = "computational"
    classical_target: str = ""


# =============================================================================
# Biological IR (BIR)
# =============================================================================


@dataclass
class BIR:
    """Biological Intermediate Representation.

    BIR = ⟨Species, Sequences, Reactions, RegulatoryRules, Rates⟩
    """

    species: List[BIRSpecies] = field(default_factory=list)
    sequences: List[BIRSequence] = field(default_factory=list)
    reactions: List[BIRReaction] = field(default_factory=list)
    regulations: List[BIRRegulation] = field(default_factory=list)


@dataclass
class BIRSpecies:
    """BIR Species (molecular species)."""

    name: str = ""
    initial_conc: float = 0.0
    type_name: str = "protein"


@dataclass
class BIRSequence:
    """BIR Sequence (DNA/RNA/Protein)."""

    name: str = ""
    seq_type: str = "dna"  # dna, rna, protein
    sequence: str = ""


@dataclass
class BIRReaction:
    """BIR Reaction."""

    reactants: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    rate_constant: float = 1.0


@dataclass
class BIRRegulation:
    """BIR Regulatory Rule."""

    target: str = ""
    activators: List[str] = field(default_factory=list)
    repressors: List[str] = field(default_factory=list)
    basal_rate: float = 0.1


# =============================================================================
# Hybrid IR (HIR)
# =============================================================================


@dataclass
class HIR:
    """Hybrid Intermediate Representation.

    HIR = ⟨Bridges, Schedules, Observations, Mappings, UncertaintyFlows⟩
    """

    bridges: List[HIRBridge] = field(default_factory=list)
    schedules: List[HIRSchedule] = field(default_factory=list)
    observations: List[HIRObservation] = field(default_factory=list)
    mappings: List[HIRMapping] = field(default_factory=list)


@dataclass
class HIRBridge:
    """HIR Bridge between substrates."""

    name: str = ""
    source_substrate: str = ""
    target_substrate: str = ""
    source_var: str = ""
    target_var: str = ""
    transform: str = "identity"
    valid: bool = True


@dataclass
class HIRSchedule:
    """HIR Execution Schedule."""

    name: str = ""
    order: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class HIRObservation:
    """HIR Observation point."""

    name: str = ""
    target: str = ""
    uncertainty: float = 0.0
    perturbation: float = 0.0


@dataclass
class HIRMapping:
    """HIR Type/Value Mapping."""

    from_type: str = ""
    to_type: str = ""
    function: str = ""
    scale_factor: float = 1.0


# =============================================================================
# IR Operations
# =============================================================================


def create_empty_ir() -> Tuple[CIR, QIR, BIR, HIR]:
    """Create empty IR tuple."""
    return CIR(), QIR(), BIR(), HIR()


def merge_cir(ir1: CIR, ir2: CIR) -> CIR:
    """Merge two CIR instances."""
    return CIR(blocks=ir1.blocks + ir2.blocks, effects=list(set(ir1.effects + ir2.effects)))


def merge_qir(ir1: QIR, ir2: QIR) -> QIR:
    """Merge two QIR instances."""
    return QIR(
        registers=ir1.registers + ir2.registers,
        gates=ir1.gates + ir2.gates,
        measures=ir1.measures + ir2.measures,
        constraints=list(set(ir1.constraints + ir2.constraints)),
    )


def merge_bir(ir1: BIR, ir2: BIR) -> BIR:
    """Merge two BIR instances."""
    return BIR(
        species=ir1.species + ir2.species,
        sequences=ir1.sequences + ir2.sequences,
        reactions=ir1.reactions + ir2.reactions,
        regulations=ir1.regulations + ir2.regulations,
    )


def merge_hir(ir1: HIR, ir2: HIR) -> HIR:
    """Merge two HIR instances."""
    return HIR(
        bridges=ir1.bridges + ir2.bridges,
        schedules=ir1.schedules + ir2.schedules,
        observations=ir1.observations + ir2.observations,
        mappings=ir1.mappings + ir2.mappings,
    )

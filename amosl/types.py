"""AMOSL Type System.

τ ::= τ_c | τ_q | τ_b | τ_h
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Substrate(Enum):
    """Computational substrate."""

    CLASSICAL = auto()
    QUANTUM = auto()
    BIOLOGICAL = auto()
    HYBRID = auto()


@dataclass(frozen=True)
class Type:
    """Base type."""

    name: str
    substrate: Substrate


# Classical Types


class ClassicalType:
    """Classical types: Bool | Int | Float | Text | Record | Set | Map"""

    BOOL = Type("Bool", Substrate.CLASSICAL)
    INT = Type("Int", Substrate.CLASSICAL)
    FLOAT = Type("Float", Substrate.CLASSICAL)
    TEXT = Type("Text", Substrate.CLASSICAL)

    @staticmethod
    def Record(fields: dict[str, Type]) -> Type:
        return Type(f"Record({len(fields)})", Substrate.CLASSICAL)

    @staticmethod
    def Set(elem_type: Type) -> Type:
        return Type(f"Set({elem_type.name})", Substrate.CLASSICAL)

    @staticmethod
    def Map(key_type: Type, val_type: Type) -> Type:
        return Type(f"Map({key_type.name},{val_type.name})", Substrate.CLASSICAL)


# Quantum Types


class QuantumType:
    """Quantum types: Qubit | Register[n] | DensityMatrix | Hamiltonian"""

    QUBIT = Type("Qubit", Substrate.QUANTUM)
    DENSITY_MATRIX = Type("DensityMatrix", Substrate.QUANTUM)
    HAMILTONIAN = Type("Hamiltonian", Substrate.QUANTUM)

    @staticmethod
    def Register(n: int) -> Type:
        return Type(f"Register[{n}]", Substrate.QUANTUM)


# Biological Types


class BiologicalType:
    """Biological types: DNASeq | RNASeq | AminoSeq | Gene | Protein | Cell"""

    DNA_SEQ = Type("DNASeq", Substrate.BIOLOGICAL)
    RNA_SEQ = Type("RNASeq", Substrate.BIOLOGICAL)
    AMINO_SEQ = Type("AminoSeq", Substrate.BIOLOGICAL)
    GENE = Type("Gene", Substrate.BIOLOGICAL)
    PROTEIN = Type("Protein", Substrate.BIOLOGICAL)
    CELL = Type("Cell", Substrate.BIOLOGICAL)

    @staticmethod
    def Population(elem_type: Type) -> Type:
        return Type(f"Population({elem_type.name})", Substrate.BIOLOGICAL)


# Hybrid Types


class HybridType:
    """Hybrid types: Bridge | Signal | Mapping"""

    SIGNAL = Type("Signal", Substrate.HYBRID)

    @staticmethod
    def Bridge(src: Type, tgt: Type) -> Type:
        return Type(f"Bridge[{src.name},{tgt.name}]", Substrate.HYBRID)

    @staticmethod
    def Mapping(src: Type, tgt: Type) -> Type:
        return Type(f"Mapping[{src.name},{tgt.name}]", Substrate.HYBRID)


# Type checking


def type_compatible(t1: Type, t2: Type) -> bool:
    """Check if two types are compatible (for bridge formation)."""
    return t1.substrate == t2.substrate or t1.name == t2.name


def bridge_valid(src: Type, tgt: Type) -> bool:
    """Check if a bridge between types is valid.

    BridgeValid(b) ⇔ TypeCompat ∧ UnitCompat ∧ TimeCompat ∧ ObsCompat
    """
    # Type compatibility
    type_compat = type_compatible(src, tgt)

    # For hybrid bridges, substrates must be different
    hybrid_valid = src.substrate != tgt.substrate

    return type_compat and hybrid_valid

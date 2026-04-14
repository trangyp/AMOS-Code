"""AMOSL - Absolute Meta Operating System Language.

A unified multi-substrate programming language for classical, quantum,
biological, and hybrid computation.

Formal specification: 9-tuple (O,S,D,C,E,M,U,V,A,R)
"""
from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Trang Phan"

from .ast_nodes import (
    AdaptDecl,
    ConstraintDecl,
    DynamicsDecl,
    EffectDecl,
    MeasureDecl,
    OntologyDecl,
    Program,
    RealizeDecl,
    StateDecl,
    UncertaintyDecl,
    VerifyDecl,
)
from .compiler import compile_program
from .invariants import validate_invariants
from .ir import (
    BIR,
    CIR,
    HIR,
    QIR,
)
from .parser import parse
from .types import (
    BiologicalType,
    ClassicalType,
    HybridType,
    QuantumType,
    Type,
)

__all__ = [
    # AST nodes
    "Program",
    "OntologyDecl",
    "StateDecl",
    "DynamicsDecl",
    "ConstraintDecl",
    "EffectDecl",
    "MeasureDecl",
    "UncertaintyDecl",
    "VerifyDecl",
    "AdaptDecl",
    "RealizeDecl",
    # Types
    "Type",
    "ClassicalType",
    "QuantumType",
    "BiologicalType",
    "HybridType",
    # IR
    "CIR",
    "QIR",
    "BIR",
    "HIR",
    # Core functions
    "parse",
    "compile_program",
    "validate_invariants",
]

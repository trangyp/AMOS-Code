"""AMOSL - Absolute Meta Operating System Language.

A unified multi-substrate programming language for classical, quantum,
biological, and hybrid computation.

Formal specification: 9-tuple (O,S,D,C,E,M,U,V,A,R)
"""
from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Trang Phan"

from .ast_nodes import (
    Program,
    OntologyDecl,
    StateDecl,
    DynamicsDecl,
    ConstraintDecl,
    EffectDecl,
    MeasureDecl,
    UncertaintyDecl,
    VerifyDecl,
    AdaptDecl,
    RealizeDecl,
)
from .types import (
    Type,
    ClassicalType,
    QuantumType,
    BiologicalType,
    HybridType,
)
from .ir import (
    CIR,
    QIR,
    BIR,
    HIR,
)
from .parser import parse
from .compiler import compile_program
from .invariants import validate_invariants

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

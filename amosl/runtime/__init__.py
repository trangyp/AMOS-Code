"""AMOSL Reference Runtime - Executable Realization of Formal Specification.

Implements the 16-tuple formal system:
- State manifold (Σ_c, Σ_q, Σ_b, Σ_h, Σ_e, Σ_t)
- Evolution operator T (block matrix)
- 8 invariants (Λ)
- Bridge morphisms (B_i→j)
- Ledger system (L_t)
- Verification stack (V)

Based on: docs/AMOSL_FORMAL_SPECIFICATION.md
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Trang Phan"

from .kernel import (
    RuntimeKernel,
    StateManifold,
    ClassicalState,
    QuantumState,
    BiologicalState,
    HybridState,
)
from .evolution import EvolutionOperator, BlockMatrix
from .ledger import Ledger, TraceTensor
from .verify import VerificationEngine
from .bridge import BridgeExecutor

__all__ = [
    "RuntimeKernel",
    "StateManifold",
    "ClassicalState",
    "QuantumState",
    "BiologicalState",
    "HybridState",
    "EvolutionOperator",
    "BlockMatrix",
    "Ledger",
    "TraceTensor",
    "VerificationEngine",
    "BridgeExecutor",
]

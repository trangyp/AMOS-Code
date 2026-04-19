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

__version__ = "1.0.0"
__author__ = "Trang Phan"

from .kernel import (
    BiologicalState,
    ClassicalState,
    HybridState,
    QuantumState,
    RuntimeKernel,
    StateManifold,
)

__all__ = [
    "RuntimeKernel",
    "StateManifold",
    "ClassicalState",
    "QuantumState",
    "BiologicalState",
    "HybridState",
]

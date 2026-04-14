"""
Repo Doctor Logic Layer.

Formal verification using:
- SMT solving with Z3
- Invariant checking
- Repository Hamiltonian operations
"""

from ..invariants import Invariant, InvariantResult, ParseInvariant
from .hamiltonian import RepositoryHamiltonian, compute_energy
from .smt_model import SMTModel, prove_invariant

__all__ = [
    "Invariant",
    "InvariantResult",
    "ParseInvariant",
    "SMTModel",
    "prove_invariant",
    "RepositoryHamiltonian",
    "compute_energy",
]

"""
Repo Doctor Omega - Mathematical Control Model

Quantum-formal state modeling for repository verification:
- State vector |Ψ_repo⟩ with 11 dimensions
- Hamiltonian H_repo with subsystem operators
- Observables for structured measurements
- Hard invariant system I = {I_parse, I_import, ..., I_security}
"""

from .contracts import ContractCommutator, PublicRuntimeDrift
from .entanglement import EntanglementAnalyzer, EntanglementMatrix
from .hamiltonian import EnergyGradient, RepositoryHamiltonian
from .invariants import InvariantChecker, InvariantPack
from .observables import ObservableSet, ObservationResult
from .spectral import GraphLaplacian, SpectralAnalyzer
from .state_vector import RepoStateVector, StateDimension, StateVectorBuilder
from .status_truth import StatusTruthChecker

__all__ = [
    "RepoStateVector",
    "StateDimension",
    "StateVectorBuilder",
    "ObservableSet",
    "ObservationResult",
    "RepositoryHamiltonian",
    "EnergyGradient",
    "InvariantPack",
    "InvariantChecker",
    "ContractCommutator",
    "PublicRuntimeDrift",
    "EntanglementMatrix",
    "EntanglementAnalyzer",
    "SpectralAnalyzer",
    "GraphLaplacian",
    "StatusTruthChecker",
]

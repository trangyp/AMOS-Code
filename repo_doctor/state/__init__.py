"""
Repo Doctor Ω∞ - State Module

Repository state as quantum-inspired density matrix:
- Pure states |Ψ_repo⟩ for fully observable repos
- Mixed states ρ_repo for uncertain/partial knowledge
- Lindblad noise operators for environment interactions
- Gauge symmetry for semantic equivalence
"""

from .amplitudes import AmplitudeCalculator, StateAmplitude
from .basis import StateBasis, StateDimension
from .density import DensityMatrix, MixedState
from .gauge import GaugeSymmetry, GaugeTransform
from .hamiltonian import EnergyOperator, RepositoryHamiltonian
from .observables import MeasurementResult, ObservableSet

__all__ = [
    "StateBasis",
    "StateDimension",
    "StateAmplitude",
    "AmplitudeCalculator",
    "DensityMatrix",
    "MixedState",
    "RepositoryHamiltonian",
    "EnergyOperator",
    "ObservableSet",
    "MeasurementResult",
    "GaugeSymmetry",
    "GaugeTransform",
]

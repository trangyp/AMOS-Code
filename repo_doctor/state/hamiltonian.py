"""
Repo Doctor Ω∞ - Repository Hamiltonian

H_repo = Σk λk Hk

Each Hk measures degradation in subsystem k.
Energy: E_repo = Tr(ρ · H) = Σk λk (1 - αk)²

Severity weights:
λS=100 (syntax), λI=90 (imports), λA=95 (API), λSec=100 (security)
λE=90 (entrypoints), λPk=90 (packaging), λRt=80 (runtime)
λPs=70 (persistence), λSt=65 (status), λD=35 (docs), λH=55 (history)
"""

from dataclasses import dataclass
from typing import Any

from .basis import StateBasis, StateDimension


@dataclass
class EnergyGradient:
    """Gradient of energy with respect to state changes."""

    partials: dict[StateDimension, float]

    def steepest_descent(self) -> StateDimension:
        """Find dimension with highest energy contribution."""
        return max(self.partials.items(), key=lambda x: x[1])[0]


class EnergyOperator:
    """Single subsystem energy operator Hk."""

    def __init__(self, dimension: StateDimension, severity_weight: float):
        self.dimension = dimension
        self.weight = severity_weight

    def apply(self, amplitude: float) -> float:
        """
        Apply operator: Hk = λk (1 - αk)²
        """
        return self.weight * (1 - amplitude) ** 2

    def gradient(self, amplitude: float) -> float:
        """
        Compute gradient: dHk/dαk = -2λk(1 - αk)
        """
        return -2 * self.weight * (1 - amplitude)


class RepositoryHamiltonian:
    """
    Full repository Hamiltonian.
    H_repo = Σk λk Hk
    """

    def __init__(self, custom_weights: dict[StateDimension, float] = None):
        self.weights = custom_weights or {dim: StateBasis.get_weight(dim) for dim in StateDimension}
        self.operators = {dim: EnergyOperator(dim, self.weights[dim]) for dim in StateDimension}

    def total_energy(self, amplitudes: dict[StateDimension, float]) -> float:
        """
        Compute total energy: E = Σk λk (1 - αk)²
        """
        total = 0.0
        for dim, amp in amplitudes.items():
            op = self.operators.get(dim)
            if op:
                total += op.apply(amp)
        return total

    def subsystem_energy(self, dimension: StateDimension, amplitude: float) -> float:
        """Energy for single subsystem."""
        return self.operators[dimension].apply(amplitude)

    def gradient(self, amplitudes: dict[StateDimension, float]) -> EnergyGradient:
        """
        Compute energy gradient for optimization.
        ∂E/∂αk = -2λk(1 - αk)
        """
        partials = {}
        for dim, amp in amplitudes.items():
            op = self.operators.get(dim)
            if op:
                partials[dim] = abs(op.gradient(amp))
        return EnergyGradient(partials)

    def is_stable(self, amplitudes: dict[StateDimension, float], threshold: float = 200.0) -> bool:
        """Check if repository is stable (energy below threshold)."""
        return self.total_energy(amplitudes) < threshold

    def critical_dimensions(self, amplitudes: dict[StateDimension, float]) -> List[StateDimension]:
        """Find dimensions contributing most to energy."""
        energies = [(dim, self.subsystem_energy(dim, amp)) for dim, amp in amplitudes.items()]
        sorted_dims = sorted(energies, key=lambda x: -x[1])
        return [dim for dim, _ in sorted_dims if _ > 10.0]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Hamiltonian configuration."""
        return {
            "weights": {dim.value: w for dim, w in self.weights.items()},
            "threshold": 200.0,
        }

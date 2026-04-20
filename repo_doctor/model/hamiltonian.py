"""
Repo Doctor Omega - Repository Hamiltonian

H_repo = λS Hsyntax + λI Himports + λT Htypes + λA Hapi +
       λE Hentry + λP Hpack + λR Hruntime + λD Hdocs +
       λM Hpersistence + λH Hhistory + λSec Hsecurity

Each Hk measures "energy" in that subsystem.
Low energy = healthy, high energy = degraded.
"""

from dataclasses import dataclass
from typing import Any, Dict

from .state_vector import DEFAULT_WEIGHTS, StateDimension


@dataclass
class EnergyGradient:
    """Gradient of energy with respect to state changes."""

    partials: dict[StateDimension, float]

    def steepest_descent(self) -> StateDimension:
        """Find dimension with highest energy contribution."""
        return max(self.partials.items(), key=lambda x: x[1])[0]

    def improvement_potential(self) -> dict[StateDimension, float]:
        """Calculate potential energy reduction per dimension."""
        return {dim: weight for dim, weight in self.partials.items()}


class RepositoryHamiltonian:
    """
    Repository Hamiltonian operator.

    H_repo = Σ λk Hk where each Hk = (1 - Ψk)^2

    This measures total repository degradation energy.
    """

    def __init__(self, weights: dict[StateDimension, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def apply(self, state_vector) -> float:
        """
        Apply Hamiltonian to state: Union[H, Ψ]> = E

        Returns: Total energy E_repo = Σ λk (1 - αk)^2
        """
        from .state_vector import StateDimension

        energy = 0.0
        for dim in StateDimension:
            alpha = state_vector.get(dim)
            weight = self.weights.get(dim, 1.0)
            energy += weight * (1 - alpha) ** 2
        return energy

    def apply_dimension(self, dimension: StateDimension, alpha: float) -> float:
        """Apply single dimension operator: Hk = (1 - αk)^2"""
        weight = self.weights.get(dimension, 1.0)
        return weight * (1 - alpha) ** 2

    def gradient(self, state_vector) -> EnergyGradient:
        """
        Compute energy gradient: ∂E/∂Ψk = -2λk(1 - Ψk)

        Shows which dimensions contribute most to energy.
        """
        from .state_vector import StateDimension

        partials = {}
        for dim in StateDimension:
            alpha = state_vector.get(dim)
            weight = self.weights.get(dim, 1.0)
            partial = 2 * weight * (1 - alpha)
            partials[dim] = partial

        return EnergyGradient(partials)

    def eigenvalue_analysis(self, state_vector) -> Dict[str, Any]:
        """
        Analyze eigenvalue decomposition of repository state.

        Returns stable vs unstable subsystems.
        """
        from .state_vector import StateDimension

        energies = {}
        total = 0.0

        for dim in StateDimension:
            alpha = state_vector.get(dim)
            weight = self.weights.get(dim, 1.0)
            energy = weight * (1 - alpha) ** 2
            energies[dim] = energy
            total += energy

        sorted_dims = sorted(energies.items(), key=lambda x: -x[1])

        return {
            "total_energy": total,
            "by_dimension": {
                dim.value: {
                    "energy": energy,
                    "percentage": (energy / total * 100) if total > 0 else 0,
                }
                for dim, energy in sorted_dims
            },
            "critical_dimensions": [dim.value for dim, energy in sorted_dims[:3] if energy > 0.5],
            "stable_dimensions": [dim.value for dim, energy in sorted_dims[-3:] if energy < 0.1],
        }

    def thermal_properties(self, state_vector) -> dict[str, float]:
        """
        Calculate thermal properties (analogous to statistical mechanics).

        - Temperature: mean deviation from ideal
        - Entropy: disorder measure
        - Free energy: available for doing work (fixes)
        """
        import math

        from .state_vector import StateDimension

        deviations = [(1 - state_vector.get(dim)) for dim in StateDimension]

        # Temperature: mean deviation
        temperature = sum(deviations) / len(deviations)

        # Entropy: Shannon-like disorder measure
        entropy = 0.0
        total_dev = sum(deviations)
        if total_dev > 0:
            for d in deviations:
                if d > 0:
                    p = d / total_dev
                    entropy -= p * math.log(p)

        # Free energy: E - T·S
        free_energy = self.apply(state_vector) - temperature * entropy

        return {
            "temperature": temperature,
            "entropy": entropy,
            "free_energy": free_energy,
            "heat_capacity": len([d for d in deviations if d > 0.5]),
        }

    def perturbation_energy(self, state_vector, delta_state: dict[StateDimension, float]) -> float:
        """
        Calculate energy change from perturbation: ΔE = E(Ψ') - E(Ψ)

        Used to predict impact of proposed changes.
        """
        # Create perturbed state
        from copy import deepcopy

        from .state_vector import RepoStateVector

        perturbed_amps = deepcopy(state_vector.amplitudes)
        for dim, delta in delta_state.items():
            current = perturbed_amps.get(dim, 1.0)
            perturbed_amps[dim] = max(0.0, min(1.0, current + delta))

        perturbed = RepoStateVector(
            amplitudes=perturbed_amps,
            weights=state_vector.weights,
        )

        return self.apply(perturbed) - self.apply(state_vector)

    def is_stable(self, state_vector, threshold: float = 2.0) -> bool:
        """Check if repository is stable (energy below threshold)."""
        return self.apply(state_vector) < threshold

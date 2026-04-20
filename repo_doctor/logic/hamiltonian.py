"""
Repository Hamiltonian

Implements the formal energy calculation for repository state:
    H_repo = Σ λ_k · (1 - Ψ_k)^2

Where:
    - λ_k: Weight for dimension k
    - Ψ_k: State value for dimension k (normalized to [0, 1])
    - E_repo = <Ψ|H|Ψ>: Scalar degradation energy

Healthy repo: E_repo ≈ 0 (all Ψ_k ≈ 1)
Broken repo: E_repo >> 0 (some Ψ_k << 1)
"""

from dataclasses import dataclass
from typing import Any

from ..state_vector import DEFAULT_WEIGHTS, RepoStateVector, StateDimension


@dataclass
class EnergyGradient:
    """Gradient of energy with respect to state changes."""

    partials: dict[StateDimension, float]

    def steepest_descent(self) -> StateDimension:
        """Find dimension with highest energy contribution."""
        return max(self.partials.items(), key=lambda x: x[1])[0]

    def improvement_potential(self) -> dict[StateDimension, float]:
        """Calculate potential energy reduction per dimension."""
        return {
            dim: 2 * weight * (1 - value)
            for dim, weight in self.partials.items()
            for value in [0]  # If we fix this dimension to 1.0
        }


class RepositoryHamiltonian:
    """
    Repository Hamiltonian operator.

    H_repo = λ_s H_syntax + λ_i H_import + λ_t H_type + λ_a H_api
           + λ_e H_entry + λ_p H_pack + λ_r H_runtime + λ_d H_docs
           + λ_h H_history + λ_σ H_security

    Each H_k = (1 - Ψ_k)^2 for the respective dimension.
    """

    def __init__(self, weights: dict[StateDimension, float] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def apply(self, state: RepoStateVector) -> float:
        """
        Apply Hamiltonian to state vector: Union[H, Ψ]> = E

        Args:
        ----
            state: Repository state vector

        Returns:
        -------
            Energy E_repo = Σ λ_k · (1 - Ψ_k)^2

        """
        energy = 0.0

        for dim in StateDimension:
            alpha_k = state.get(dim)  # Ψ_k - state value
            lambda_k = self.weights.get(dim, 1.0)

            # Hamiltonian term: λ_k · (1 - Ψ_k)^2
            term = lambda_k * (1 - alpha_k) ** 2
            energy += term

        return energy

    def gradient(self, state: RepoStateVector) -> EnergyGradient:
        """
        Compute energy gradient: ∂E/∂Ψ_k = -2λ_k(1 - Ψ_k)

        This shows which dimensions contribute most to energy.
        """
        partials = {}

        for dim in StateDimension:
            alpha_k = state.get(dim)
            lambda_k = self.weights.get(dim, 1.0)

            # Partial derivative
            partial = 2 * lambda_k * (1 - alpha_k)
            partials[dim] = partial

        return EnergyGradient(partials)

    def eigenvalue_approximation(self, state: RepoStateVector) -> Dict[str, Any]:
        """
        Approximate eigenvalue analysis of repository state.

        Returns decomposition showing which subsystems are:
        - Stable (low energy contribution)
        - Unstable (high energy contribution)
        - Critical (approaching threshold)
        """
        energy_by_dim = {}
        total = 0.0

        for dim in StateDimension:
            alpha_k = state.get(dim)
            lambda_k = self.weights.get(dim, 1.0)
            term = lambda_k * (1 - alpha_k) ** 2
            energy_by_dim[dim] = term
            total += term

        # Sort by energy contribution
        sorted_dims = sorted(energy_by_dim.items(), key=lambda x: -x[1])

        return {
            "total_energy": total,
            "by_dimension": {
                dim.value: {"energy": energy, "percentage": energy / total * 100}
                for dim, energy in sorted_dims
                if total > 0
            },
            "critical_dimensions": [dim.value for dim, energy in sorted_dims[:3] if energy > 0.5],
            "stable_dimensions": [dim.value for dim, energy in sorted_dims[-3:] if energy < 0.1],
        }

    def thermal_properties(self, state: RepoStateVector) -> dict[str, float]:
        """
        Calculate "thermal" properties of repository.

        Analogous to statistical mechanics:
        - Temperature: average deviation from ideal
        - Entropy: disorder measure
        - Free energy: available for doing work (fixes)
        """
        deviations = [(1 - state.get(dim)) for dim in StateDimension]

        # Temperature: mean deviation
        temperature = sum(deviations) / len(deviations)

        # Entropy: measure of disorder (Shannon-like)
        import math

        entropy = 0.0
        for d in deviations:
            if d > 0:
                p = d / sum(deviations) if sum(deviations) > 0 else 0
                if p > 0:
                    entropy -= p * math.log(p)

        # Free energy: E - T·S
        free_energy = self.apply(state) - temperature * entropy

        return {
            "temperature": temperature,
            "entropy": entropy,
            "free_energy": free_energy,
            "heat_capacity": len([d for d in deviations if d > 0.5]),
        }

    def perturbation(
        self, state: RepoStateVector, delta_state: dict[StateDimension, float]
    ) -> float:
        """
        Calculate energy change from perturbation: ΔE = <Ψ'|H|Ψ'> - <Ψ|H|Ψ>

        Used to predict impact of proposed changes.
        """
        # Create perturbed state
        from copy import deepcopy

        perturbed_values = deepcopy(state.values)
        for dim, delta in delta_state.items():
            perturbed_values[dim] = max(0.0, min(1.0, perturbed_values.get(dim, 1.0) + delta))

        perturbed_state = RepoStateVector(
            values=perturbed_values,
            weights=state.weights,
        )

        return self.apply(perturbed_state) - self.apply(state)

    def commutator(self, state_a: RepoStateVector, state_b: RepoStateVector) -> float:
        """
        Calculate commutator [A, B] = AB - BA for two states.

        Non-zero commutator indicates non-commuting changes.
        """
        # [H, Δ] = H(Ψ_A) - H(Ψ_B) when operations don't commute
        return abs(self.apply(state_a) - self.apply(state_b))


def compute_energy(state: RepoStateVector) -> float:
    """Convenience function: compute repository energy."""
    hamiltonian = RepositoryHamiltonian()
    return hamiltonian.apply(state)


def compute_thermal_properties(state: RepoStateVector) -> dict[str, float]:
    """Convenience function: compute thermal properties."""
    hamiltonian = RepositoryHamiltonian()
    return hamiltonian.thermal_properties(state)

"""
Repo Doctor Ω∞ - Density Matrix

Mixed state representation for uncertain repository knowledge:
ρ_repo = Σi pi |Ψ_i⟩⟨Ψ_i|

Handles:
- Partial observability
- Environment-conditioned behavior
- Competing failure hypotheses
- Nondeterministic test outcomes
"""

import math
from dataclasses import dataclass, field
from typing import Any

from .basis import StateBasis, StateDimension


@dataclass
class PureState:
    """A pure repository state |Ψ⟩ with amplitudes."""

    amplitudes: dict[StateDimension, float]
    label: str = ""
    probability: float = 1.0

    def __post_init__(self):
        """Ensure amplitudes are in [0,1]."""
        self.amplitudes = {dim: max(0.0, min(1.0, amp)) for dim, amp in self.amplitudes.items()}

    def expectation(self, operator: dict[StateDimension, float]) -> float:
        """Compute ⟨Ψ|O|Ψ⟩ for diagonal operator O."""
        total = 0.0
        for dim, amp in self.amplitudes.items():
            weight = operator.get(dim, 1.0)
            total += weight * amp
        return total


@dataclass
class MixedState:
    """
    Mixed state density matrix.
    ρ = Σi pi |Ψ_i⟩⟨Ψ_i|
    """

    components: List[PureState] = field(default_factory=list)

    def add_component(self, state: PureState) -> None:
        """Add a pure state component."""
        self.components.append(state)
        self._normalize()

    def _normalize(self) -> None:
        """Normalize probabilities to sum to 1."""
        total = sum(c.probability for c in self.components)
        if total > 0:
            for c in self.components:
                c.probability /= total

    def expectation_value(self, dim: StateDimension) -> float:
        """
        Compute expected amplitude: ⟨αk⟩ = Tr(ρ · Ak)
        """
        total = 0.0
        for comp in self.components:
            amp = comp.amplitudes.get(dim, 0.0)
            total += comp.probability * amp
        return total

    def expected_energy(self, weights: dict[StateDimension, float] = None) -> float:
        """
        Compute expected energy: E = Tr(ρ · H)
        E = Σk λk (1 - ⟨αk⟩)²
        """
        if weights is None:
            weights = {dim: StateBasis.get_weight(dim) for dim in StateDimension}

        energy = 0.0
        for dim in StateDimension:
            expected_amp = self.expectation_value(dim)
            weight = weights.get(dim, 1.0)
            energy += weight * (1 - expected_amp) ** 2

        return energy

    def von_neumann_entropy(self) -> float:
        """
        Compute von Neumann entropy: S = -Tr(ρ log ρ)
        Approximation using component probabilities.
        """
        entropy = 0.0
        for comp in self.components:
            p = comp.probability
            if p > 0:
                entropy -= p * math.log(p)
        return entropy

    def coherence(self) -> float:
        """
        Measure quantum coherence / purity.
        Tr(ρ²) = 1 for pure state, < 1 for mixed state.
        """
        # Simplified: 1 - entropy estimate
        return 1.0 - min(1.0, self.von_neumann_entropy() / math.log(len(self.components) + 1))

    def collapse_dimension(self, dim: StateDimension, measured_value: float) -> None:
        """
        Collapse state after measurement of one dimension.
        Update components based on measurement result.
        """
        for comp in self.components:
            # Update amplitude toward measured value
            current = comp.amplitudes.get(dim, 0.5)
            comp.amplitudes[dim] = 0.7 * measured_value + 0.3 * current

        # Re-normalize based on likelihood
        for comp in self.components:
            measured_amp = comp.amplitudes.get(dim, 0.5)
            # Higher probability if component matches measurement
            comp.probability *= 1 - abs(measured_amp - measured_value)

        self._normalize()


class DensityMatrix:
    """
    Full density matrix operator for repository state.
    Handles mixed states, uncertainty, and open system dynamics.
    """

    def __init__(self, repo_path: str = ""):
        self.repo_path = repo_path
        self.state = MixedState()
        self.lindblad_operators: list[dict[str, Any]] = []

    def initialize_pure(self, amplitudes: dict[StateDimension, float]) -> None:
        """Initialize as pure state."""
        self.state = MixedState(components=[PureState(amplitudes=amplitudes, probability=1.0)])

    def add_uncertainty(self, dim: StateDimension, variance: float) -> None:
        """
        Add uncertainty to a dimension by creating mixed state.
        """
        current = self.state.expectation_value(dim)

        # Create two components representing uncertainty bounds
        comp1 = PureState(
            amplitudes={d: self.state.expectation_value(d) for d in StateDimension},
            probability=0.5,
            label="upper_bound",
        )
        comp1.amplitudes[dim] = min(1.0, current + variance)

        comp2 = PureState(
            amplitudes={d: self.state.expectation_value(d) for d in StateDimension},
            probability=0.5,
            label="lower_bound",
        )
        comp2.amplitudes[dim] = max(0.0, current - variance)

        self.state = MixedState(components=[comp1, comp2])

    def apply_lindblad_noise(self, noise_type: str, strength: float) -> None:
        """
        Apply Lindblad noise operator.
        Models environment interactions like:
        - Python version mismatch
        - OS-specific behavior
        - Missing dependencies
        - CI-only branches
        """
        noise_operators = {
            "pyver": {StateDimension.RUNTIME: 0.8, StateDimension.PACKAGING: 0.9},
            "os": {StateDimension.RUNTIME: 0.9, StateDimension.ENTRYPOINTS: 0.95},
            "native": {StateDimension.PACKAGING: 0.7, StateDimension.RUNTIME: 0.8},
            "ci": {StateDimension.TESTS: 0.9, StateDimension.HISTORY: 0.95},
            "net": {StateDimension.RUNTIME: 0.85, StateDimension.PERSISTENCE: 0.9},
            "secret": {StateDimension.SECURITY: 0.7, StateDimension.STATUS: 0.95},
        }

        affected = noise_operators.get(noise_type, {})

        for comp in self.state.components:
            for dim, factor in affected.items():
                current = comp.amplitudes.get(dim, 1.0)
                # Noise reduces amplitude
                comp.amplitudes[dim] = current * (1 - strength * (1 - factor))

        self.lindblad_operators.append({"type": noise_type, "strength": strength})

    def evolve(self, hamiltonian: dict[StateDimension, float], dt: float = 1.0) -> None:
        """
        Time evolution: dρ/dt = -i[H, ρ] + Lindblad terms
        Simplified: deterministic evolution of expected values.
        """
        # For each component, evolve amplitudes toward Hamiltonian ground state
        for comp in self.state.components:
            for dim in StateDimension:
                target = 1.0  # Ground state is all 1s
                current = comp.amplitudes.get(dim, 0.5)
                rate = hamiltonian.get(dim, 1.0) / 100.0

                # Evolution toward target
                comp.amplitudes[dim] = current + rate * (target - current) * dt

    def to_dict(self) -> Dict[str, Any]:
        """Serialize density matrix."""
        return {
            "repo_path": self.repo_path,
            "expected_amplitudes": {
                dim.value: self.state.expectation_value(dim) for dim in StateDimension
            },
            "expected_energy": self.state.expected_energy(),
            "entropy": self.state.von_neumann_entropy(),
            "coherence": self.state.coherence(),
            "components": len(self.state.components),
            "noise_operators": self.lindblad_operators,
        }

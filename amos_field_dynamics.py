"""
AMOS Field Dynamics Engine
Lagrangian Field Theory for AMOSL v4.0.0

Implements the Field lens of the 5-lens mathematical regime:
- Lagrangian density L(φ, ∂φ, x)
- Action functional S[φ] = ∫ L d⁴x
- Field equations via variational principle
- Hamiltonian formulation
- Noether currents and conservation laws
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

import numpy as np


@dataclass
class FieldConfig:
    """Configuration for field dynamics."""

    dim: int = 4  # spacetime dimensions
    dx: float = 0.01  # spatial discretization
    dt: float = 0.001  # temporal discretization
    coupling: float = 1.0  # interaction strength
    mass: float = 1.0  # field mass parameter


@dataclass
class FieldState:
    """
    Quantum field configuration state.

    Represents φ(x) - the field value at each spacetime point.
    """

    values: np.ndarray
    momenta: np.ndarray = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.momenta is None:
            self.momenta = np.zeros_like(self.values)


class Lagrangian(Protocol):
    """Protocol for Lagrangian density functions."""

    def evaluate(self, phi: np.ndarray, dphi: np.ndarray) -> float:
        """Evaluate L(φ, ∂φ) at a point."""
        ...

    def derivative(self, phi: np.ndarray, dphi: np.ndarray) -> np.ndarray:
        """Compute ∂L/∂(∂φ) - canonical momentum density."""
        ...


@dataclass
class ScalarLagrangian:
    """
    Scalar field Lagrangian: L = ½(∂φ)² - V(φ)

    Klein-Gordon field with potential V(φ) = ½m²φ² + λφ⁴/4!
    """

    mass: float = 1.0
    coupling: float = 0.1  # λ for φ⁴ theory

    def evaluate(self, phi: np.ndarray, dphi: np.ndarray) -> float:
        """L = ½(∂φ)² - ½m²φ² - λφ⁴/4!"""
        kinetic = 0.5 * np.sum(dphi**2)
        potential = 0.5 * self.mass**2 * np.sum(phi**2)
        interaction = self.coupling * np.sum(phi**4) / 24
        return kinetic - potential - interaction

    def derivative(self, phi: np.ndarray, dphi: np.ndarray) -> np.ndarray:
        """∂L/∂(∂φ) = ∂φ (canonical momentum)"""
        return dphi

    def eom_rhs(self, phi: np.ndarray, pi: np.ndarray) -> np.ndarray:
        """
        Right-hand side of equations of motion.
        ∂²φ = -∂V/∂φ = -m²φ - λφ³/6
        """
        return -(self.mass**2 * phi + self.coupling * phi**3 / 6)


@dataclass
class GaugeLagrangian:
    """
    U(1) Gauge field Lagrangian: L = -¼FμνF^μν

    Electromagnetic field strength tensor.
    """

    charge: float = 1.0

    def field_strength(self, A: np.ndarray) -> np.ndarray:
        """Fμν = ∂μAν - ∂νAμ"""
        # Simplified: return 4D field strength tensor
        F = np.zeros((4, 4) + A.shape[1:])
        for mu in range(4):
            for nu in range(4):
                if mu != nu:
                    dmu_Anu = np.gradient(A[nu], axis=mu)
                    dnu_Amu = np.gradient(A[mu], axis=nu)
                    F[mu, nu] = dmu_Anu - dnu_Amu
        return F

    def evaluate(self, A: np.ndarray, dA: np.ndarray = None) -> float:
        """L = -¼FμνF^μν"""
        F = self.field_strength(A)
        # Contract indices: FμνF^μν = Σ Fμν² (with metric)
        return -0.25 * np.sum(F**2)


class FieldDynamics:
    """
    Field Dynamics Engine for AMOS.

    Evolves quantum fields via Lagrangian dynamics.
    Provides the field-theoretic foundation for AMOSL.
    """

    def __init__(self, lagrangian: Lagrangian, config: Optional[FieldConfig] = None) -> None:
        self.lagrangian = lagrangian
        self.config = config or FieldConfig()
        self.history: List[FieldState] = []
        self._action_history: List[float] = []
        self._conserved_quantities: dict[str, list[float]] = defaultdict(list)
        self._initialized_at = datetime.now(timezone.utc).isoformat()

    def initialize_field(self, shape: tuple[int, ...], initializer: str = "vacuum") -> FieldState:
        """Initialize field configuration."""
        if initializer == "vacuum":
            values = np.zeros(shape)
        elif initializer == "random":
            values = np.random.randn(*shape) * 0.1
        elif initializer == "soliton":
            # 1D soliton profile: φ(x) = tanh(x/√2)
            x = np.linspace(-5, 5, shape[0])
            values = np.tanh(x / np.sqrt(2))
            if len(shape) > 1:
                values = np.tile(values.reshape(-1, 1), (1, shape[1]))
        else:
            values = np.zeros(shape)

        state = FieldState(values=values)
        self.history.append(state)
        return state

    def compute_action(self, state: FieldState) -> float:
        """Compute action S[φ] = ∫ L d⁴x."""
        phi = state.values
        # Compute gradients (∂φ)
        dphi = np.gradient(phi)
        if isinstance(dphi, list):
            dphi = np.stack(dphi)

        lagrangian_density = self.lagrangian.evaluate(phi, dphi)
        # Discretized integral: Σ L ΔV
        dvol = self.config.dx ** (phi.ndim)
        action = lagrangian_density * dvol

        self._action_history.append(action)
        return action

    def compute_hamiltonian(self, state: FieldState) -> float:
        """
        Compute Hamiltonian H = ∫ (π∂φ - L) d³x.
        Energy density of the field configuration.
        """
        phi = state.values
        pi = state.momenta if state.momenta is not None else np.zeros_like(phi)

        # H = ∫ (½π² + ½(∇φ)² + V(φ)) d³x
        kinetic = 0.5 * np.sum(pi**2)
        gradient = np.gradient(phi)
        if isinstance(gradient, list):
            gradient_energy = 0.5 * sum(np.sum(g**2) for g in gradient)
        else:
            gradient_energy = 0.5 * np.sum(gradient**2)

        # Potential from Lagrangian
        if isinstance(self.lagrangian, ScalarLagrangian):
            potential = 0.5 * self.lagrangian.mass**2 * np.sum(phi**2)
            potential += self.lagrangian.coupling * np.sum(phi**4) / 24
        else:
            potential = 0.0

        dvol = self.config.dx ** (phi.ndim)
        return (kinetic + gradient_energy + potential) * dvol

    def step(self, state: Optional[FieldState] = None) -> FieldState:
        """
        Evolve field by one timestep using symplectic integration.

        Uses leapfrog/Verlet integrator for Hamiltonian dynamics:
        φ(t+dt) = φ(t) + dt·π(t) + ½dt²·∂²φ
        π(t+dt) = π(t) + dt·∂²φ(t+dt/2)
        """
        if state is None:
            state = self.history[-1] if self.history else self.initialize_field((64,))

        phi = state.values.copy()
        pi = state.momenta.copy() if state.momenta is not None else np.zeros_like(phi)
        dt = self.config.dt

        # Compute Laplacian ∂²φ
        if isinstance(self.lagrangian, ScalarLagrangian):
            # ∂²φ = -m²φ - λφ³/6 (from equations of motion)
            acceleration = self.lagrangian.eom_rhs(phi, pi)
        else:
            # General: numerical Laplacian
            acceleration = np.zeros_like(phi)
            for axis in range(phi.ndim):
                acceleration += np.gradient(np.gradient(phi, axis=axis), axis=axis)

        # Leapfrog integration (symplectic, energy-conserving)
        # Half-step momentum
        pi_half = pi + 0.5 * dt * acceleration
        # Full-step position
        phi_new = phi + dt * pi_half
        # Compute new acceleration
        if isinstance(self.lagrangian, ScalarLagrangian):
            acc_new = self.lagrangian.eom_rhs(phi_new, pi_half)
        else:
            acc_new = np.zeros_like(phi_new)
            for axis in range(phi_new.ndim):
                acc_new += np.gradient(np.gradient(phi_new, axis=axis), axis=axis)
        # Full-step momentum
        pi_new = pi_half + 0.5 * dt * acc_new

        new_state = FieldState(
            values=phi_new,
            momenta=pi_new,
            metadata={"parent_id": id(state), "step": len(self.history)},
        )

        self.history.append(new_state)

        # Track conserved quantities
        H = self.compute_hamiltonian(new_state)
        self._conserved_quantities["energy"].append(H)

        return new_state

    def evolve(self, n_steps: int, initial_state: Optional[FieldState] = None) -> List[FieldState]:
        """Evolve field for n timesteps."""
        states = []
        state = initial_state or (
            self.history[-1] if self.history else self.initialize_field((64,))
        )

        for _ in range(n_steps):
            state = self.step(state)
            states.append(state)

        return states

    def get_noether_charge(self, symmetry: str) -> float:
        """
        Compute Noether charge for a given symmetry.

        Symmetries:
        - "phase": U(1) phase rotation → particle number
        - "translation": spatial translation → momentum
        """
        if not self.history:
            return 0.0

        state = self.history[-1]
        phi = state.values

        if symmetry == "phase":
            # Q = Im(∫ φ* π d³x) for complex fields
            # For real fields, use alternative: ρ = φ²
            if np.iscomplexobj(phi):
                pi = state.momenta if state.momenta is not None else np.zeros_like(phi)
                charge = np.imag(np.sum(np.conj(phi) * pi))
            else:
                # Particle number density: ρ = φ² for real scalar
                charge = np.sum(phi**2)
        elif symmetry == "translation":
            # P = -∫ π ∇φ d³x
            if state.momenta is not None:
                grad_phi = np.gradient(phi)
                if isinstance(grad_phi, list):
                    grad_phi = grad_phi[0]  # Take first spatial component
                charge = -np.sum(state.momenta * grad_phi)
            else:
                charge = 0.0
        else:
            charge = 0.0

        return charge * (self.config.dx**phi.ndim)

    def get_metrics(self) -> Dict[str, Any]:
        """Get field dynamics metrics."""
        return {
            "history_length": len(self.history),
            "last_action": self._action_history[-1] if self._action_history else 0.0,
            "energy_drift": self._compute_energy_drift(),
            "noether_charges": {
                "particle_number": self.get_noether_charge("phase"),
                "momentum": self.get_noether_charge("translation"),
            },
            "initialized_at": self._initialized_at,
            "last_evolution": self.history[-1].timestamp if self.history else None,
        }

    def _compute_energy_drift(self) -> float:
        """Compute relative energy conservation violation."""
        if len(self._conserved_quantities["energy"]) < 2:
            return 0.0

        energies = self._conserved_quantities["energy"]
        if len(energies) == 0 or energies[0] == 0:
            return 0.0

        max_deviation = max(abs(e - energies[0]) for e in energies)
        return max_deviation / abs(energies[0])


def create_scalar_field(
    mass: float = 1.0, coupling: float = 0.1, grid_size: int = 64
) -> FieldDynamics:
    """Factory for scalar field dynamics."""
    lagrangian = ScalarLagrangian(mass=mass, coupling=coupling)
    config = FieldConfig(dx=0.1, dt=0.01, mass=mass, coupling=coupling)
    return FieldDynamics(lagrangian, config)


def create_gauge_field(charge: float = 1.0) -> FieldDynamics:
    """Factory for U(1) gauge field dynamics."""
    lagrangian = GaugeLagrangian(charge=charge)
    config = FieldConfig(dx=0.1, dt=0.01)
    return FieldDynamics(lagrangian, config)


if __name__ == "__main__":
    # Demonstrate field dynamics
    print("=== AMOS Field Dynamics Engine Demo ===\n")

    # Create scalar φ⁴ field
    dynamics = create_scalar_field(mass=1.0, coupling=0.1, grid_size=64)

    # Initialize soliton
    initial = dynamics.initialize_field((64,), initializer="soliton")
    print(f"Initial energy: {dynamics.compute_hamiltonian(initial):.4f}")
    print(f"Initial action: {dynamics.compute_action(initial):.4f}")

    # Evolve
    print("\nEvolving field...")
    states = dynamics.evolve(100)

    # Report
    metrics = dynamics.get_metrics()
    print(f"\nFinal energy: {dynamics.compute_hamiltonian(states[-1]):.4f}")
    print(f"Energy drift: {metrics['energy_drift']:.2e}")
    print(f"Noether charges: {metrics['noether_charges']}")
    print("\n✅ Field dynamics operational")

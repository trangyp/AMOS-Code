"""AMOSL Runtime Kernel - Core execution engine.

Implements the state manifold Σ and evolution operator Φ from the formal spec:

State Manifold:
    Σ = Σ_c × Σ_q × Σ_b × Σ_h × Σ_e × Σ_t

Evolution Rule:
    Σ_{t+1} = Φ(Σ_t, a_t, o_t, e_t, θ_t) subject to Λ(Σ_{t+1}) = ⊤
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional


class Substrate(Enum):
    """Substrate types for the state manifold."""

    CLASSICAL = auto()
    QUANTUM = auto()
    BIOLOGICAL = auto()
    HYBRID = auto()
    ENVIRONMENT = auto()
    TIME = auto()


@dataclass
class ClassicalState:
    """Σ_c = ⟨X_c, μ_c, π_c, η_c⟩

    Classical state components:
    - X_c: values/entities
    - μ_c: mutable store
    - π_c: policies
    - η_c: events/logical control state
    """

    values: dict[str, Any] = field(default_factory=dict)
    store: dict[str, Any] = field(default_factory=dict)
    policies: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)

    def get(self, key: str, default=None):
        return self.values.get(key, self.store.get(key, default))

    def set(self, key: str, value: Any):
        self.store[key] = value
        self.values[key] = value

    def emit_event(self, event: str):
        self.events.append(event)


@dataclass
class QuantumState:
    """Σ_q = ⟨ℋ, ρ, 𝕆, 𝕌⟩

    Quantum state components:
    - ℋ: Hilbert space
    - ρ: density operator
    - 𝕆: observable set
    - 𝕌: admissible operator set
    """

    hilbert_dim: int = 2
    density_matrix: Optional[list[list[complex]]] = None
    observables: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)
    registers: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.density_matrix is None:
            # Initialize to |0⟩⟨0|
            n = self.hilbert_dim
            self.density_matrix = [
                [1.0 if i == j == 0 else 0.0 for j in range(n)] for i in range(n)
            ]

    def add_register(self, name: str, qubits: int):
        self.registers[name] = qubits

    def apply_gate(self, gate: str, targets: list[int]):
        self.operators.append(f"{gate}({targets})")


@dataclass
class BiologicalState:
    """Σ_b = ⟨G, R, P, C, N, Env_b⟩

    Biological state components:
    - G: genomic state
    - R: transcriptomic/regulatory state
    - P: proteomic/functional state
    - C: concentrations
    - N: population/network state
    - Env_b: biological environment
    """

    genome: dict[str, str] = field(default_factory=dict)
    transcriptome: dict[str, float] = field(default_factory=dict)
    proteome: dict[str, float] = field(default_factory=dict)
    concentrations: dict[str, float] = field(default_factory=dict)
    population: dict[str, int] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)

    def express_gene(self, gene: str, rate: float = 1.0):
        self.transcriptome[gene] = self.transcriptome.get(gene, 0) + rate

    def translate_protein(self, mrna: str, rate: float = 1.0):
        self.proteome[mrna] = self.proteome.get(mrna, 0) + rate

    def react(self, reaction_id: str, rate: float):
        self.concentrations[reaction_id] = self.concentrations.get(reaction_id, 0) + rate


@dataclass
class HybridState:
    """Σ_h = ⟨B, T_h, W, S_h⟩

    Hybrid state components:
    - B: active bridges
    - T_h: thresholds/transforms
    - W: uncertainty-weight maps
    - S_h: scheduling/synchronization state
    """

    active_bridges: list[str] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)
    uncertainty_weights: dict[str, float] = field(default_factory=dict)
    schedule: list[tuple[str, Any]] = field(default_factory=list)

    def activate_bridge(self, bridge_id: str, source: str, target: str):
        self.active_bridges.append(f"{bridge_id}:{source}->{target}")

    def set_threshold(self, key: str, value: float):
        self.thresholds[key] = value

    def schedule_event(self, time: float, event: Any):
        self.schedule.append((time, event))
        self.schedule.sort(key=lambda x: x[0])


@dataclass
class EnvironmentState:
    """Σ_e = ⟨external_signals, resources, noise, conditions⟩"""

    signals: dict[str, Any] = field(default_factory=dict)
    resources: dict[str, float] = field(default_factory=dict)
    noise: float = 0.0
    conditions: dict[str, Any] = field(default_factory=dict)

    def signal(self, channel: str, value: Any):
        self.signals[channel] = value

    def consume_resource(self, name: str, amount: float):
        self.resources[name] = max(0, self.resources.get(name, 0) - amount)


@dataclass
class TimeState:
    """Σ_t = ⟨t, Δt, history⟩"""

    t: float = 0.0
    dt: float = 1.0
    history: list[dict[str, Any]] = field(default_factory=list)

    def tick(self):
        self.t += self.dt
        return self.t

    def record(self, state_snapshot: dict[str, Any]):
        self.history.append({"time": self.t, "state": state_snapshot})


@dataclass
class StateManifold:
    """Σ = Σ_c × Σ_q × Σ_b × Σ_h × Σ_e × Σ_t

    The complete state manifold as a block vector:
        S = [Σ_c, Σ_q, Σ_b, Σ_h, Σ_e, Σ_t]^T
    """

    classical: ClassicalState = field(default_factory=ClassicalState)
    quantum: QuantumState = field(default_factory=QuantumState)
    biological: BiologicalState = field(default_factory=BiologicalState)
    hybrid: HybridState = field(default_factory=HybridState)
    environment: EnvironmentState = field(default_factory=EnvironmentState)
    time: TimeState = field(default_factory=TimeState)

    def as_block_vector(self) -> list[Any]:
        """Return state as block vector [Σ_c, Σ_q, Σ_b, Σ_h, Σ_e, Σ_t]."""
        return [
            self.classical,
            self.quantum,
            self.biological,
            self.hybrid,
            self.environment,
            self.time,
        ]

    def get_substrate(self, substrate: Substrate) -> Any:
        """Get substrate state by type."""
        mapping = {
            Substrate.CLASSICAL: self.classical,
            Substrate.QUANTUM: self.quantum,
            Substrate.BIOLOGICAL: self.biological,
            Substrate.HYBRID: self.hybrid,
            Substrate.ENVIRONMENT: self.environment,
            Substrate.TIME: self.time,
        }
        return mapping[substrate]

    def snapshot(self) -> dict[str, Any]:
        """Create serializable snapshot of state."""
        return {
            "t": self.time.t,
            "classical": {"values": list(self.classical.values.keys())},
            "quantum": {"registers": self.quantum.registers},
            "biological": {"genes": list(self.biological.genome.keys())},
            "hybrid": {"bridges": self.hybrid.active_bridges},
            "environment": {"signals": list(self.environment.signals.keys())},
        }


class RuntimeKernel:
    """Core runtime implementing Φ: Σ × A × O × E × Θ → Σ'"""

    def __init__(self):
        self.state = StateManifold()
        self.invariants: list[callable] = []
        self.verification_hooks: list[callable] = []

    def step(
        self,
        action_bundle: Optional[dict] = None,
        observation_bundle: Optional[dict] = None,
        environment: Optional[dict] = None,
        control_params: Optional[dict] = None,
    ) -> StateManifold:
        """Execute one runtime step: Σ_{t+1} = Φ(Σ_t, a_t, o_t, e_t, θ_t)."""
        # Update time
        self.state.time.tick()

        # Apply action bundle
        if action_bundle:
            self._apply_actions(action_bundle)

        # Process observations
        if observation_bundle:
            self._process_observations(observation_bundle)

        # Update environment
        if environment:
            self._update_environment(environment)

        # Verify invariants before commit
        if not self._verify_invariants():
            raise RuntimeError("Invariant violation - commit rejected")

        # Record to history
        self.state.time.record(self.state.snapshot())

        return self.state

    def _apply_actions(self, actions: dict[str, Any]):
        """Apply action bundle to state."""
        for substrate, action in actions.items():
            if substrate == "classical":
                self._apply_classical_action(action)
            elif substrate == "quantum":
                self._apply_quantum_action(action)
            elif substrate == "biological":
                self._apply_biological_action(action)
            elif substrate == "hybrid":
                self._apply_hybrid_action(action)

    def _apply_classical_action(self, action: dict):
        """Apply classical action."""
        if "set" in action:
            for k, v in action["set"].items():
                self.state.classical.set(k, v)
        if "emit" in action:
            self.state.classical.emit_event(action["emit"])

    def _apply_quantum_action(self, action: dict):
        """Apply quantum action (gate operations)."""
        if "gate" in action:
            self.state.quantum.apply_gate(action["gate"], action.get("targets", [0]))

    def _apply_biological_action(self, action: dict):
        """Apply biological action."""
        if "express" in action:
            self.state.biological.express_gene(action["express"], action.get("rate", 1.0))
        if "react" in action:
            self.state.biological.react(action["react"], action.get("rate", 1.0))

    def _apply_hybrid_action(self, action: dict):
        """Apply hybrid action."""
        if "bridge" in action:
            self.state.hybrid.activate_bridge(
                action["bridge"], action.get("source", ""), action.get("target", "")
            )

    def _process_observations(self, observations: dict):
        """Process observation bundle."""
        for obs_type, obs_value in observations.items():
            self.state.environment.signal(obs_type, obs_value)

    def _update_environment(self, env_update: dict):
        """Update environment state."""
        for key, value in env_update.items():
            self.state.environment.conditions[key] = value

    def _verify_invariants(self) -> bool:
        """Verify all invariants: Valid(Σ) = ∧_i C_i(Σ)."""
        for invariant in self.invariants:
            if not invariant(self.state):
                return False
        return True

    def register_invariant(self, invariant_fn: callable):
        """Register an invariant check function."""
        self.invariants.append(invariant_fn)

    def run(self, steps: int = 1, actions_per_step: Optional[list[dict]] = None):
        """Run kernel for multiple steps."""
        results = []
        for i in range(steps):
            actions = (
                actions_per_step[i] if actions_per_step and i < len(actions_per_step) else None
            )
            state = self.step(action_bundle=actions)
            results.append(state.snapshot())
        return results

"""
Axiom Canonical State Model - Coupled Hyperbundle State Representation

Implements Section 104.6 from Axiom specification:
State is a coupled hyperbundle: X = X_c × X_q × X_b × X_h × X_w × X_t × X_u × X_l × X_id × X_meta
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class StateDomain(Enum):
    """State domains in the coupled hyperbundle."""

    CLASSICAL = "classical"  # X_c: Classical/system state
    QUANTUM = "quantum"  # X_q: Quantum state
    BIOLOGICAL = "biological"  # X_b: Biological state
    HYBRID = "hybrid"  # X_h: Hybrid bridge state
    WORLD = "world"  # X_w: World/environment state
    TEMPORAL = "temporal"  # X_t: Time state
    UNCERTAINTY = "uncertainty"  # X_u: Uncertainty/epistemic state
    LEDGER = "ledger"  # X_l: Ledger/audit state
    IDENTITY = "identity"  # X_id: Identity state
    META = "meta"  # X_meta: Meta/self-model state


@dataclass(frozen=True)
class ClassicalState:
    """X_c: Classical/system state - deterministic system properties."""

    system_load: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage: float = 0.0
    network_io: dict[str, float] = field(default_factory=dict)
    process_count: int = 0
    thread_count: int = 0
    open_files: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_load": self.system_load,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_usage": self.disk_usage,
            "network_io": self.network_io,
            "process_count": self.process_count,
            "thread_count": self.thread_count,
            "open_files": self.open_files,
        }


@dataclass(frozen=True)
class QuantumState:
    """X_q: Quantum state representation for quantum-classical bridge."""

    superposition_weights: dict[str, float] = field(default_factory=dict)
    entanglement_map: dict[str, list[str]] = field(default_factory=dict)
    coherence_time: float = 0.0
    decoherence_rate: float = 0.0
    measurement_basis: str = "computational"

    def to_dict(self) -> dict[str, Any]:
        return {
            "superposition_weights": self.superposition_weights,
            "entanglement_map": self.entanglement_map,
            "coherence_time": self.coherence_time,
            "decoherence_rate": self.decoherence_rate,
            "measurement_basis": self.measurement_basis,
        }


@dataclass(frozen=True)
class BiologicalState:
    """X_b: Biological state - organic system analogies."""

    energy_level: float = 1.0  # 0.0 to 1.0
    metabolic_rate: float = 0.5
    health_score: float = 1.0
    stress_level: float = 0.0
    adaptation_capacity: float = 0.8
    regeneration_rate: float = 0.1
    immune_response: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "energy_level": self.energy_level,
            "metabolic_rate": self.metabolic_rate,
            "health_score": self.health_score,
            "stress_level": self.stress_level,
            "adaptation_capacity": self.adaptation_capacity,
            "regeneration_rate": self.regeneration_rate,
            "immune_response": self.immune_response,
        }


@dataclass(frozen=True)
class HybridState:
    """X_h: Hybrid bridge state - quantum-classical interface."""

    bridge_fidelity: float = 1.0
    encoding_map: dict[str, str] = field(default_factory=dict)
    error_mitigation: dict[str, float] = field(default_factory=dict)
    classical_shadow: dict[str, Any] = field(default_factory=dict)
    quantum_resource_usage: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge_fidelity": self.bridge_fidelity,
            "encoding_map": self.encoding_map,
            "error_mitigation": self.error_mitigation,
            "classical_shadow": self.classical_shadow,
            "quantum_resource_usage": self.quantum_resource_usage,
        }


@dataclass(frozen=True)
class WorldState:
    """X_w: World/environment state - external context."""

    environment_context: dict[str, Any] = field(default_factory=dict)
    external_pressure: float = 0.0
    available_resources: dict[str, float] = field(default_factory=dict)
    peer_connections: list[str] = field(default_factory=list)
    market_conditions: dict[str, Any] = field(default_factory=dict)
    weather_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "environment_context": self.environment_context,
            "external_pressure": self.external_pressure,
            "available_resources": self.available_resources,
            "peer_connections": self.peer_connections,
            "market_conditions": self.market_conditions,
            "weather_data": self.weather_data,
        }


@dataclass(frozen=True)
class TemporalState:
    """X_t: Time state - temporal evolution tracking."""

    current_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    time_scale: str = "realtime"  # realtime, simulated, paused
    tick_count: int = 0
    epoch_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    scheduled_events: list[dict[str, Any]] = field(default_factory=list)
    time_dilation: float = 1.0  # 1.0 = normal speed

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_time": self.current_time.isoformat(),
            "time_scale": self.time_scale,
            "tick_count": self.tick_count,
            "epoch_start": self.epoch_start.isoformat(),
            "scheduled_events": self.scheduled_events,
            "time_dilation": self.time_dilation,
        }


@dataclass(frozen=True)
class UncertaintyState:
    """X_u: Uncertainty/epistemic state - knowledge bounds."""

    probability_distributions: dict[str, dict[str, float]] = field(default_factory=dict)
    confidence_intervals: dict[str, tuple[float, float]] = field(default_factory=dict)
    entropy_measures: dict[str, float] = field(default_factory=dict)
    epistemic_uncertainty: float = 0.5  # Lack of knowledge
    aleatoric_uncertainty: float = 0.3  # Inherent randomness
    model_uncertainty: float = 0.2  # Model error

    def to_dict(self) -> dict[str, Any]:
        return {
            "probability_distributions": self.probability_distributions,
            "confidence_intervals": self.confidence_intervals,
            "entropy_measures": self.entropy_measures,
            "epistemic_uncertainty": self.epistemic_uncertainty,
            "aleatoric_uncertainty": self.aleatoric_uncertainty,
            "model_uncertainty": self.model_uncertainty,
        }


@dataclass(frozen=True)
class LedgerEntry:
    """Single ledger entry for audit trail."""

    timestamp: datetime
    transition_type: str
    from_state_hash: str
    to_state_hash: str
    action_taken: dict[str, Any]
    verification_result: dict[str, Any]
    entropy_change: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "transition_type": self.transition_type,
            "from_state_hash": self.from_state_hash,
            "to_state_hash": self.to_state_hash,
            "action_taken": self.action_taken,
            "verification_result": self.verification_result,
            "entropy_change": self.entropy_change,
        }


@dataclass
class LedgerState:
    """X_l: Ledger/audit state - immutable transition history."""

    entries: list[LedgerEntry] = field(default_factory=list)
    current_entropy: float = 0.0
    max_entries: int = 10000

    def append(self, entry: LedgerEntry) -> None:
        """Append entry with automatic pruning."""
        self.entries.append(entry)
        if len(self.entries) > self.max_entries:
            # Keep most recent entries, archive old ones
            self.entries = self.entries[-self.max_entries :]
        self.current_entropy += entry.entropy_change

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_count": len(self.entries),
            "current_entropy": self.current_entropy,
            "recent_entries": [e.to_dict() for e in self.entries[-10:]],
        }


@dataclass(frozen=True)
class IdentityState:
    """X_id: Identity state - self-model and continuity."""

    identity_hash: str = ""
    continuity_score: float = 1.0  # How consistent is identity over time
    self_model: dict[str, Any] = field(default_factory=dict)
    goals: list[dict[str, Any]] = field(default_factory=list)
    values: dict[str, float] = field(default_factory=dict)
    personality_profile: dict[str, float] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute identity hash from core components."""
        data = {
            "goals": sorted([g.get("id", "") for g in self.goals]),
            "values": dict(sorted(self.values.items())),
            "personality": dict(sorted(self.personality_profile.items())),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:32]

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity_hash": self.identity_hash or self.compute_hash(),
            "continuity_score": self.continuity_score,
            "self_model": self.self_model,
            "goals": self.goals,
            "values": self.values,
            "personality_profile": self.personality_profile,
        }


@dataclass(frozen=True)
class MetaState:
    """X_meta: Meta/self-model state - reflection and governance."""

    reflection_depth: int = 0
    self_evaluation: dict[str, float] = field(default_factory=dict)
    governance_status: dict[str, Any] = field(default_factory=dict)
    learning_rate: float = 0.01
    adaptation_history: list[dict[str, Any]] = field(default_factory=list)
    meta_constraints: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reflection_depth": self.reflection_depth,
            "self_evaluation": self.self_evaluation,
            "governance_status": self.governance_status,
            "learning_rate": self.learning_rate,
            "adaptation_count": len(self.adaptation_history),
            "meta_constraints": self.meta_constraints,
        }


@dataclass
class AxiomState:
    """
    Coupled hyperbundle state: X = X_c × X_q × X_b × X_h × X_w × X_t × X_u × X_l × X_id × X_meta

    This is the canonical state representation for the AMOS/Axiom system.
    All subsystems must map their state into this representation.
    """

    # Core state components
    classical: ClassicalState = field(default_factory=ClassicalState)
    quantum: QuantumState = field(default_factory=QuantumState)
    biological: BiologicalState = field(default_factory=BiologicalState)
    hybrid: HybridState = field(default_factory=HybridState)
    world: WorldState = field(default_factory=WorldState)
    temporal: TemporalState = field(default_factory=TemporalState)
    uncertainty: UncertaintyState = field(default_factory=UncertaintyState)
    ledger: LedgerState = field(default_factory=LedgerState)
    identity: IdentityState = field(default_factory=IdentityState)
    meta: MetaState = field(default_factory=MetaState)

    # Canonical hash for determinism verification
    canonical_hash: str = ""

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Compute canonical hash after initialization."""
        if not self.canonical_hash:
            object.__setattr__(self, "canonical_hash", self.compute_hash())

    def compute_hash(self) -> str:
        """Compute deterministic hash of entire state."""
        state_dict = {
            "classical": self.classical.to_dict(),
            "quantum": self.quantum.to_dict(),
            "biological": self.biological.to_dict(),
            "hybrid": self.hybrid.to_dict(),
            "world": self.world.to_dict(),
            "temporal": self.temporal.to_dict(),
            "uncertainty": self.uncertainty.to_dict(),
            "identity": self.identity.to_dict(),
            "meta": self.meta.to_dict(),
            "timestamp": self.timestamp.isoformat(),
        }
        return hashlib.sha256(
            json.dumps(state_dict, sort_keys=True, default=str).encode()
        ).hexdigest()

    def project(self, view: str) -> dict[str, Any]:
        """Project state into specific view."""
        projectors = {
            "deterministic": self._project_deterministic,
            "observational": self._project_observational,
            "decision": self._project_decision,
            "health": self._project_health,
            "audit": self._project_audit,
            "minimal": self._project_minimal,
        }
        projector = projectors.get(view, self._project_minimal)
        return projector()

    def _project_deterministic(self) -> dict[str, Any]:
        """Projection for deterministic core."""
        return {
            "state_hash": self.canonical_hash,
            "system_load": self.classical.system_load,
            "health_score": self.biological.health_score,
            "uncertainty_total": (
                self.uncertainty.epistemic_uncertainty
                + self.uncertainty.aleatoric_uncertainty
                + self.uncertainty.model_uncertainty
            )
            / 3,
            "identity_stable": self.identity.continuity_score > 0.8,
            "time_scale": self.temporal.time_scale,
        }

    def _project_observational(self) -> dict[str, Any]:
        """Projection for self-observer."""
        return {
            "contradiction_score": self._compute_contradiction_score(),
            "integrity_score": self._compute_integrity_score(),
            "drift_detected": self.meta.reflection_depth > 5,
            "learning_active": self.meta.learning_rate > 0,
            "governance_constraints": len(self.meta.meta_constraints),
        }

    def _project_decision(self) -> dict[str, Any]:
        """Projection for decision making."""
        return {
            "load_capacity_ratio": self.classical.system_load / 100,
            "prediction_confidence": 1.0 - self.uncertainty.epistemic_uncertainty,
            "system_ready": self.biological.health_score > 0.7,
            "environment_stable": self.world.external_pressure < 0.5,
            "resources_available": sum(self.world.available_resources.values()),
        }

    def _project_health(self) -> dict[str, Any]:
        """Projection for health monitoring."""
        return {
            "health_score": self.biological.health_score,
            "stress_level": self.biological.stress_level,
            "energy_level": self.biological.energy_level,
            "system_load": self.classical.system_load,
            "timestamp": self.timestamp.isoformat(),
        }

    def _project_audit(self) -> dict[str, Any]:
        """Projection for audit."""
        return {
            "state_hash": self.canonical_hash,
            "identity_hash": self.identity.compute_hash(),
            "ledger_entries": len(self.ledger.entries),
            "entropy": self.ledger.current_entropy,
            "timestamp": self.timestamp.isoformat(),
        }

    def _project_minimal(self) -> dict[str, Any]:
        """Minimal projection."""
        return {
            "hash": self.canonical_hash[:16],
            "health": self.biological.health_score,
            "timestamp": self.timestamp.isoformat(),
        }

    def _compute_contradiction_score(self) -> float:
        """Compute internal contradiction score."""
        scores = [
            abs(self.biological.health_score - (1.0 - self.biological.stress_level)),
            self.uncertainty.epistemic_uncertainty,
            1.0 - self.hybrid.bridge_fidelity,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def _compute_integrity_score(self) -> float:
        """Compute overall integrity score."""
        scores = [
            self.biological.health_score,
            1.0 - self.biological.stress_level,
            self.hybrid.bridge_fidelity,
            self.identity.continuity_score,
            1.0 - self.uncertainty.epistemic_uncertainty,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "classical": self.classical.to_dict(),
            "quantum": self.quantum.to_dict(),
            "biological": self.biological.to_dict(),
            "hybrid": self.hybrid.to_dict(),
            "world": self.world.to_dict(),
            "temporal": self.temporal.to_dict(),
            "uncertainty": self.uncertainty.to_dict(),
            "ledger": self.ledger.to_dict(),
            "identity": self.identity.to_dict(),
            "meta": self.meta.to_dict(),
            "canonical_hash": self.canonical_hash,
            "timestamp": self.timestamp.isoformat(),
        }


class StateManager:
    """Manages AxiomState lifecycle and transitions."""

    _instance: Optional[StateManager] = None

    def __new__(cls) -> StateManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._current: AxiomState = AxiomState()
        self._history: list[AxiomState] = []
        self._max_history = 1000
        self._initialized = True

    def get_current(self) -> AxiomState:
        """Get current state."""
        return self._current

    def transition(
        self, new_state: AxiomState, action: dict[str, Any], verification: dict[str, Any]
    ) -> None:
        """Perform state transition with ledger recording."""
        old_hash = self._current.canonical_hash
        new_hash = new_state.compute_hash()

        # Create ledger entry
        entry = LedgerEntry(
            timestamp=datetime.now(UTC),
            transition_type=action.get("type", "unknown"),
            from_state_hash=old_hash,
            to_state_hash=new_hash,
            action_taken=action,
            verification_result=verification,
            entropy_change=self._compute_entropy_change(self._current, new_state),
        )

        # Update state with ledger entry
        new_state.ledger.append(entry)

        # Store in history
        self._history.append(self._current)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        self._current = new_state

    def _compute_entropy_change(self, old: AxiomState, new: AxiomState) -> float:
        """Compute entropy change between states."""
        old_uncertainty = (
            old.uncertainty.epistemic_uncertainty + old.uncertainty.aleatoric_uncertainty
        ) / 2
        new_uncertainty = (
            new.uncertainty.epistemic_uncertainty + new.uncertainty.aleatoric_uncertainty
        ) / 2
        return new_uncertainty - old_uncertainty

    def get_history(self, n: int = 10) -> list[AxiomState]:
        """Get recent state history."""
        return self._history[-n:]


def get_state_manager() -> StateManager:
    """Get singleton state manager."""
    return StateManager()

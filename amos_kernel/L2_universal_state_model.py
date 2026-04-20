"""
L2 - Universal State Model

All system state reduces into one normalized internal representation.

State Tensor:
    T^{μναβ}

Axes:
    μ: biological / load / regulation
    ν: cognition / prediction / contradiction
    α: org-system / policy / coordination
    β: environment / context / external pressure

This becomes the one internal state object every layer reads and updates.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any


@dataclass
class StateTensor:
    """
    Universal state tensor T^{μναβ}.

    All subsystem state maps into this representation.
    Projections allow different views for different purposes.
    """

    # Canonical tensor axes
    mu: dict[str, Any] = field(default_factory=dict)  # Biological/load/regulation
    nu: dict[str, Any] = field(default_factory=dict)  # Cognition/prediction
    alpha: dict[str, Any] = field(default_factory=dict)  # Org-system/policy
    beta: dict[str, Any] = field(default_factory=dict)  # Environment/context

    # Integrity tensor (computed)
    integrity: dict[str, float] = field(default_factory=dict)

    # Raw source data (preserved for audit)
    raw_data: dict[str, Any] = field(default_factory=dict)

    # Projections (computed views)
    projections: dict[str, Any] = field(default_factory=dict)

    # Canonical hash (for determinism verification)
    canonical_hash: str = ""

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def compute_hash(self) -> str:
        """Compute canonical hash for determinism verification."""
        data = {
            "mu": self._normalize_for_hash(self.mu),
            "nu": self._normalize_for_hash(self.nu),
            "alpha": self._normalize_for_hash(self.alpha),
            "beta": self._normalize_for_hash(self.beta),
        }
        hash_input = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]

    def update_hash(self) -> None:
        """Update canonical hash."""
        self.canonical_hash = self.compute_hash()

    def project(self, view: str, weights: dict[str, float] | None = None) -> dict[str, Any]:
        """Project tensor into a specific view."""
        projectors = {
            "deterministic": self._project_deterministic,
            "observational": self._project_observational,
            "repair": self._project_repair,
            "decision": self._project_decision,
            "health": self._project_health,
            "internal": self._project_internal,
            "external": self._project_external,
        }

        projector = projectors.get(view, lambda w: {"raw": self.raw_data})
        result = projector(weights)
        self.projections[view] = result
        return result

    def _project_deterministic(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Projection for deterministic core."""
        return {
            "state_hash": self.canonical_hash,
            "mu_load": self.mu.get("load", 0.0),
            "nu_prediction_error": self.nu.get("prediction_error", 0.0),
            "alpha_policy_state": self.alpha.get("policy_state", {}),
            "beta_environment_stable": self.beta.get("stable", True),
        }

    def _project_observational(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Projection for self-observer."""
        return {
            "drift_detected": self.integrity.get("drift_score", 0.0) > 0.5,
            "contradiction_score": self.integrity.get("contradiction_score", 0.0),
            "quadrant_scores": {
                "code": self.integrity.get("code_score", 0.0),
                "build": self.integrity.get("build_score", 0.0),
                "operational": self.integrity.get("operational_score", 0.0),
                "environment": self.integrity.get("environment_score", 0.0),
            },
            "raw_health": self.raw_data.get("health", {}),
        }

    def _project_repair(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Projection for repair executor."""
        return {
            "repair_queue": self.alpha.get("repair_queue", []),
            "repair_in_progress": self.alpha.get("repair_in_progress", False),
            "last_repair_result": self.alpha.get("last_repair_result", {}),
            "available_repairs": self.alpha.get("available_repairs", []),
        }

    def _project_decision(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Projection for decision making."""
        return {
            "load_capacity_ratio": self.mu.get("load", 0.0)
            / max(self.mu.get("capacity", 1.0), 1e-6),
            "prediction_confidence": 1.0 - self.nu.get("prediction_error", 0.0),
            "system_ready": self.alpha.get("system_ready", False),
            "environment_stable": self.beta.get("stable", True),
            "integrity_score": self._compute_integrity_score(),
        }

    def _project_health(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Projection for health monitoring."""
        return {
            "health_score": self.mu.get("health_score", 1.0),
            "stress_level": self.mu.get("stress", 0.0),
            "cognitive_load": self.nu.get("cognitive_load", 0.0),
            "system_integrity": self._compute_integrity_score(),
            "timestamp": self.timestamp.isoformat(),
        }

    def _project_internal(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """Internal state projection (dual interaction)."""
        return {
            "mu": self.mu,
            "nu": self.nu,
            "alpha": self.alpha,
        }

    def _project_external(self, weights: dict[str, float] | None) -> dict[str, Any]:
        """External state projection (dual interaction)."""
        return {
            "beta": self.beta,
            "external_events": self.raw_data.get("external_events", []),
            "environment_context": self.beta.get("context", {}),
        }

    def _compute_integrity_score(self) -> float:
        """Compute overall integrity score."""
        scores = [
            self.integrity.get("code_score", 0.5),
            self.integrity.get("build_score", 0.5),
            self.integrity.get("operational_score", 0.5),
            self.integrity.get("environment_score", 0.5),
        ]
        return sum(scores) / len(scores)

    @staticmethod
    def _normalize_for_hash(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize data for consistent hashing."""
        return {k: str(v) for k, v in sorted(data.items())}


@dataclass
class IntegrityTensor:
    """Integrity scores across all axes."""

    mu_integrity: float = 1.0  # Biological/regulation integrity
    nu_integrity: float = 1.0  # Cognition consistency
    alpha_integrity: float = 1.0  # Policy/org-system integrity
    beta_integrity: float = 1.0  # Environment/context integrity

    overall: float = field(init=False)

    def __post_init__(self) -> None:
        self.overall = (
            self.mu_integrity * self.nu_integrity * self.alpha_integrity * self.beta_integrity
        ) ** 0.25


@dataclass
class LoadCapacityModel:
    """Load vs capacity model."""

    current_load: float = 0.0
    max_capacity: float = 100.0
    safety_margin: float = 0.2

    def ratio(self) -> float:
        """Compute load/capacity ratio."""
        return self.current_load / max(self.max_capacity, 1e-6)

    def available_capacity(self) -> float:
        """Compute available capacity."""
        safe_capacity = self.max_capacity * (1.0 - self.safety_margin)
        return max(safe_capacity - self.current_load, 0.0)

    def is_overloaded(self) -> bool:
        """Check if system is overloaded."""
        return self.ratio() > (1.0 - self.safety_margin)


class UniversalStateModel:
    """
    Manages the universal state tensor.

    All subsystems must map into this layer.
    """

    _instance: UniversalStateModel | None = None

    def __new__(cls) -> UniversalStateModel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._current_state: StateTensor | None = None
        self._state_history: list[StateTensor] = []
        self._max_history = 100
        self._initialized = True

    def normalize(self, raw_inputs: dict[str, Any]) -> StateTensor:
        """
        Normalize raw inputs into canonical state tensor.

        This is the entry point. All state must pass through here.
        """
        tensor = StateTensor(
            mu=self._extract_mu(raw_inputs),
            nu=self._extract_nu(raw_inputs),
            alpha=self._extract_alpha(raw_inputs),
            beta=self._extract_beta(raw_inputs),
            raw_data=raw_inputs,
        )

        # Compute integrity
        tensor.integrity = self._compute_integrity(tensor)

        # Update hash
        tensor.update_hash()

        # Store
        self._current_state = tensor
        self._state_history.append(tensor)
        if len(self._state_history) > self._max_history:
            self._state_history.pop(0)

        return tensor

    def project(
        self, tensor: StateTensor, view: str, weights: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """Project tensor into a specific view."""
        return tensor.project(view, weights)

    def integrity(self, tensor: StateTensor) -> IntegrityTensor:
        """Compute integrity tensor."""
        return IntegrityTensor(
            mu_integrity=tensor.integrity.get("mu_score", 1.0),
            nu_integrity=tensor.integrity.get("nu_score", 1.0),
            alpha_integrity=tensor.integrity.get("alpha_score", 1.0),
            beta_integrity=tensor.integrity.get("beta_score", 1.0),
        )

    def load_capacity_ratio(self, tensor: StateTensor) -> float:
        """Compute load/capacity ratio."""
        load_model = LoadCapacityModel(
            current_load=tensor.mu.get("load", 0.0),
            max_capacity=tensor.mu.get("capacity", 100.0),
        )
        return load_model.ratio()

    def get_current_state(self) -> StateTensor | None:
        """Get current state tensor."""
        return self._current_state

    def get_state_history(self) -> list[StateTensor]:
        """Get state history."""
        return self._state_history.copy()

    def _extract_mu(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract μ (biological/load/regulation) axis."""
        return {
            "load": raw.get("system_load", 0.0),
            "capacity": raw.get("system_capacity", 100.0),
            "health_score": raw.get("health_score", 1.0),
            "stress": raw.get("stress_level", 0.0),
            "regulation_status": raw.get("regulation", {}),
        }

    def _extract_nu(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract ν (cognition/prediction) axis."""
        return {
            "prediction_error": raw.get("prediction_error", 0.0),
            "cognitive_load": raw.get("cognitive_load", 0.0),
            "contradiction_count": raw.get("contradictions", 0),
            "inference_depth": raw.get("inference_depth", 0),
        }

    def _extract_alpha(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract α (org-system/policy) axis."""
        return {
            "policy_state": raw.get("policies", {}),
            "system_ready": raw.get("system_ready", False),
            "repair_queue": raw.get("repair_queue", []),
            "subsystem_states": raw.get("subsystems", {}),
        }

    def _extract_beta(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract β (environment/context) axis."""
        return {
            "stable": raw.get("environment_stable", True),
            "context": raw.get("environment_context", {}),
            "external_pressure": raw.get("external_pressure", 0.0),
            "available_resources": raw.get("resources", {}),
        }

    def _compute_integrity(self, tensor: StateTensor) -> dict[str, float]:
        """Compute integrity scores for all axes."""
        # μ integrity: based on load/capacity ratio
        load_ratio = tensor.mu.get("load", 0.0) / max(tensor.mu.get("capacity", 1.0), 1e-6)
        mu_score = max(0.0, 1.0 - load_ratio)

        # ν integrity: based on prediction error and contradictions
        pred_error = tensor.nu.get("prediction_error", 0.0)
        contradictions = tensor.nu.get("contradiction_count", 0)
        nu_score = max(0.0, 1.0 - pred_error - (contradictions * 0.1))

        # α integrity: based on system readiness
        alpha_score = 1.0 if tensor.alpha.get("system_ready", False) else 0.5

        # β integrity: based on environment stability
        beta_score = 1.0 if tensor.beta.get("stable", True) else 0.3

        # Quadrant scores (for ULK)
        code_score = (
            raw_data.get("code", {}).get("score", 0.5) if (raw_data := tensor.raw_data) else 0.5
        )
        build_score = raw_data.get("build", {}).get("score", 0.5) if raw_data else 0.5
        operational_score = raw_data.get("operational", {}).get("score", 0.5) if raw_data else 0.5
        environment_score = raw_data.get("environment", {}).get("score", 0.5) if raw_data else 0.5

        return {
            "mu_score": mu_score,
            "nu_score": nu_score,
            "alpha_score": alpha_score,
            "beta_score": beta_score,
            "code_score": code_score,
            "build_score": build_score,
            "operational_score": operational_score,
            "environment_score": environment_score,
            "drift_score": raw_data.get("drift_score", 0.0) if raw_data else 0.0,
            "contradiction_score": raw_data.get("contradiction_score", 0.0) if raw_data else 0.0,
            "overall": (mu_score * nu_score * alpha_score * beta_score) ** 0.25,
        }


def get_universal_state_model() -> UniversalStateModel:
    """Get the singleton state model."""
    return UniversalStateModel()

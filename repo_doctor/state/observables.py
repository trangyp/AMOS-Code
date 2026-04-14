"""
Repo Doctor Ω∞ - Observables

Structured measurements, not warnings.

O = {
  o_parse_fatal, o_parse_recoverable,
  o_import_unresolved, o_export_unreachable,
  o_signature_arity_mismatch, o_signature_kwarg_mismatch,
  o_return_shape_mismatch,
  o_entrypoint_missing, o_entrypoint_wrong_target,
  o_packaging_conflict,
  o_roundtrip_failure,
  o_status_false_claim,
  o_runtime_promise_violation,
  o_test_contract_failure,
  o_security_flow_violation,
  o_temporal_breakpoint
}

Subsystem amplitudes:
αk = exp(- Σj wk,j · oj)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .basis import StateDimension


@dataclass
class Observable:
    """A single structured observable measurement."""

    name: str
    dimension: StateDimension
    severity: float  # 0-1, higher is worse
    details: dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    line_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "dimension": self.dimension.value,
            "severity": self.severity,
            "details": self.details,
            "source": f"{self.source_file}:{self.line_number}" if self.source_file else "",
        }


@dataclass
class MeasurementResult:
    """Result of measuring an observable."""

    observable: Observable
    measured_value: float
    confidence: float
    timestamp: str = ""


class ObservableSet:
    """
    Collection of observables feeding state amplitudes.
    """

    # Dimension weights for amplitude calculation
    DIMENSION_WEIGHTS: dict[StateDimension, dict[str, float]] = {
        StateDimension.SYNTAX: {
            "parse_fatal": 10.0,
            "parse_recoverable": 0.5,
        },
        StateDimension.IMPORTS: {
            "unresolved_import": 5.0,
            "export_unreachable": 3.0,
        },
        StateDimension.API: {
            "signature_arity_mismatch": 8.0,
            "signature_kwarg_mismatch": 6.0,
            "return_shape_mismatch": 7.0,
            "doc_example_mismatch": 4.0,
        },
        StateDimension.ENTRYPOINTS: {
            "entrypoint_missing": 10.0,
            "entrypoint_wrong_target": 9.0,
            "unconsumed_flag": 3.0,
            "unimplemented_transport": 8.0,
        },
        StateDimension.PACKAGING: {
            "metadata_conflict": 5.0,
            "unshipped_module": 8.0,
            "broken_console_script": 9.0,
        },
        StateDimension.PERSISTENCE: {
            "roundtrip_failure": 7.0,
            "schema_field_loss": 6.0,
            "cache_poison": 10.0,
        },
        StateDimension.STATUS: {
            "false_enabled": 5.0,
            "false_initialized": 7.0,
            "false_healthy": 10.0,
            "false_active": 4.0,
        },
        StateDimension.SECURITY: {
            "security_flow_violation": 10.0,
            "disallowed_dependency": 8.0,
        },
    }

    def __init__(self):
        self.observables: list[Observable] = []

    def add(self, obs: Observable) -> None:
        """Add an observable measurement."""
        self.observables.append(obs)

    def get_for_dimension(self, dim: StateDimension) -> list[Observable]:
        """Get all observables for a dimension."""
        return [o for o in self.observables if o.dimension == dim]

    def calculate_amplitude(self, dim: StateDimension) -> float:
        """
        Calculate amplitude from observables:
        αk = exp(- Σj wk,j · oj)
        """
        import math

        obs_for_dim = self.get_for_dimension(dim)
        if not obs_for_dim:
            return 1.0  # No issues = perfect amplitude

        weights = self.DIMENSION_WEIGHTS.get(dim, {})

        total_penalty = 0.0
        for obs in obs_for_dim:
            w = weights.get(obs.name, 1.0)
            total_penalty += w * obs.severity

        # Exponential decay
        return math.exp(-total_penalty / 10.0)

    def to_amplitude_dict(self) -> dict[StateDimension, float]:
        """Calculate all dimension amplitudes."""
        return {dim: self.calculate_amplitude(dim) for dim in StateDimension}

    def critical_observables(self, threshold: float = 0.5) -> list[Observable]:
        """Get observables above severity threshold."""
        return [o for o in self.observables if o.severity >= threshold]

    def to_dict(self) -> dict[str, Any]:
        """Serialize observable set."""
        return {
            "count": len(self.observables),
            "by_dimension": {
                dim.value: [o.to_dict() for o in self.get_for_dimension(dim)]
                for dim in StateDimension
            },
            "amplitudes": {dim.value: self.calculate_amplitude(dim) for dim in StateDimension},
        }

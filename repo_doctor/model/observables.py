"""
Repo Doctor Omega - Observables System

Structured measurements for repository state:
- o_parse_errors: Fatal parse errors count
- o_unresolved_imports: Unresolved import count
- o_signature_mismatches: Call signature violations
- o_missing_entrypoints: Missing entrypoint count
- o_packaging_conflicts: Build/runtime mismatches
- o_test_failures: Failed test count
- o_security_findings: Security findings count
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObservationResult:
    """Result of a single observable measurement."""

    name: str
    value: float
    unit: str = "count"
    severity: str = "info"  # info, warning, error, critical
    details: List[str] = field(default_factory=list)
    files_affected: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "severity": self.severity,
            "details": self.details,
            "files_affected": self.files_affected,
        }


class ObservableSet:
    """
    Collection of all repository observables.

    These are raw measurements that feed into state vector amplitudes
    via exponential decay: αk = exp(-Σj wk,j · oj)
    """

    def __init__(self):
        self.observations: Dict[str, ObservationResult] = {}

    def add(self, result: ObservationResult) -> None:
        """Add an observation."""
        self.observations[result.name] = result

    def get(self, name: str) -> float:
        """Get observation value by name."""
        obs = self.observations.get(name)
        return obs.value if obs else 0.0

    def get_severity_count(self, severity: str) -> int:
        """Count observations of a given severity."""
        return sum(1 for obs in self.observations.values() if obs.severity == severity)

    def to_dict(self) -> dict[str, float]:
        """Convert to flat dictionary of observable values."""
        return {name: obs.value for name, obs in self.observations.items()}

    @classmethod
    def from_sensor_data(cls, sensor_results: Dict[str, Any]) -> ObservableSet:
        """
        Build observables from sensor backend results.

        Args:
        ----
            sensor_results: Raw output from Tree-sitter, CodeQL, Joern, etc.

        """
        obs = cls()

        # Tree-sitter observations
        if "parse_errors" in sensor_results:
            obs.add(
                ObservationResult(
                    name="parse_errors",
                    value=sensor_results["parse_errors"],
                    severity="critical" if sensor_results["parse_errors"] > 0 else "info",
                    details=sensor_results.get("parse_error_files", []),
                )
            )

        # Import observations
        if "unresolved_imports" in sensor_results:
            obs.add(
                ObservationResult(
                    name="unresolved_imports",
                    value=sensor_results["unresolved_imports"],
                    severity="error" if sensor_results["unresolved_imports"] > 0 else "info",
                    details=sensor_results.get("unresolved_import_details", []),
                )
            )

        # Type/API observations
        if "signature_mismatches" in sensor_results:
            obs.add(
                ObservationResult(
                    name="signature_mismatches",
                    value=sensor_results["signature_mismatches"],
                    severity="error" if sensor_results["signature_mismatches"] > 0 else "info",
                )
            )

        # Entrypoint observations
        if "missing_entrypoints" in sensor_results:
            obs.add(
                ObservationResult(
                    name="missing_entrypoints",
                    value=sensor_results["missing_entrypoints"],
                    severity="error" if sensor_results["missing_entrypoints"] > 0 else "info",
                    details=sensor_results.get("missing_entrypoint_names", []),
                )
            )

        # Packaging observations
        if "packaging_conflicts" in sensor_results:
            obs.add(
                ObservationResult(
                    name="packaging_conflicts",
                    value=sensor_results["packaging_conflicts"],
                    severity="error" if sensor_results["packaging_conflicts"] > 0 else "info",
                )
            )

        # Test observations
        if "test_failures" in sensor_results:
            total = sensor_results.get("total_tests", 1)
            failures = sensor_results["test_failures"]
            obs.add(
                ObservationResult(
                    name="test_failures",
                    value=failures,
                    unit="failures",
                    severity="error" if failures > 0 else "info",
                    details=[f"{failures}/{total} tests failed"],
                )
            )

        # Security observations
        if "security_findings" in sensor_results:
            critical = sensor_results.get("critical_findings", 0)
            high = sensor_results.get("high_findings", 0)
            medium = sensor_results.get("medium_findings", 0)

            severity = "info"
            if critical > 0:
                severity = "critical"
            elif high > 0:
                severity = "error"
            elif medium > 0:
                severity = "warning"

            obs.add(
                ObservationResult(
                    name="security_findings",
                    value=sensor_results["security_findings"],
                    severity=severity,
                    details=[f"{critical} critical, {high} high, {medium} medium"],
                )
            )

        # Persistence observations
        if "persistence_failures" in sensor_results:
            obs.add(
                ObservationResult(
                    name="persistence_failures",
                    value=sensor_results["persistence_failures"],
                    severity="error" if sensor_results["persistence_failures"] > 0 else "info",
                )
            )

        # Status truth observations
        if "status_false_claims" in sensor_results:
            obs.add(
                ObservationResult(
                    name="status_false_claims",
                    value=sensor_results["status_false_claims"],
                    severity="error" if sensor_results["status_false_claims"] > 0 else "info",
                    details=sensor_results.get("false_claim_details", []),
                )
            )

        return obs

    def compute_amplitude(self, dimension: str, weights: Dict[str, float]) -> float:
        """
        Compute amplitude from observables: α = exp(-Σ wj · oj)

        Args:
        ----
            dimension: Target dimension name
            weights: Mapping from observable names to weights for this dimension

        """
        import math

        total = 0.0
        for obs_name, weight in weights.items():
            value = self.get(obs_name)
            total += weight * value

        return math.exp(-total)

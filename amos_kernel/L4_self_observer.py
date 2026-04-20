"""
L4 - Self Observer

Where the "brain fixes itself" begins. But it only proposes.

Responsibilities:
- drift detection
- mismatch detection
- contract violations
- structural audits
- correction proposals

Core loop:
    system → observe self → detect drift → propose correction
    → validate via ULK → apply via RepairExecutor

No direct mutation without validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from amos_kernel.contracts import (
    KernelResult,
)

if TYPE_CHECKING:
    from amos_kernel.L2_universal_state_model import StateTensor


@dataclass
class DriftReport:
    """Report of detected drift."""

    drift_type: str  # "contradiction", "degradation", "structural", "performance"
    severity: float  # 0.0 to 1.0
    location: str  # Where drift was detected
    evidence: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ContractReport:
    """Report of contract violations."""

    contract_type: str  # "api", "build", "runtime", "interface"
    violations: list[dict[str, Any]]
    severity: float
    affected_components: list[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ObservationRecord:
    """Record of a single observation."""

    observation_type: str
    state_hash: str
    findings: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class SelfObserver:
    """
    Self-observation layer. Detects drift, proposes repairs.

    Never mutates directly. Only proposes corrections that
    must be validated by ULK before execution.
    """

    _instance: Optional[SelfObserver] = None

    def __new__(cls) -> SelfObserver:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._observation_history: list[ObservationRecord] = []
        self._drift_history: list[DriftReport] = []
        self._contract_history: list[ContractReport] = []
        self._observation_interval: float = 30.0  # seconds
        self._initialized = True

    def detect_drift(self, state: StateTensor) -> list[DriftReport]:
        """
        Detect drift in system state.

        Drift types:
        - contradiction: ¬(A ∧ ¬A) violated
        - degradation: quadrant scores declining
        - structural: component relationships broken
        - performance: latency/throughput degradation
        """
        reports: list[DriftReport] = []

        # Check for contradictions
        contradiction_drift = self._detect_contradiction_drift(state)
        if contradiction_drift:
            reports.append(contradiction_drift)

        # Check for degradation
        degradation_drift = self._detect_degradation_drift(state)
        if degradation_drift:
            reports.append(degradation_drift)

        # Check for structural drift
        structural_drift = self._detect_structural_drift(state)
        if structural_drift:
            reports.append(structural_drift)

        # Check for performance drift
        performance_drift = self._detect_performance_drift(state)
        if performance_drift:
            reports.append(performance_drift)

        self._drift_history.extend(reports)
        return reports

    def detect_contract_mismatch(self, repo_state: dict[str, Any]) -> list[ContractReport]:
        """
        Detect contract mismatches in repo state.

        Contracts:
        - api: API contracts (schemas, endpoints)
        - build: Build contracts (dependencies, paths)
        - runtime: Runtime contracts (config, env)
        - interface: Interface contracts (imports, exports)
        """
        reports: list[ContractReport] = []

        # Check API contracts
        api_violations = self._check_api_contracts(repo_state)
        if api_violations:
            reports.append(
                ContractReport(
                    contract_type="api",
                    violations=api_violations,
                    severity=self._compute_violation_severity(api_violations),
                    affected_components=[v.get("component", "unknown") for v in api_violations],
                )
            )

        # Check build contracts
        build_violations = self._check_build_contracts(repo_state)
        if build_violations:
            reports.append(
                ContractReport(
                    contract_type="build",
                    violations=build_violations,
                    severity=self._compute_violation_severity(build_violations),
                    affected_components=[v.get("component", "unknown") for v in build_violations],
                )
            )

        # Check runtime contracts
        runtime_violations = self._check_runtime_contracts(repo_state)
        if runtime_violations:
            reports.append(
                ContractReport(
                    contract_type="runtime",
                    violations=runtime_violations,
                    severity=self._compute_violation_severity(runtime_violations),
                    affected_components=[v.get("component", "unknown") for v in runtime_violations],
                )
            )

        # Check interface contracts
        interface_violations = self._check_interface_contracts(repo_state)
        if interface_violations:
            reports.append(
                ContractReport(
                    contract_type="interface",
                    violations=interface_violations,
                    severity=self._compute_violation_severity(interface_violations),
                    affected_components=[
                        v.get("component", "unknown") for v in interface_violations
                    ],
                )
            )

        self._contract_history.extend(reports)
        return reports

    def propose_repairs(
        self, drift_reports: list[DriftReport], contract_reports: list[ContractReport]
    ) -> KernelResult[list[dict[str, Any]]]:
        """
        Propose repairs based on detected issues.

        This only proposes. Actual repair requires ULK validation.
        """
        proposals: list[dict[str, Any]] = []

        # Generate proposals for drift
        for drift in drift_reports:
            proposal = self._generate_drift_repair(drift)
            if proposal:
                proposals.append(proposal)

        # Generate proposals for contract violations
        for contract in contract_reports:
            proposal = self._generate_contract_repair(contract)
            if proposal:
                proposals.append(proposal)

        # Record observation
        record = ObservationRecord(
            observation_type="repair_proposal",
            state_hash="proposed",
            findings={"proposals": len(proposals), "drift_count": len(drift_reports)},
        )
        self._observation_history.append(record)

        if proposals:
            return KernelResult.ok(proposals, "SelfObserver")

        return KernelResult.ok([], "SelfObserver")

    def structural_audit(self, state: StateTensor) -> dict[str, Any]:
        """
        Perform structural audit of system.

        Returns comprehensive structural health report.
        """
        audit = {
            "timestamp": datetime.now(UTC).isoformat(),
            "tensor_integrity": self._audit_tensor_axes(state),
            "projection_coverage": self._audit_projections(state),
            "historical_stability": self._audit_history_stability(),
            "quadrant_balance": self._audit_quadrant_balance(state),
        }

        record = ObservationRecord(
            observation_type="structural_audit",
            state_hash=state.canonical_hash,
            findings=audit,
        )
        self._observation_history.append(record)

        return audit

    def get_observation_history(self) -> list[ObservationRecord]:
        """Get observation history."""
        return self._observation_history.copy()

    def get_drift_history(self) -> list[DriftReport]:
        """Get drift history."""
        return self._drift_history.copy()

    def _detect_contradiction_drift(self, state: StateTensor) -> Optional[DriftReport]:
        """Detect contradiction-based drift."""
        contradiction_score = state.integrity.get("contradiction_score", 0.0)

        if contradiction_score > 0.3:  # Threshold
            return DriftReport(
                drift_type="contradiction",
                severity=contradiction_score,
                location="state_tensor",
                evidence={"contradiction_score": contradiction_score},
            )
        return None

    def _detect_degradation_drift(self, state: StateTensor) -> Optional[DriftReport]:
        """Detect degradation drift."""
        overall = state.integrity.get("overall", 1.0)

        if overall < 0.7:  # Degradation threshold
            return DriftReport(
                drift_type="degradation",
                severity=1.0 - overall,
                location="integrity",
                evidence={"integrity_score": overall},
            )
        return None

    def _detect_structural_drift(self, state: StateTensor) -> Optional[DriftReport]:
        """Detect structural drift."""
        # Check if projections are incomplete
        expected_projections = {"deterministic", "observational", "repair", "decision"}
        actual_projections = set(state.projections.keys())

        missing = expected_projections - actual_projections

        if missing:
            return DriftReport(
                drift_type="structural",
                severity=len(missing) / len(expected_projections),
                location="projections",
                evidence={"missing_projections": list(missing)},
            )
        return None

    def _detect_performance_drift(self, state: StateTensor) -> Optional[DriftReport]:
        """Detect performance drift."""
        load_ratio = state.mu.get("load", 0.0) / max(state.mu.get("capacity", 1.0), 1e-6)

        if load_ratio > 0.9:  # Overload threshold
            return DriftReport(
                drift_type="performance",
                severity=load_ratio,
                location="load_capacity",
                evidence={"load_ratio": load_ratio},
            )
        return None

    def _check_api_contracts(self, repo_state: dict[str, Any]) -> list[dict[str, Any]]:
        """Check API contract compliance."""
        violations: list[dict[str, Any]] = []

        api_state = repo_state.get("api", {})
        schemas = api_state.get("schemas", {})
        endpoints = api_state.get("endpoints", {})

        # Check for schema mismatches
        for endpoint, config in endpoints.items():
            expected_schema = config.get("schema")
            if expected_schema and expected_schema not in schemas:
                violations.append(
                    {
                        "component": endpoint,
                        "issue": "missing_schema",
                        "expected": expected_schema,
                    }
                )

        return violations

    def _check_build_contracts(self, repo_state: dict[str, Any]) -> list[dict[str, Any]]:
        """Check build contract compliance."""
        violations: list[dict[str, Any]] = []

        build_state = repo_state.get("build", {})
        declared_deps = build_state.get("dependencies", {})
        resolved_deps = build_state.get("resolved", {})

        # Check for unresolved dependencies
        for dep, version in declared_deps.items():
            if dep not in resolved_deps:
                violations.append(
                    {
                        "component": dep,
                        "issue": "unresolved_dependency",
                        "expected_version": version,
                    }
                )

        return violations

    def _check_runtime_contracts(self, repo_state: dict[str, Any]) -> list[dict[str, Any]]:
        """Check runtime contract compliance."""
        violations: list[dict[str, Any]] = []

        runtime_state = repo_state.get("runtime", {})
        required_env = runtime_state.get("required_env", [])
        available_env = runtime_state.get("available_env", {})

        for env_var in required_env:
            if env_var not in available_env:
                violations.append(
                    {
                        "component": env_var,
                        "issue": "missing_environment_variable",
                    }
                )

        return violations

    def _check_interface_contracts(self, repo_state: dict[str, Any]) -> list[dict[str, Any]]:
        """Check interface contract compliance."""
        violations: list[dict[str, Any]] = []

        interface_state = repo_state.get("interface", {})
        exports = interface_state.get("exports", [])
        imports = interface_state.get("imports", [])

        # Check for circular imports (simplified)
        for imp in imports:
            if imp in exports:
                violations.append(
                    {
                        "component": imp,
                        "issue": "potential_circular_dependency",
                    }
                )

        return violations

    def _compute_violation_severity(self, violations: list[dict[str, Any]]) -> float:
        """Compute severity from violation count."""
        if not violations:
            return 0.0
        return min(len(violations) * 0.1, 1.0)

    def _generate_drift_repair(self, drift: DriftReport) -> Optional[dict[str, Any]]:
        """Generate repair proposal for drift."""
        repairs = {
            "contradiction": {
                "action": "enter_safe_mode",
                "target": "state_tensor",
                "priority": "critical",
            },
            "degradation": {
                "action": "reduce_load",
                "target": "mu_axis",
                "priority": "high",
            },
            "structural": {
                "action": "rebuild_projections",
                "target": "state_model",
                "priority": "medium",
            },
            "performance": {
                "action": "scale_capacity",
                "target": "mu_axis",
                "priority": "high",
            },
        }

        return repairs.get(drift.drift_type)

    def _generate_contract_repair(self, contract: ContractReport) -> Optional[dict[str, Any]]:
        """Generate repair proposal for contract violation."""
        repairs = {
            "api": {
                "action": "regenerate_schemas",
                "target": "api_layer",
                "priority": "high",
            },
            "build": {
                "action": "update_dependencies",
                "target": "build_system",
                "priority": "medium",
            },
            "runtime": {
                "action": "configure_environment",
                "target": "runtime_config",
                "priority": "critical",
            },
            "interface": {
                "action": "refactor_imports",
                "target": "module_structure",
                "priority": "low",
            },
        }

        return repairs.get(contract.contract_type)

    def _audit_tensor_axes(self, state: StateTensor) -> dict[str, Any]:
        """Audit tensor axes for completeness."""
        return {
            "mu_complete": bool(state.mu),
            "nu_complete": bool(state.nu),
            "alpha_complete": bool(state.alpha),
            "beta_complete": bool(state.beta),
        }

    def _audit_projections(self, state: StateTensor) -> dict[str, Any]:
        """Audit projection coverage."""
        expected = {"deterministic", "observational", "repair", "decision", "health"}
        actual = set(state.projections.keys())

        return {
            "coverage": len(actual) / len(expected),
            "missing": list(expected - actual),
            "extra": list(actual - expected),
        }

    def _audit_history_stability(self) -> dict[str, Any]:
        """Audit historical stability."""
        if len(self._drift_history) < 2:
            return {"stable": True, "trend": "insufficient_data"}

        recent_drifts = self._drift_history[-10:]
        avg_severity = sum(d.severity for d in recent_drifts) / len(recent_drifts)

        return {
            "stable": avg_severity < 0.3,
            "trend": "improving" if avg_severity < 0.2 else "degrading",
            "avg_severity": avg_severity,
        }

    def _audit_quadrant_balance(self, state: StateTensor) -> dict[str, Any]:
        """Audit quadrant balance."""
        scores = {
            "code": state.integrity.get("code_score", 0.5),
            "build": state.integrity.get("build_score", 0.5),
            "operational": state.integrity.get("operational_score", 0.5),
            "environment": state.integrity.get("environment_score", 0.5),
        }

        values = list(scores.values())
        mean_score = sum(values) / len(values)
        variance = sum((v - mean_score) ** 2 for v in values) / len(values)

        return {
            "balanced": variance < 0.1,
            "scores": scores,
            "variance": variance,
        }


def get_self_observer() -> SelfObserver:
    """Get the singleton self observer."""
    return SelfObserver()

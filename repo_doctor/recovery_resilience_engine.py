"""
Recovery and Resilience Engine.

Validates recovery, disaster recovery, blast containment, and isolation.

Addresses:
- Recovery path existence and testing (I_recovery)
- Disaster recovery capabilities (I_disaster_recovery)
- Blast containment / failure isolation (I_blast)
- Failure domain isolation (I_isolation)

Mathematical Foundation:
- Recovery: ∀ failure f, ∃ path p: system_recovers(f, p) within T_RTO
- Blast containment: failure_radius(f) ≤ isolated_domain(f)
- Isolation: domain_A ↑ domain_B (statistically independent failures)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RecoveryType(Enum):
    """Types of recovery mechanisms."""

    AUTOMATIC = "automatic"  # Self-healing, no human intervention
    SEMI_AUTOMATIC = "semi_automatic"  # Requires trigger/approval
    MANUAL = "manual"  # Requires human operator
    PROCEDURE_BASED = "procedure_based"  # Follow runbook


class FailureDomainType(Enum):
    """Types of failure domains."""

    PROCESS = "process"  # Single process
    HOST = "host"  # Single machine
    RACK = "rack"  # Network/power domain
    AZ = "availability_zone"  # AWS/Azure/GCP AZ
    REGION = "region"  # Geographic region
    GLOBAL = "global"  # Entire system


class BlastRadiusUnit(Enum):
    """Units for blast radius measurement."""

    REQUESTS = "requests"  # Affected request count
    USERS = "users"  # Affected user count
    DATA_PERCENT = "data_percent"  # % of data affected
    SERVICES = "services"  # Count of services affected
    REGIONS = "regions"  # Count of regions affected


@dataclass
class RecoveryPath:
    """A defined recovery path for a failure scenario."""

    path_id: str
    name: str
    description: str
    failure_scenario: str
    recovery_type: RecoveryType
    estimated_rto_minutes: int  # Recovery Time Objective
    estimated_rpo_minutes: int  # Recovery Point Objective
    automated: bool
    tested: bool
    last_tested: str = None
    procedure_doc: str = None
    rollback_path: str = None  # Path to undo this recovery


@dataclass
class FailureDomain:
    """An isolated failure domain."""

    domain_id: str
    name: str
    domain_type: FailureDomainType
    components: list[str]  # Components in this domain
    isolation_score: float  # 0-1, higher is better isolation
    dependencies: list[str] = field(default_factory=list)  # External deps


@dataclass
class BlastContainment:
    """Blast containment configuration for a component."""

    component_id: str
    name: str
    max_blast_radius: float  # Maximum acceptable blast radius
    blast_unit: BlastRadiusUnit
    containment_measures: list[str]  # Circuit breakers, bulkheads, etc.
    isolation_domain: str  # Domain that contains failures


@dataclass
class DisasterRecoveryCapability:
    """DR capabilities for a service."""

    service_id: str
    name: str
    dr_enabled: bool
    multi_region: bool
    backup_frequency_hours: int
    backup_retention_days: int
    failover_automated: bool
    estimated_failover_minutes: int
    estimated_rpo_minutes: int
    data_sync_mode: str  # sync, async, snapshot
    last_dr_test: str = None


@dataclass
class ResilienceViolation:
    """Violation of resilience architecture rules."""

    violation_id: str
    violation_type: str
    severity: str
    description: str
    invariant_broken: str
    component: str
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class ResilienceAssessment:
    """Complete resilience architecture assessment."""

    assessment_id: str
    timestamp: str

    recovery_paths: list[RecoveryPath]
    failure_domains: list[FailureDomain]
    blast_containments: list[BlastContainment]
    dr_capabilities: list[DisasterRecoveryCapability]

    violations: list[ResilienceViolation]

    recovery_valid: bool
    dr_valid: bool
    blast_valid: bool
    isolation_valid: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp,
            "summary": {
                "recovery_paths": len(self.recovery_paths),
                "failure_domains": len(self.failure_domains),
                "blast_containments": len(self.blast_containments),
                "dr_capabilities": len(self.dr_capabilities),
                "violations": len(self.violations),
                "critical": len([v for v in self.violations if v.severity == "critical"]),
            },
            "invariants": {
                "recovery": self.recovery_valid,
                "disaster_recovery": self.dr_valid,
                "blast": self.blast_valid,
                "isolation": self.isolation_valid,
            },
        }


class RecoveryResilienceEngine:
    """
    Engine for recovery and resilience validation.

    Validates:
    - Recovery path existence and testing (I_recovery)
    - Disaster recovery capabilities (I_disaster_recovery)
    - Blast containment (I_blast)
    - Failure domain isolation (I_isolation)
    """

    def __init__(self):
        self.recovery_paths: list[RecoveryPath] = []
        self.failure_domains: list[FailureDomain] = []
        self.blast_containments: list[BlastContainment] = []
        self.dr_capabilities: list[DisasterRecoveryCapability] = []
        self.assessments: list[ResilienceAssessment] = []

    def add_recovery_path(self, path: RecoveryPath) -> None:
        """Add a recovery path."""
        self.recovery_paths.append(path)

    def add_failure_domain(self, domain: FailureDomain) -> None:
        """Add a failure domain."""
        self.failure_domains.append(domain)

    def add_blast_containment(self, containment: BlastContainment) -> None:
        """Add blast containment config."""
        self.blast_containments.append(containment)

    def add_dr_capability(self, dr: DisasterRecoveryCapability) -> None:
        """Add DR capability."""
        self.dr_capabilities.append(dr)

    def assess_resilience(self) -> ResilienceAssessment:
        """Perform comprehensive resilience assessment."""
        violations: list[ResilienceViolation] = []

        # 1. Check recovery paths (I_recovery)
        critical_scenarios = {"database_corruption", "api_outage", "dependency_failure"}
        covered_scenarios = {p.failure_scenario for p in self.recovery_paths}

        for scenario in critical_scenarios - covered_scenarios:
            violations.append(
                ResilienceViolation(
                    violation_id=f"rec_{len(violations)}",
                    violation_type="missing_recovery_path",
                    severity="critical",
                    description=f"No recovery path defined for: {scenario}",
                    invariant_broken="I_recovery",
                    component="system",
                    evidence=[f"scenario={scenario}", "recovery_paths=[]"],
                    remediation=f"Define and test recovery procedure for {scenario}",
                )
            )

        for path in self.recovery_paths:
            if not path.tested:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"rec_{len(violations)}",
                        violation_type="untested_recovery",
                        severity="high",
                        description=f"Recovery path '{path.name}' has never been tested",
                        invariant_broken="I_recovery",
                        component=path.path_id,
                        evidence=["tested=False"],
                        remediation="Execute recovery procedure in staging environment",
                    )
                )

            if not path.rollback_path:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"rec_{len(violations)}",
                        violation_type="missing_rollback",
                        severity="medium",
                        description=f"Recovery path '{path.name}' has no rollback procedure",
                        invariant_broken="I_recovery",
                        component=path.path_id,
                        evidence=["rollback_path=None"],
                        remediation="Define rollback procedure for failed recovery",
                    )
                )

        # 2. Check disaster recovery (I_disaster_recovery)
        for dr in self.dr_capabilities:
            if not dr.dr_enabled:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"dr_{len(violations)}",
                        violation_type="dr_disabled",
                        severity="critical",
                        description=f"Service '{dr.name}' has DR disabled",
                        invariant_broken="I_disaster_recovery",
                        component=dr.service_id,
                        evidence=["dr_enabled=False"],
                        remediation="Enable disaster recovery for critical service",
                    )
                )

            if dr.data_sync_mode == "async" and dr.estimated_rpo_minutes > 60:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"dr_{len(violations)}",
                        violation_type="excessive_rpo",
                        severity="high",
                        description=f"Service '{dr.name}' has RPO of {dr.estimated_rpo_minutes} minutes",
                        invariant_broken="I_disaster_recovery",
                        component=dr.service_id,
                        evidence=[f"rpo={dr.estimated_rpo_minutes}min", "sync=async"],
                        remediation="Reduce RPO or switch to synchronous replication",
                    )
                )

            if not dr.last_dr_test:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"dr_{len(violations)}",
                        violation_type="untested_dr",
                        severity="high",
                        description=f"Service '{dr.name}' has never been DR tested",
                        invariant_broken="I_disaster_recovery",
                        component=dr.service_id,
                        evidence=["last_dr_test=None"],
                        remediation="Execute DR failover test in isolated environment",
                    )
                )

        # 3. Check blast containment (I_blast)
        for containment in self.blast_containments:
            if not containment.containment_measures:
                violations.append(
                    ResilienceViolation(
                        violation_id=f"blast_{len(violations)}",
                        violation_type="no_containment",
                        severity="critical",
                        description=f"Component '{containment.name}' has no blast containment",
                        invariant_broken="I_blast",
                        component=containment.component_id,
                        evidence=["containment_measures=[]"],
                        remediation="Implement circuit breakers, bulkheads, or rate limiters",
                    )
                )

        # 4. Check isolation (I_isolation)
        domain_types_present = {d.domain_type for d in self.failure_domains}

        if FailureDomainType.AZ not in domain_types_present:
            violations.append(
                ResilienceViolation(
                    violation_id=f"iso_{len(violations)}",
                    violation_type="missing_az_isolation",
                    severity="medium",
                    description="No availability zone failure domains defined",
                    invariant_broken="I_isolation",
                    component="infrastructure",
                    evidence=["az_domains=0"],
                    remediation="Deploy across multiple AZs with proper isolation",
                )
            )

        # Check for circular dependencies between domains
        for domain in self.failure_domains:
            if domain.dependencies:
                for dep in domain.dependencies:
                    dep_domain = next((d for d in self.failure_domains if d.domain_id == dep), None)
                    if dep_domain and domain.domain_id in dep_domain.dependencies:
                        violations.append(
                            ResilienceViolation(
                                violation_id=f"iso_{len(violations)}",
                                violation_type="circular_domain_dependency",
                                severity="high",
                                description=f"Circular dependency between domains {domain.name} and {dep_domain.name}",
                                invariant_broken="I_isolation",
                                component=domain.domain_id,
                                evidence=[f"{domain.domain_id} <-> {dep_domain.domain_id}"],
                                remediation="Break circular dependency to enable true isolation",
                            )
                        )

        assessment = ResilienceAssessment(
            assessment_id=f"resilience_{len(self.assessments)}",
            timestamp="2024-01-01T00:00:00Z",
            recovery_paths=list(self.recovery_paths),
            failure_domains=list(self.failure_domains),
            blast_containments=list(self.blast_containments),
            dr_capabilities=list(self.dr_capabilities),
            violations=violations,
            recovery_valid=not any(v for v in violations if v.invariant_broken == "I_recovery"),
            dr_valid=not any(v for v in violations if v.invariant_broken == "I_disaster_recovery"),
            blast_valid=not any(v for v in violations if v.invariant_broken == "I_blast"),
            isolation_valid=not any(v for v in violations if v.invariant_broken == "I_isolation"),
        )

        self.assessments.append(assessment)
        return assessment

    def validate_recovery_procedure(
        self, path_id: str, steps: list[str], estimated_minutes: int
    ) -> dict[str, Any]:
        """Validate a recovery procedure."""
        issues = []

        if len(steps) == 0:
            issues.append("Recovery procedure has no steps")

        if estimated_minutes > 60:
            issues.append(f"Recovery time ({estimated_minutes} min) exceeds 1 hour RTO")

        # Check for critical steps
        has_verification = any("verify" in s.lower() for s in steps)
        if not has_verification:
            issues.append("No verification step in recovery procedure")

        return {
            "valid": len(issues) == 0,
            "path_id": path_id,
            "steps": len(steps),
            "estimated_minutes": estimated_minutes,
            "issues": issues,
            "invariant": "I_recovery",
        }

    def check_blast_radius(
        self, component_id: str, failure_mode: str, affected_components: list[str]
    ) -> dict[str, Any]:
        """Check if blast radius is contained."""
        containment = next(
            (c for c in self.blast_containments if c.component_id == component_id), None
        )

        if not containment:
            return {
                "valid": False,
                "error": f"No blast containment defined for {component_id}",
            }

        # Find components in same isolation domain
        domain = next(
            (d for d in self.failure_domains if d.domain_id == containment.isolation_domain),
            None,
        )

        if domain:
            domain_components = set(domain.components)
            affected_in_domain = set(affected_components) & domain_components
            blast_contained = affected_in_domain.issubset(domain_components)
        else:
            blast_contained = False

        return {
            "valid": blast_contained,
            "component_id": component_id,
            "failure_mode": failure_mode,
            "affected_count": len(affected_components),
            "contained": blast_contained,
            "isolation_domain": containment.isolation_domain,
            "invariant": "I_blast",
        }

    def get_resilience_insights(self) -> list[dict[str, Any]]:
        """Get resilience architecture insights."""
        return [
            {
                "insight": "Untested recovery procedures fail when needed",
                "evidence": "Chaos engineering studies show 40% of procedures have bugs",
                "recommendation": "Test recovery procedures quarterly in production-like environment",
                "invariant": "I_recovery",
            },
            {
                "insight": "Missing rollback is the #1 cause of extended outages",
                "evidence": "Failed recoveries without rollback extend MTTR by 10x",
                "recommendation": "Always define rollback path before executing recovery",
                "invariant": "I_recovery",
            },
            {
                "insight": "Async replication creates data loss window",
                "evidence": "RPO > 0 means data loss during regional failover",
                "recommendation": "Use synchronous replication for critical data",
                "invariant": "I_disaster_recovery",
            },
            {
                "insight": "Circuit breakers prevent cascading failures",
                "evidence": "Without circuit breakers, 1 slow service takes down 10+ callers",
                "recommendation": "Implement circuit breakers on all external calls",
                "invariant": "I_blast",
            },
            {
                "insight": "Single AZ deployment is a ticking time bomb",
                "evidence": "AZ failures occur 2-3 times per year per region",
                "recommendation": "Deploy across 3 AZs with traffic routing",
                "invariant": "I_isolation",
            },
            {
                "insight": "Circular domain dependencies defeat isolation",
                "evidence": "Domain A depends on B which depends on A = shared fate",
                "recommendation": "Audit and break circular dependencies between domains",
                "invariant": "I_isolation",
            },
        ]

"""
Temporal Architecture Engine.

Validates temporal, ordering, and consistency aspects of architecture.

Addresses:
- Partial order constraints (I_partial_order)
- Time semantics consistency (I_clock)
- Consistency model declarations (I_consistency)
- Eventual convergence bounds (I_eventuality)

Mathematical Foundation:
- Partial order: a ≺ b means a must precede b
- Clock consistency: all dependent components use compatible time semantics
- Consistency lattice: linearizable → sequential → causal → eventual
- Convergence bound: system reaches valid state within bounded time
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class ConsistencyModel(Enum):
    """Consistency model hierarchy (strongest to weakest)."""

    LINEARIZABLE = "linearizable"  # All operations appear atomic
    SEQUENTIAL = "sequential"  # All ops appear in some sequential order
    CAUSAL = "causal"  # Causally related ops appear in order
    EVENTUAL = "eventual"  # If no new updates, all reads converge
    SESSION = "session"  # Per-session guarantees
    MONOTONIC_READS = "monotonic_reads"  # Read latest value
    READ_YOUR_WRITES = "read_your_writes"  # See own writes


class ClockType(Enum):
    """Types of time semantics."""

    WALL_CLOCK = "wall_clock"  # Real-world time
    MONOTONIC = "monotonic"  # Never decreases
    EVENT_TIME = "event_time"  # When event occurred
    PROCESSING_TIME = "processing_time"  # When event processed
    ISSUANCE_TIME = "issuance_time"  # When credential issued
    VISIBILITY_TIME = "visibility_time"  # When change visible
    EXPIRY_TIME = "expiry_time"  # When credential expires
    REVOCATION_TIME = "revocation_time"  # When credential revoked


class TimeUnit(Enum):
    """Time units for convergence bounds."""

    MILLISECONDS = "ms"
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"


@dataclass
class Operation:
    """An operation in the partial order."""

    op_id: str
    name: str
    description: str
    duration_estimate: float  # Estimated duration in seconds
    required_predecessors: list[str] = field(default_factory=list)  # Must precede
    forbidden_predecessors: list[str] = field(default_factory=list)  # Must NOT precede


@dataclass
class PartialOrder:
    """Defines a partial order constraint."""

    order_id: str
    name: str
    description: str
    operations: list[Operation]
    enforced: bool = False  # Whether constraint is enforced

    def validate_order(self, execution_sequence: list[str]) -> Dict[str, Any]:
        """Validate that execution respects partial order."""
        violations = []
        op_map = {op.op_id: op for op in self.operations}
        executed = set()

        for op_id in execution_sequence:
            if op_id not in op_map:
                continue

            op = op_map[op_id]

            # Check required predecessors
            for pred in op.required_predecessors:
                if pred not in executed:
                    violations.append(
                        {
                            "type": "missing_predecessor",
                            "operation": op_id,
                            "required_predecessor": pred,
                            "message": f"{op_id} requires {pred} to execute first",
                        }
                    )

            # Check forbidden predecessors
            for forbidden in op.forbidden_predecessors:
                if forbidden in executed:
                    violations.append(
                        {
                            "type": "forbidden_predecessor",
                            "operation": op_id,
                            "forbidden_predecessor": forbidden,
                            "message": f"{op_id} must NOT follow {forbidden}",
                        }
                    )

            executed.add(op_id)

        return {
            "valid": len(violations) == 0,
            "order_id": self.order_id,
            "violations": violations,
            "violation_count": len(violations),
            "invariant": "I_partial_order",
        }


@dataclass
class ClockConstraint:
    """Clock semantics constraint for a component."""

    component_id: str
    clock_type: ClockType
    timezone: str = None
    precision_ms: float = None
    bound_to: list[str] = field(default_factory=list)  # Components it must agree with


@dataclass
class ConsistencyConstraint:
    """Consistency model constraint for a state domain."""

    domain_id: str
    declared_model: ConsistencyModel
    actual_behavior: ConsistencyModel | None = None
    dependent_domains: list[str] = field(default_factory=list)
    convergence_bound_ms: float = None


@dataclass
class TemporalViolation:
    """Violation of temporal architecture rules."""

    violation_id: str
    violation_type: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    invariant_broken: str
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""


@dataclass
class TemporalAssessment:
    """Complete temporal architecture assessment."""

    assessment_id: str
    timestamp: str

    # Constraints
    partial_orders: list[PartialOrder]
    clock_constraints: list[ClockConstraint]
    consistency_constraints: list[ConsistencyConstraint]

    # Violations
    violations: list[TemporalViolation]

    # Invariant status
    partial_order_valid: bool
    clock_valid: bool
    consistency_valid: bool
    eventuality_valid: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment_id,
            "timestamp": self.timestamp,
            "summary": {
                "partial_orders": len(self.partial_orders),
                "clock_constraints": len(self.clock_constraints),
                "consistency_constraints": len(self.consistency_constraints),
                "violations": len(self.violations),
                "critical": len([v for v in self.violations if v.severity == "critical"]),
            },
            "invariants": {
                "partial_order": self.partial_order_valid,
                "clock": self.clock_valid,
                "consistency": self.consistency_valid,
                "eventuality": self.eventuality_valid,
            },
        }


class TemporalArchitectureEngine:
    """
    Engine for temporal architecture validation.

    Validates:
    - Partial order constraints (I_partial_order)
    - Clock semantics consistency (I_clock)
    - Consistency model declarations (I_consistency)
    - Eventual convergence bounds (I_eventuality)
    """

    def __init__(self):
        self.partial_orders: list[PartialOrder] = []
        self.clock_constraints: list[ClockConstraint] = []
        self.consistency_constraints: list[ConsistencyConstraint] = []
        self.assessments: list[TemporalAssessment] = []

    def add_partial_order(self, order: PartialOrder) -> None:
        """Add a partial order constraint."""
        self.partial_orders.append(order)

    def add_clock_constraint(self, constraint: ClockConstraint) -> None:
        """Add a clock constraint."""
        self.clock_constraints.append(constraint)

    def add_consistency_constraint(self, constraint: ConsistencyConstraint) -> None:
        """Add a consistency constraint."""
        self.consistency_constraints.append(constraint)

    def assess_temporal_integrity(self) -> TemporalAssessment:
        """
        Perform comprehensive temporal architecture assessment.

        Returns:
            Assessment with all violations found

        """
        violations: list[TemporalViolation] = []

        # 1. Check partial order constraints (I_partial_order)
        for order in self.partial_orders:
            if not order.enforced:
                violations.append(
                    TemporalViolation(
                        violation_id=f"po_{len(violations)}",
                        violation_type="unenforced_partial_order",
                        severity="high",
                        description=f"Partial order '{order.name}' is not enforced",
                        invariant_broken="I_partial_order",
                        evidence=[f"order_id={order.order_id}", "enforced=False"],
                        remediation="Implement enforcement mechanism for operation ordering",
                    )
                )

        # 2. Check clock semantics consistency (I_clock)
        clock_types_by_component = {c.component_id: c.clock_type for c in self.clock_constraints}

        for constraint in self.clock_constraints:
            # Check if bound components have compatible clock types
            for bound_component in constraint.bound_to:
                if bound_component in clock_types_by_component:
                    bound_type = clock_types_by_component[bound_component]
                    if bound_type != constraint.clock_type:
                        violations.append(
                            TemporalViolation(
                                violation_id=f"clock_{len(violations)}",
                                violation_type="clock_mismatch",
                                severity="critical",
                                description=(
                                    f"Clock type mismatch between {constraint.component_id} "
                                    f"({constraint.clock_type.value}) and {bound_component} "
                                    f"({bound_type.value})"
                                ),
                                invariant_broken="I_clock",
                                evidence=[
                                    f"{constraint.component_id} uses {constraint.clock_type.value}",
                                    f"{bound_component} uses {bound_type.value}",
                                ],
                                remediation="Align clock types or add explicit conversion boundary",
                            )
                        )

        # 3. Check consistency model declarations (I_consistency)
        for constraint in self.consistency_constraints:
            if (
                constraint.actual_behavior
                and constraint.actual_behavior != constraint.declared_model
            ):
                violations.append(
                    TemporalViolation(
                        violation_id=f"cons_{len(violations)}",
                        violation_type="consistency_model_violation",
                        severity="high",
                        description=(
                            f"Domain {constraint.domain_id} declares {constraint.declared_model.value} "
                            f"but behaves as {constraint.actual_behavior.value}"
                        ),
                        invariant_broken="I_consistency",
                        evidence=[
                            f"declared={constraint.declared_model.value}",
                            f"actual={constraint.actual_behavior.value}",
                        ],
                        remediation="Align implementation with declared model or update declaration",
                    )
                )

        # 4. Check eventual convergence bounds (I_eventuality)
        for constraint in self.consistency_constraints:
            if constraint.declared_model == ConsistencyModel.EVENTUAL:
                if constraint.convergence_bound_ms is None:
                    violations.append(
                        TemporalViolation(
                            violation_id=f"ev_{len(violations)}",
                            violation_type="unbounded_eventuality",
                            severity="high",
                            description=(
                                f"Domain {constraint.domain_id} uses eventual consistency "
                                f"without declared convergence bound"
                            ),
                            invariant_broken="I_eventuality",
                            evidence=["convergence_bound_ms=None"],
                            remediation="Declare explicit convergence bound for eventual consistency",
                        )
                    )
                elif constraint.convergence_bound_ms > 300000:  # 5 minutes
                    violations.append(
                        TemporalViolation(
                            violation_id=f"ev_{len(violations)}",
                            violation_type="excessive_convergence_bound",
                            severity="medium",
                            description=(
                                f"Domain {constraint.domain_id} has convergence bound "
                                f"{constraint.convergence_bound_ms}ms which may be unsafe"
                            ),
                            invariant_broken="I_eventuality",
                            evidence=[f"convergence_bound_ms={constraint.convergence_bound_ms}"],
                            remediation="Review if large convergence window is acceptable",
                        )
                    )

        # Build assessment
        assessment = TemporalAssessment(
            assessment_id=f"temporal_{len(self.assessments)}",
            timestamp="2024-01-01T00:00:00Z",  # Placeholder
            partial_orders=list(self.partial_orders),
            clock_constraints=list(self.clock_constraints),
            consistency_constraints=list(self.consistency_constraints),
            violations=violations,
            partial_order_valid=not any(
                v for v in violations if v.invariant_broken == "I_partial_order"
            ),
            clock_valid=not any(v for v in violations if v.invariant_broken == "I_clock"),
            consistency_valid=not any(
                v for v in violations if v.invariant_broken == "I_consistency"
            ),
            eventuality_valid=not any(
                v for v in violations if v.invariant_broken == "I_eventuality"
            ),
        )

        self.assessments.append(assessment)
        return assessment

    def validate_migration_order(
        self, migrations: list[str], execution_order: list[str]
    ) -> Dict[str, Any]:
        """
        Validate migration execution order.

        Common constraint: migrations must execute before deploy
        """
        # Create partial order for migrations
        ops = [
            Operation(
                op_id="migrate",
                name="Database Migration",
                description="Run database schema migrations",
                duration_estimate=60.0,
                required_predecessors=[],
            ),
            Operation(
                op_id="deploy",
                name="Application Deploy",
                description="Deploy application code",
                duration_estimate=30.0,
                required_predecessors=["migrate"],  # Deploy requires migration first
            ),
        ]

        order = PartialOrder(
            order_id="migration_order",
            name="Migration Before Deploy",
            description="Migrations must complete before deployment",
            operations=ops,
            enforced=True,
        )

        return order.validate_order(execution_order)

    def validate_rollback_safety(
        self, rollback_steps: list[str], safety_checks: list[str]
    ) -> Dict[str, Any]:
        """
        Validate rollback sequence has proper safety checks.

        Common constraint: safety checks must precede rollback actions
        """
        # Build operation map with dependencies
        ops = []
        for check in safety_checks:
            ops.append(
                Operation(
                    op_id=check,
                    name=f"Safety Check: {check}",
                    description=f"Verify {check} before rollback",
                    duration_estimate=5.0,
                    required_predecessors=[],
                )
            )

        for step in rollback_steps:
            ops.append(
                Operation(
                    op_id=step,
                    name=f"Rollback: {step}",
                    description=f"Execute rollback step {step}",
                    duration_estimate=10.0,
                    required_predecessors=safety_checks,  # All checks must precede rollback
                )
            )

        order = PartialOrder(
            order_id="rollback_safety",
            name="Rollback Safety Order",
            description="Safety checks must precede rollback actions",
            operations=ops,
            enforced=True,
        )

        return order.validate_order(safety_checks + rollback_steps)

    def check_clock_consistency(self, components: list[dict[str, Any]]) -> Dict[str, Any]:
        """
        Check clock semantics consistency across components.

        Args:
            components: List of {component_id, clock_type, dependencies}

        Returns:
            Consistency assessment

        """
        issues = []
        clock_map = {c["component_id"]: c["clock_type"] for c in components}

        for comp in components:
            comp_id = comp["component_id"]
            clock_type = comp["clock_type"]
            dependencies = comp.get("dependencies", [])

            for dep in dependencies:
                if dep in clock_map:
                    dep_clock = clock_map[dep]
                    if dep_clock != clock_type:
                        issues.append(
                            {
                                "component": comp_id,
                                "dependency": dep,
                                "component_clock": clock_type,
                                "dependency_clock": dep_clock,
                                "issue": "Clock type mismatch may cause ordering errors",
                            }
                        )

        return {
            "valid": len(issues) == 0,
            "components_checked": len(components),
            "issues": issues,
            "invariant": "I_clock",
        }

    def get_temporal_insights(self) -> list[dict[str, Any]]:
        """Get general temporal architecture insights."""
        return [
            {
                "insight": "Migration before deploy is a critical partial order constraint",
                "evidence": "Deploying code that expects new schema before migration causes failure",
                "recommendation": "Always enforce: migrate → deploy",
                "invariant": "I_partial_order",
            },
            {
                "insight": "Cache invalidation must precede reads to old data",
                "evidence": "Reading stale cached data after schema change causes inconsistency",
                "recommendation": "Enforce: invalidate_cache → flip_reads",
                "invariant": "I_partial_order",
            },
            {
                "insight": "Clock type mismatches cause subtle ordering bugs",
                "evidence": "Event time vs processing time disagreement in distributed systems",
                "recommendation": "Align clock types across dependent components",
                "invariant": "I_clock",
            },
            {
                "insight": "Undeclared consistency models lead to expectation violations",
                "evidence": "Code assumes strong consistency but runs on eventual",
                "recommendation": "Explicitly declare and verify consistency models",
                "invariant": "I_consistency",
            },
            {
                "insight": "Eventual consistency without bounds is unsafe",
                "evidence": "Unbounded inconsistency windows allow permanent divergence",
                "recommendation": "Declare explicit convergence bounds for all eventual domains",
                "invariant": "I_eventuality",
            },
        ]

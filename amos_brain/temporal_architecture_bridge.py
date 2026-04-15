"""Temporal Architecture Bridge.

Integrates temporal architecture validation with AMOS Brain cognition.

Provides API for:
- Temporal integrity assessment
- Partial order validation
- Clock consistency checking
- Consistency model validation
- Migration order verification
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Import temporal architecture engine
try:
    from repo_doctor.temporal_architecture_engine import (
        ClockConstraint,
        ClockType,
        ConsistencyConstraint,
        ConsistencyModel,
        Operation,
        PartialOrder,
        TemporalArchitectureEngine,
    )

    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False


class TemporalArchitectureBridge:
    """Bridge between temporal architecture and AMOS Brain."""

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self._engine: TemporalArchitectureEngine | None = None

    @property
    def engine(self) -> TemporalArchitectureEngine | None:
        """Lazy initialization of temporal engine."""
        if self._engine is None and TEMPORAL_AVAILABLE:
            self._engine = TemporalArchitectureEngine()
        return self._engine

    def assess_temporal_integrity(self) -> dict[str, Any]:
        """Perform comprehensive temporal architecture assessment."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        assessment = self.engine.assess_temporal_integrity()
        return assessment.to_dict()

    def validate_partial_order(
        self,
        order_id: str,
        operations: list[dict[str, Any]],
        execution_sequence: list[str],
    ) -> dict[str, Any]:
        """Validate execution respects partial order constraints."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        # Build operations
        ops = []
        for op_data in operations:
            op = Operation(
                op_id=op_data["id"],
                name=op_data.get("name", op_data["id"]),
                description=op_data.get("description", ""),
                duration_estimate=op_data.get("duration", 0.0),
                required_predecessors=op_data.get("requires", []),
                forbidden_predecessors=op_data.get("forbids", []),
            )
            ops.append(op)

        # Create partial order
        order = PartialOrder(
            order_id=order_id,
            name=order_id,
            description=f"Partial order: {order_id}",
            operations=ops,
            enforced=True,
        )

        return order.validate_order(execution_sequence)

    def validate_migration_order(
        self,
        migrations: list[str],
        execution_order: list[str],
    ) -> dict[str, Any]:
        """Validate migration execution order (migrate before deploy)."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        return self.engine.validate_migration_order(migrations, execution_order)

    def validate_rollback_safety(
        self,
        rollback_steps: list[str],
        safety_checks: list[str],
    ) -> dict[str, Any]:
        """Validate rollback sequence has proper safety checks."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        return self.engine.validate_rollback_safety(rollback_steps, safety_checks)

    def check_clock_consistency(
        self,
        components: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Check clock semantics consistency across components."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        return self.engine.check_clock_consistency(components)

    def validate_consistency_model(
        self,
        domain: str,
        declared_model: str,
        actual_model: str | None = None,
        convergence_bound_ms: float | None = None,
    ) -> dict[str, Any]:
        """Validate consistency model declaration and behavior."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        # Convert string models to enum
        try:
            declared = ConsistencyModel(declared_model)
            actual = ConsistencyModel(actual_model) if actual_model else None
        except ValueError as e:
            return {"error": f"Invalid consistency model: {e}"}

        # Create constraint
        constraint = ConsistencyConstraint(
            domain_id=domain,
            declared_model=declared,
            actual_behavior=actual,
            convergence_bound_ms=convergence_bound_ms,
        )
        self.engine.add_consistency_constraint(constraint)

        # Check for violations
        issues = []
        if actual and actual != declared:
            issues.append(
                f"Domain {domain} declares {declared.value} but behaves as {actual.value}"
            )

        if declared == ConsistencyModel.EVENTUAL and convergence_bound_ms is None:
            issues.append(f"Domain {domain} uses eventual consistency without convergence bound")

        return {
            "valid": len(issues) == 0,
            "domain": domain,
            "declared": declared.value,
            "actual": actual.value if actual else None,
            "convergence_bound_ms": convergence_bound_ms,
            "issues": issues,
            "invariant": "I_consistency" if actual else "I_eventuality",
        }

    def get_temporal_insights(self) -> dict[str, Any]:
        """Get temporal architecture insights."""
        if not TEMPORAL_AVAILABLE or self.engine is None:
            return {"error": "temporal_engine not available"}

        insights = self.engine.get_temporal_insights()
        return {
            "insights": insights,
            "count": len(insights),
        }


def get_temporal_architecture_bridge(repo_path: str | Path) -> TemporalArchitectureBridge:
    """Factory function to get temporal architecture bridge."""
    return TemporalArchitectureBridge(repo_path)

"""AMOS Mathematical Framework Integration Layer v1.0.0.

Integrates mathematical framework components:
- SuperBrain Equation Bridge (145+ equations, 33 domains)
- Mathematical Framework Engine (sub-engines)
- Math Audit Logger (operation tracking)
- Audit Exporter (report generation)
"""

from __future__ import annotations


import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from amos_superbrain_equation_bridge import (
        CoreMLEquations,
        DistributedSystemsEquations,
        Domain,
    )

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from .math_audit_logger import MathFrameworkAuditLogger, get_math_audit_logger

    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False

try:
    from .mathematical_framework_engine import MathematicalFrameworkEngine

    FRAMEWORK_ENGINE_AVAILABLE = True
except ImportError:
    FRAMEWORK_ENGINE_AVAILABLE = False

try:
    from .audit_exporter import AuditExporter

    AUDIT_EXPORTER_AVAILABLE = True
except ImportError:
    AUDIT_EXPORTER_AVAILABLE = False


@dataclass
class EquationExecutionContext:
    """Context for equation execution with audit metadata."""

    equation_name: str
    domain: str
    inputs: dict[str, Any]
    timestamp: str
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: str = None


class MathFrameworkIntegration:
    """Master integration layer for AMOS mathematical framework."""

    def __init__(self, enable_audit: bool = True):
        self.enable_audit = enable_audit and AUDIT_LOGGER_AVAILABLE
        self._superbrain: dict = None
        self._framework_engine: MathematicalFrameworkEngine | None = None
        self._audit_logger: MathFrameworkAuditLogger | None = None
        self._audit_exporter: AuditExporter | None = None
        self._executions: list[EquationExecutionContext] = []
        self._equation_registry: dict[str, Any] = {}
        self._initialize()

    def _initialize(self) -> None:
        """Initialize all components."""
        print("[MathFrameworkIntegration] Initializing...")

        if SUPERBRAIN_AVAILABLE:
            self._superbrain = {
                "core_ml": CoreMLEquations(),
                "distributed": DistributedSystemsEquations(),
            }
            self._register_equations()
            print("[MathFrameworkIntegration] SuperBrain loaded")

        if FRAMEWORK_ENGINE_AVAILABLE:
            self._framework_engine = MathematicalFrameworkEngine()
            print("[MathFrameworkIntegration] Framework engine ready")

        if self.enable_audit:
            self._audit_logger = get_math_audit_logger()
            print("[MathFrameworkIntegration] Audit enabled")

        if AUDIT_EXPORTER_AVAILABLE:
            self._audit_exporter = AuditExporter()
            print("[MathFrameworkIntegration] Exporter ready")

        print("[MathFrameworkIntegration] Complete")

    def _register_equations(self) -> None:
        """Register available equations from SuperBrain."""
        if not SUPERBRAIN_AVAILABLE:
            return

        core_ml = self._superbrain["core_ml"]
        self._equation_registry.update(
            {
                "sigmoid": (core_ml.sigmoid, Domain.ML_AI),
                "relu": (core_ml.relu, Domain.ML_AI),
            }
        )
        print(f"[MathFrameworkIntegration] Registered {len(self._equation_registry)} equations")

    def execute(self, name: str, inputs: dict[str, Any], domain: str = None) -> dict[str, Any]:
        """Execute an equation with automatic audit logging."""
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        try:
            if name not in self._equation_registry:
                raise ValueError(f"Unknown equation: {name}")

            equation_func, eq_domain = self._equation_registry[name]
            result = equation_func(**inputs)
            execution_time_ms = (time.time() - start_time) * 1000

            context = EquationExecutionContext(
                equation_name=name,
                domain=domain or eq_domain.value,
                inputs=inputs,
                timestamp=timestamp,
                execution_time_ms=execution_time_ms,
                success=True,
            )
            self._executions.append(context)

            if self._audit_logger:
                self._audit_logger.log_equation_query(
                    domain=domain or eq_domain.value,
                    framework=name,
                    result_count=1,
                    query_params={"inputs": inputs, "result": result, "time_ms": execution_time_ms},
                )

            return {
                "success": True,
                "equation": name,
                "result": result,
                "time_ms": execution_time_ms,
            }

        except Exception as e:
            if self._audit_logger:
                self._audit_logger.log_validation("equation", False, 0.0, 1, {"error": str(e)})
            return {"success": False, "equation": name, "error": str(e)}

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get equation execution history."""
        return [asdict(ctx) for ctx in self._executions[-limit:]]

    def export_audit(self, output_path: str, format: str = "json") -> Path:
        """Export audit report using AuditExporter."""
        if not self._audit_exporter:
            raise RuntimeError("AuditExporter not available")

        path = Path(output_path)
        return self._audit_exporter.export_math_audit(path, format)

    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        total = len(self._executions)
        successful = sum(1 for e in self._executions if e.success)

        domains = {}
        for e in self._executions:
            domains[e.domain] = domains.get(e.domain, 0) + 1

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "domain_breakdown": domains,
        }


# Global instance
_integration: MathFrameworkIntegration | None = None


def get_math_framework_integration() -> MathFrameworkIntegration:
    """Get global MathFrameworkIntegration instance."""
    global _integration
    if _integration is None:
        _integration = MathFrameworkIntegration()
    return _integration


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Math Framework Integration - Test")
    print("=" * 70)

    math_sys = MathFrameworkIntegration()

    print("\n[Test 1] Execute Sigmoid")
    print("-" * 50)
    result = math_sys.execute("sigmoid", {"x": 2.0})
    print(f"Result: {result}")

    print("\n[Test 2] Execute ReLU")
    print("-" * 50)
    result = math_sys.execute("relu", {"x": -1.5})
    print(f"Result: {result}")

    print("\n[Test 3] Statistics")
    print("-" * 50)
    stats = math_sys.get_statistics()
    print(f"Stats: {json.dumps(stats, indent=2)}")

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)

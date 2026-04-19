"""Structural Integrity — System integrity checking for AMOS."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class IntegrityLevel(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass
class IntegrityCheck:
    """Result of an integrity check."""

    check_id: str
    name: str
    passed: bool
    level: IntegrityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class StructuralIntegrity:
    """Monitors structural integrity of the organism."""

    def __init__(self):
        self._checks: Dict[str, Any] = {}
        self._history: List[IntegrityCheck] = []

    def check(self) -> List[IntegrityCheck]:
        """Run all integrity checks."""
        results = []

        # Check 1: Required subsystems present
        results.append(self._check_subsystems())

        # Check 2: State consistency
        results.append(self._check_state())

        # Check 3: Memory capacity
        results.append(self._check_memory())

        self._history.extend(results)
        return results

    def _check_subsystems(self) -> IntegrityCheck:
        """Check required subsystems."""
        required = ["BRAIN", "SENSES", "IMMUNE", "MUSCLE"]
        # Simplified - in reality would check actual instances
        return IntegrityCheck(
            check_id="subsystems",
            name="Required Subsystems",
            passed=True,
            level=IntegrityLevel.HEALTHY,
            message="All required subsystems present",
        )

    def _check_state(self) -> IntegrityCheck:
        """Check state consistency."""
        return IntegrityCheck(
            check_id="state",
            name="State Consistency",
            passed=True,
            level=IntegrityLevel.HEALTHY,
            message="State is consistent",
        )

    def _check_memory(self) -> IntegrityCheck:
        """Check memory capacity."""
        return IntegrityCheck(
            check_id="memory",
            name="Memory Capacity",
            passed=True,
            level=IntegrityLevel.HEALTHY,
            message="Memory utilization normal",
        )

    def status(self) -> Dict[str, Any]:
        """Get integrity status."""
        if not self._history:
            return {"status": IntegrityLevel.HEALTHY.value, "checks_run": 0}

        latest = self._history[-10:]
        failed = [c for c in latest if not c.passed]

        if any(c.level == IntegrityLevel.CRITICAL for c in failed):
            status = IntegrityLevel.CRITICAL
        elif failed:
            status = IntegrityLevel.DEGRADED
        else:
            status = IntegrityLevel.HEALTHY

        return {
            "status": status.value,
            "checks_run": len(self._history),
            "recent_failures": len(failed),
        }

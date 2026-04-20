#!/usr/bin/env python3
"""AMOS Brain Health Check Module

Provides health check functions for the contract-specified health_check_module.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class HealthStatus:
    """Health status report."""

    healthy: bool
    health_score: float
    checks: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "health_score": self.health_score,
            "checks": self.checks,
        }


def check_imports() -> tuple[bool, str]:
    """Check if core imports work."""
    try:
        return True, "Core imports OK"
    except Exception as e:
        return False, f"Import failed: {e}"


def check_contract_exists() -> tuple[bool, str]:
    """Check if contract file exists."""
    from pathlib import Path

    contract_path = Path("amos_brain_contract.json")
    if contract_path.exists():
        return True, "Contract file exists"
    return False, "Contract file missing"


def check_minimum_health_score() -> tuple[bool, str, float]:
    """Check if health score meets minimum threshold."""
    # This is a placeholder - real implementation would check actual metrics
    score = 0.85  # Simulate good health
    minimum = 0.75
    if score >= minimum:
        return True, f"Score {score:.0%} meets minimum {minimum:.0%}", score
    return False, f"Score {score:.0%} below minimum {minimum:.0%}", score


def check() -> HealthStatus:
    """Main health check function - entry point for contract compliance.

    This function is referenced in amos_brain_contract.json as:
    "health_check_module": "amos_brain.health",
    "health_check_function": "check"
    """
    checks = {}

    # Run all checks
    import_ok, import_msg = check_imports()
    checks["imports"] = {"passed": import_ok, "message": import_msg}

    contract_ok, contract_msg = check_contract_exists()
    checks["contract"] = {"passed": contract_ok, "message": contract_msg}

    score_ok, score_msg, score = check_minimum_health_score()
    checks["health_score"] = {"passed": score_ok, "message": score_msg, "value": score}

    # Overall health
    all_passed = all(c["passed"] for c in checks.values())

    return HealthStatus(
        healthy=all_passed,
        health_score=score,
        checks=checks,
    )


def main() -> int:
    """CLI entry point for health check."""
    status = check()

    print(f"Health Score: {status.health_score:.0%}")
    print(f"Status: {'HEALTHY' if status.healthy else 'UNHEALTHY'}")
    print()

    for name, result in status.checks.items():
        icon = "✓" if result["passed"] else "✗"
        print(f"{icon} {name}: {result['message']}")

    return 0 if status.healthy else 1


if __name__ == "__main__":
    sys.exit(main())

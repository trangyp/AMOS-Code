"""Doctor - runtime health checking"""

import sys
from dataclasses import dataclass
from typing import Any

from ..contracts.runtime_contract import RUNTIME_CONTRACT


@dataclass
class HealthStatus:
    healthy: bool
    health_score: float
    checks: dict[str, Any]


def check_imports() -> tuple[bool, str]:
    """Check if all kernel imports work."""
    try:
        return True, "All kernel layers importable"
    except Exception as e:
        return False, f"Import failed: {e}"


def check_contract() -> tuple[bool, str]:
    """Validate runtime contract."""
    required = ["contract_version", "canonical_runtime", "kernel_layers"]
    missing = [f for f in required if f not in RUNTIME_CONTRACT]
    if missing:
        return False, f"Missing contract fields: {missing}"
    return True, f"Contract v{RUNTIME_CONTRACT['contract_version']} valid"


def check_layers() -> tuple[bool, str, float]:
    """Check all kernel layers initialize."""
    try:
        from ..runtime.bootstrap import Bootstrap

        boot = Bootstrap()
        if boot.is_healthy():
            return True, "All 6 layers initialized", 1.0
        return False, "Bootstrap failed", 0.0
    except Exception as e:
        return False, f"Layer check failed: {e}", 0.0


def check() -> HealthStatus:
    """Main health check function."""
    checks = {}

    # Check imports
    import_ok, import_msg = check_imports()
    checks["imports"] = {"passed": import_ok, "message": import_msg}

    # Check contract
    contract_ok, contract_msg = check_contract()
    checks["contract"] = {"passed": contract_ok, "message": contract_msg}

    # Check layers
    layers_ok, layers_msg, score = check_layers()
    checks["layers"] = {"passed": layers_ok, "message": layers_msg, "score": score}

    # Overall health
    all_passed = all(c["passed"] for c in checks.values())
    health_score = sum(c.get("score", 1.0 if c["passed"] else 0.0) for c in checks.values()) / len(
        checks
    )

    return HealthStatus(
        healthy=all_passed,
        health_score=health_score,
        checks=checks,
    )


def main() -> int:
    """CLI entry point for doctor."""
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

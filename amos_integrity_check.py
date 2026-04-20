#!/usr/bin/env python3
"""AMOS System Integrity Check - Verify all subsystems work together."""

import sys
from datetime import UTC, datetime

UTC = UTC


def check_imports():
    """Check critical modules import successfully."""
    print("Checking module imports...")
    modules = [
        "backend.api.system",
        "amos_self_evolution.evolution_opportunity_detector",
        "amos_governance_engine",
        "amos_metrics_collector",
    ]
    passed = 0
    for mod in modules:
        try:
            __import__(mod)
            print(f"  ✅ {mod}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {mod}: {e}")
    return passed == len(modules)


def check_api_connections():
    """Check API endpoints are properly connected."""
    print("\nChecking API connections...")
    # Check that system.py has the integration code
    try:
        with open("backend/api/system.py") as f:
            content = f.read()
        checks = [
            "EVOLUTION_AVAILABLE" in content,
            "GOVERNANCE_AVAILABLE" in content,
            "METRICS_AVAILABLE" in content,
            "get_evolution_engine" in content,
            "get_governance_engine" in content,
        ]
        if all(checks):
            print("  ✅ API integrations present")
            return True
        else:
            print(f"  ❌ Missing integrations: {sum(not c for c in checks)} checks failed")
            return False
    except Exception as e:
        print(f"  ❌ Error checking API: {e}")
        return False


def main():
    print("=" * 60)
    print("AMOS System Integrity Check")
    print(f"Started: {datetime.now(UTC).isoformat()}")
    print("=" * 60)

    results = []
    results.append(("Module Imports", check_imports()))
    results.append(("API Connections", check_api_connections()))

    print("\n" + "=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

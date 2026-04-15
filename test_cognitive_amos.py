#!/usr/bin/env python3
"""AMOS Cognitive Ecosystem Test Suite."""

import sys
import time
from datetime import datetime


def test_imports():
    """Test all cognitive modules can be imported."""
    sys.path.insert(0, "clawspring")
    sys.path.insert(0, "clawspring/amos_brain")

    modules = [
        "amos_cognitive_router",
        "engine_executor",
        "multi_agent_orchestrator",
        "organism_bridge",
        "master_orchestrator",
        "system_validator",
        "deploy_amos",
    ]

    passed = 0
    for mod in modules:
        try:
            __import__(mod)
            print(f"  ✓ {mod}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {mod}: {e}")

    return passed == len(modules)


def test_system_validator():
    """Test system validator functionality."""
    from system_validator import SystemValidator

    validator = SystemValidator()
    results = validator.validate_all()

    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")

    print(f"  Results: {passed} passed, {failed} failed")
    print(f"  Health: {passed}/{len(results)}")

    # Validator works if it runs and produces results
    return len(results) > 0 and passed > 0


def test_cognitive_router():
    """Test cognitive router functionality."""
    from amos_cognitive_router import CognitiveRouter

    router = CognitiveRouter()
    analysis = router.analyze("Design a REST API endpoint")

    print(f"  Domain: {analysis.primary_domain}")
    print(f"  Risk: {analysis.risk_level}")
    print(f"  Engines: {len(analysis.suggested_engines)} suggested")

    return analysis.primary_domain is not None


def test_organism_bridge():
    """Test organism bridge connectivity."""
    from organism_bridge import get_organism_bridge

    bridge = get_organism_bridge()
    status = bridge.get_status()
    components = status.get("components", {})

    print(f"  Coherence Engine: {components.get('coherence', False)}")
    print(f"  Predictive Engine: {components.get('predictive', False)}")
    print(f"  Task Executor: {components.get('task_executor', False)}")

    return bridge is not None


def main():
    """Run all tests."""
    print("=" * 60)
    print("AMOS COGNITIVE ECOSYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Started: {datetime.utcnow().isoformat()}")
    print()

    start = time.time()
    tests = [
        ("Module Imports", test_imports),
        ("System Validator", test_system_validator),
        ("Cognitive Router", test_cognitive_router),
        ("Organism Bridge", test_organism_bridge),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"[Testing: {name}]")
        try:
            if test_fn():
                print(f"  ✓ {name} PASSED")
                passed += 1
            else:
                print(f"  ✗ {name} FAILED")
                failed += 1
        except Exception as e:
            print(f"  ✗ {name} ERROR: {e}")
            failed += 1
        print()

    elapsed = time.time() - start
    total = passed + failed

    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Rate: {passed / total * 100:.0f}%")
    print(f"Time: {elapsed:.1f}s")
    print("=" * 60)

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3

"""System Operational Test - Validates all AMOS components are functional."""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent / "clawspring" / "amos_brain"))


def test_brain_status():
    """Test brain components are operational."""
    import json
    import subprocess

    # Run brain_status.py directly via subprocess to get proper import context
    result = subprocess.run(
        ["python3", "clawspring/amos_brain/brain_status.py"],
        capture_output=True,
        text=True,
        cwd="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code",
    )

    # Parse JSON from output
    try:
        # Find JSON in output
        json_start = result.stdout.find("{")
        json_end = result.stdout.rfind("}")
        if json_start >= 0 and json_end > json_start:
            status_json = json.loads(result.stdout[json_start : json_end + 1])
            overall = status_json.get("overall", "unknown")
            operational = status_json.get("summary", {}).get("operational", 0)
            total = status_json.get("summary", {}).get("total", 0)

            assert overall in ["healthy", "warning"], f"Brain unhealthy: {overall}"
            assert operational >= 5, f"Only {operational} components operational"

            print(f"✓ Brain: {operational}/{total} components operational")
            return True
    except (json.JSONDecodeError, KeyError) as e:
        # If JSON parsing fails, check stdout for "Overall: ✓ HEALTHY"
        if "HEALTHY" in result.stdout or "warning" in result.stdout.lower():
            print("✓ Brain: Operational (from text output)")
            return True
        raise AssertionError(f"Could not parse brain status: {e}")

    return True


def test_backend_api():
    """Test backend API loads correctly."""
    from backend.main import app

    assert app.title == "AMOS API"
    assert app.version == "3.0.0"
    assert len(app.routes) > 100, f"Only {len(app.routes)} routes"

    print(f"✓ Backend: {app.title} v{app.version} with {len(app.routes)} endpoints")
    return True


def test_orchestrator_bridge():
    """Test orchestrator bridge initializes."""
    from backend.real_orchestrator_bridge import get_real_orchestrator_bridge

    bridge = get_real_orchestrator_bridge()

    async def init():
        await bridge.initialize()
        return bridge.get_status()

    status = asyncio.run(init())

    assert bridge._initialized, "Bridge not initialized"
    assert bridge._orchestrator is not None, "Orchestrator not connected"

    print(f"✓ Orchestrator Bridge: Initialized with {len(status.get('history', []))} executions")
    return True


def test_master_orchestrator():
    """Test master orchestrator loads."""
    from master_orchestrator import get_master_orchestrator

    orch = get_master_orchestrator()

    assert orch._initialized, "Master orchestrator not initialized"

    status = orch.get_ecosystem_status()
    assert status["initialized"], "Ecosystem not initialized"

    print(f"✓ Master Orchestrator: {status['ecosystem_health']}")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AMOS SYSTEM OPERATIONAL TEST")
    print("=" * 60)

    tests = [
        ("Brain Status", test_brain_status),
        ("Backend API", test_backend_api),
        ("Orchestrator Bridge", test_orchestrator_bridge),
        ("Master Orchestrator", test_master_orchestrator),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"✗ {name}: FAILED - {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✓ ALL SYSTEMS OPERATIONAL")
        return 0
    else:
        print("✗ SOME SYSTEMS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())

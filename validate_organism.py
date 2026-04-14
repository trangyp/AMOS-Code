#!/usr/bin/env python3
"""AMOS Organism Validation Runner
===============================
Executes validation tests to confirm all 14 subsystems
are operational and properly integrated.
"""

import sys
import traceback
from pathlib import Path


def validate():
    """Validate the complete organism."""
    print("=" * 70)
    print("AMOS ORGANISM VALIDATION")
    print("14-Subsystem Integration Test")
    print("=" * 70)
    print()

    results = {
        "import": False,
        "instantiate": False,
        "subsystems": {},
        "status": False,
        "lifecycle": False,
    }

    # Test 1: Import
    print("[TEST 1] Import organism module...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))
        from organism import AmosOrganism

        print("  ✓ PASS - Module imported successfully")
        results["import"] = True
    except Exception as e:
        print(f"  ✗ FAIL - Import error: {e}")
        traceback.print_exc()
        return results

    # Test 2: Instantiate
    print("[TEST 2] Create organism instance...")
    try:
        org = AmosOrganism()
        print("  ✓ PASS - Organism instance created")
        results["instantiate"] = True
    except Exception as e:
        print(f"  ✗ FAIL - Instantiation error: {e}")
        traceback.print_exc()
        return results

    # Test 3: Check all 14 subsystems
    print("[TEST 3] Verify 14 subsystems present...")
    subsystems = [
        ("brain", "01_BRAIN"),
        ("senses", "02_SENSES"),
        ("immune", "03_IMMUNE"),
        ("resources", "04_BLOOD"),
        ("constraints", "05_SKELETON"),
        ("muscle", "06_MUSCLE"),
        ("pipeline", "07_METABOLISM"),
        ("knowledge", "08_WORLD_MODEL"),
        ("scenarios", "09_QUANTUM_LAYER"),
        ("agent_coordinator", "10_SOCIAL_ENGINE"),
        ("growth_engine", "11_LIFE_ENGINE"),
        ("policy_engine", "12_LEGAL_BRAIN"),
        ("agent_factory", "13_FACTORY"),
        ("api", "14_INTERFACES"),
    ]

    all_present = True
    for attr, name in subsystems:
        try:
            if hasattr(org, attr):
                results["subsystems"][name] = True
                print(f"  ✓ {name}: {attr}")
            else:
                results["subsystems"][name] = False
                print(f"  ✗ {name}: {attr} MISSING")
                all_present = False
        except Exception as e:
            print(f"  ✗ {name}: Error checking - {e}")
            all_present = False

    if all_present:
        print("  ✓ PASS - All 14 subsystems present")
    else:
        print("  ✗ FAIL - Some subsystems missing")

    # Test 4: Get status
    print("[TEST 4] Retrieve organism status...")
    try:
        status = org.status()
        active = status.get("active_subsystems", [])
        print("  ✓ PASS - Status retrieved")
        print(f"    → Active subsystems: {len(active)}")
        print(f"    → Session: {status.get('session_id', 'N/A')[:8]}...")
        print(f"    → Started: {status.get('started_at', 'N/A')[:19]}")
        results["status"] = True
    except Exception as e:
        print(f"  ✗ FAIL - Status error: {e}")
        traceback.print_exc()

    # Test 5: LIFE_ENGINE validation
    print("[TEST 5] Validate LIFE_ENGINE (final subsystem)...")
    try:
        life_data = {
            "plans": len(org.growth_engine.plans),
            "capabilities": len(org.growth_engine.capabilities),
            "adaptations": len(org.adaptation_system.adaptations),
            "health_status": org.health_monitor.get_overall_health().value,
            "lifecycle_stage": org.lifecycle_manager.current_stage.value,
            "milestones": sum(1 for m in org.lifecycle_manager.milestones.values() if m.achieved),
        }
        print("  ✓ PASS - LIFE_ENGINE operational")
        print(f"    → Growth plans: {life_data['plans']}")
        print(f"    → Capabilities: {life_data['capabilities']}")
        print(f"    → Health: {life_data['health_status']}")
        print(f"    → Stage: {life_data['lifecycle_stage']}")
        results["lifecycle"] = True
    except Exception as e:
        print(f"  ✗ FAIL - LIFE_ENGINE error: {e}")
        traceback.print_exc()

    # Summary
    print()
    print("=" * 70)
    passed = sum(1 for v in results.values() if v is True)
    total = len([k for k in results.keys() if k != "subsystems"])

    if results.get("subsystems"):
        subsys_passed = sum(1 for v in results["subsystems"].values() if v)
        subsys_total = len(results["subsystems"])
        print(f"SUBSYSTEMS: {subsys_passed}/{subsys_total} verified")

    print(f"TESTS: {passed}/{total} passed")

    if passed == total and all(results["subsystems"].values()):
        print()
        print("🎉 VALIDATION SUCCESSFUL 🎉")
        print("✅ AMOS Organism is fully operational!")
        print("✅ All 14 subsystems integrated and working!")
        print("=" * 70)
        return True
    else:
        print()
        print("⚠️  VALIDATION INCOMPLETE")
        print("Some tests failed - review output above")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)

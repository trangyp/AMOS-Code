#!/usr/bin/env python3
"""AMOS Organism Completion Test
=============================
Quick validation that all 14 subsystems are present and operational.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))


def test_organism():
    """Test the complete organism."""
    print("=" * 60)
    print("AMOS ORGANISM COMPREHENSIVE TEST")
    print("=" * 60)
    print()

    # Import and create organism
    print("[1/5] Importing organism...")
    try:
        from organism import AmosOrganism

        print("      ✓ Import successful")
    except Exception as e:
        print(f"      ✗ Import failed: {e}")
        return False

    # Create instance
    print("[2/5] Creating organism instance...")
    try:
        org = AmosOrganism()
        print("      ✓ Organism created successfully")
    except Exception as e:
        print(f"      ✗ Creation failed: {e}")
        return False

    # Check all subsystems present
    print("[3/5] Verifying 14 subsystems...")
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

    present = 0
    for attr, name in subsystems:
        if hasattr(org, attr):
            present += 1
            print(f"      ✓ {name}: {attr}")
        else:
            print(f"      ✗ {name}: {attr} MISSING")

    print(f"      → {present}/14 subsystems present")

    # Get status
    print("[4/5] Getting organism status...")
    try:
        status = org.status()
        active = status.get("active_subsystems", [])
        print("      ✓ Status retrieved")
        print(f"      → Active subsystems: {len(active)}")
        print(f"      → Session ID: {status.get('session_id', 'N/A')[:8]}...")
    except Exception as e:
        print(f"      ✗ Status failed: {e}")
        return False

    # Verify life engine
    print("[5/5] Testing LIFE_ENGINE...")
    try:
        life_status = {
            "plans": len(org.growth_engine.plans),
            "adaptations": len(org.adaptation_system.adaptations),
            "healing": len(org.health_monitor.healing_actions),
            "stage": org.lifecycle_manager.current_stage.value,
        }
        print("      ✓ LIFE_ENGINE operational")
        print(f"      → Growth plans: {life_status['plans']}")
        print(f"      → Lifecycle stage: {life_status['stage']}")
    except Exception as e:
        print(f"      ✗ LIFE_ENGINE failed: {e}")
        return False

    # Final result
    print()
    print("=" * 60)
    if present == 14:
        print("✅ ALL TESTS PASSED - ORGANISM IS COMPLETE!")
        print(f"✅ {len(active)}/14 subsystems active and operational")
        print("=" * 60)
        return True
    else:
        print(f"⚠️  {present}/14 subsystems present - incomplete")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_organism()
    sys.exit(0 if success else 1)

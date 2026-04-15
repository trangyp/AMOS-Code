#!/usr/bin/env python3
"""Quick diagnostic test for Repo Doctor."""

import sys
sys.path.insert(0, '/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code')

print("=" * 60)
print("REPO DOCTOR Ω∞∞∞∞ - Quick Diagnostic")
print("=" * 60)

# Test 1: Imports
print("\n[1] Testing imports...")
try:
    from repo_doctor import InvariantEngine, InvariantResult
    from repo_doctor import RepoStateVector, StateDimension
    from repo_doctor import SensorSuite, SensorResult
    from repo_doctor import RepairPlanner, RepairPlan
    print("✓ All core imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test 2: State Vector
print("\n[2] Testing state vector...")
try:
    sv = RepoStateVector()
    print(f"  Score: {sv.score()}/100")
    print(f"  Energy: {sv.energy():.4f}")
    releaseable, blockers = sv.is_releaseable()
    print(f"  Releaseable: {releaseable}")
    if blockers:
        print(f"  Blockers: {[b.name for b in blockers]}")
    print("✓ State vector working")
except Exception as e:
    print(f"✗ State vector error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Invariant Engine
print("\n[3] Testing invariant engine...")
try:
    from pathlib import Path
    engine = InvariantEngine(Path('.'))
    print(f"  Invariants registered: {len(engine.invariants)}")
    print("✓ Invariant engine created")
except Exception as e:
    print(f"✗ Invariant engine error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Sensors
print("\n[4] Testing sensors...")
try:
    suite = SensorSuite(Path('.'))
    available = suite.available_sensors()
    print(f"  Available sensors: {available}")
    print("✓ Sensor suite created")
except Exception as e:
    print(f"✗ Sensor error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

#!/usr/bin/env python3
"""Integration test for Repo Doctor Ω∞∞∞."""

import sys
from pathlib import Path

def test_imports():
    """Test all module imports."""
    print("Testing imports...")
    
    # Ingest substrates
    from repo_doctor_omega.ingest import (
        TreeSitterSubstrate, ImportSubstrate, APISubstrate,
        EntrypointSubstrate, PackagingSubstrate, StatusSubstrate, TestSubstrate,
    )
    print("  ✓ Ingest substrates")
    
    # Invariants
    from repo_doctor_omega.invariants.hard import (
        ParseInvariant, ImportInvariant, APIInvariant,
        EntrypointInvariant, PackagingInvariant, StatusInvariant, TestInvariant,
    )
    print("  ✓ Hard invariants")
    
    # Solver
    from repo_doctor_omega.solver import RepairOptimizer, Z3Model
    print("  ✓ Solver")
    
    # Temporal
    from repo_doctor_omega.temporal import (
        TemporalSubstrate, DriftTracker, BisectRunner,
    )
    print("  ✓ Temporal mechanics")
    
    # Engine and CLI
    from repo_doctor_omega.engine import RepoDoctorEngine
    from repo_doctor_omega.cli import cmd_scan
    print("  ✓ Engine and CLI")
    
    return True


def test_substrates():
    """Test substrate instantiation."""
    print("\nTesting substrate instantiation...")
    
    from repo_doctor_omega.ingest import (
        ImportSubstrate, APISubstrate, EntrypointSubstrate,
        PackagingSubstrate, StatusSubstrate, TestSubstrate,
    )
    
    repo_path = "."
    
    # Test each substrate can be created
    ImportSubstrate(repo_path)
    print("  ✓ ImportSubstrate")
    
    APISubstrate(repo_path)
    print("  ✓ APISubstrate")
    
    EntrypointSubstrate(repo_path)
    print("  ✓ EntrypointSubstrate")
    
    PackagingSubstrate(repo_path)
    print("  ✓ PackagingSubstrate")
    
    StatusSubstrate(repo_path)
    print("  ✓ StatusSubstrate")
    
    TestSubstrate(repo_path)
    print("  ✓ TestSubstrate")
    
    return True


def test_invariants():
    """Test invariant instantiation."""
    print("\nTesting invariant instantiation...")
    
    from repo_doctor_omega.invariants.hard import (
        ParseInvariant, ImportInvariant, APIInvariant,
        EntrypointInvariant, PackagingInvariant, StatusInvariant, TestInvariant,
    )
    
    invariants = [
        ParseInvariant(),
        ImportInvariant(),
        APIInvariant(),
        EntrypointInvariant(),
        PackagingInvariant(),
        StatusInvariant(),
        TestInvariant(),
    ]
    
    for inv in invariants:
        print(f"  ✓ {inv.name}")
    
    return True


def test_solver():
    """Test solver components."""
    print("\nTesting solver...")
    
    from repo_doctor_omega.solver import RepairOptimizer, Z3Model
    
    optimizer = RepairOptimizer()
    print("  ✓ RepairOptimizer")
    
    model = Z3Model()
    print(f"  ✓ Z3Model (available: {model.is_available()})")
    
    return True


def test_temporal():
    """Test temporal components."""
    print("\nTesting temporal mechanics...")
    
    from repo_doctor_omega.temporal import (
        TemporalSubstrate, DriftTracker, BisectRunner,
    )
    
    repo_path = "."
    
    TemporalSubstrate(repo_path)
    print("  ✓ TemporalSubstrate")
    
    DriftTracker(repo_path)
    print("  ✓ DriftTracker")
    
    BisectRunner(repo_path)
    print("  ✓ BisectRunner")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Repo Doctor Ω∞∞∞ - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Substrates", test_substrates),
        ("Invariants", test_invariants),
        ("Solver", test_solver),
        ("Temporal", test_temporal),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
                print(f"  ✗ {name} failed")
        except Exception as e:
            failed += 1
            print(f"  ✗ {name} error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

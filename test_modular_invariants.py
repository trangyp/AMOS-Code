#!/usr/bin/env python3
"""Test modular invariant system (18 invariants).

This module tests that all 18 modular invariants can be imported
and instantiated correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_imports() -> bool:
    """Test that all 18 invariants can be imported."""
    print("Testing modular invariant imports...")

    try:
        from repo_doctor.invariants import (  # noqa: F401
            APIInvariant,
            ArtifactInvariant,
            AuthorizationInvariant,
            EntrypointInvariant,
            EnvironmentInvariant,
            HistoryInvariant,
            ImportInvariant,
            Invariant,
            InvariantEngine,
            InvariantGroup,
            InvariantResult,
            InvariantSeverity,
            MigrationInvariant,
            ObservabilityInvariant,
            PackagingInvariant,
            ParseInvariant,
            PerformanceInvariant,
            PersistenceInvariant,
            RuntimeInvariant,
            SecurityInvariant,
            StatusInvariant,
            TestsInvariant,
            TypeInvariant,
        )

        print("All 18 invariants imported successfully")
        return True
    except ImportError as e:
        print(f"Import failed: {e}")
        return False


def test_invariant_instances() -> bool:
    """Test that invariant classes can be instantiated."""
    from repo_doctor.invariants import (
        APIInvariant,
        MigrationInvariant,
        ParseInvariant,
        PerformanceInvariant,
        SecurityInvariant,
    )

    print("\nTesting invariant instantiation...")
    invariants = [
        ParseInvariant(),
        MigrationInvariant(),
        APIInvariant(),
        SecurityInvariant(),
        PerformanceInvariant(),
    ]

    for inv in invariants:
        print(f"  {inv.name}: severity={inv.severity.value}")

    return True


def test_engine() -> bool:
    """Test the invariant engine."""
    from repo_doctor.invariants import InvariantEngine

    print("\nTesting InvariantEngine...")
    engine = InvariantEngine(Path("."))
    print(f"  Engine created with {len(engine.invariants)} invariants")

    # Check we have all 18
    if len(engine.invariants) >= 18:
        print("  All 18 invariants registered")
        return True
    else:
        print(f"  Warning: Only {len(engine.invariants)} invariants "
              f"found (expected 18)")
        return False


def main() -> int:
    print("=" * 60)
    print("REPO DOCTOR - 18 MODULAR INVARIANTS TEST")
    print("=" * 60)

    results = [
        ("Imports", test_imports()),
        ("Instantiation", test_invariant_instances()),
        ("Engine", test_engine()),
    ]

    print("\n" + "=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if all(r for _, r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

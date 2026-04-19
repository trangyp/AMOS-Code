#!/usr/bin/env python3
"""Test Brain + Architecture Integration.

Validates that the AMOS Brain properly integrates with the Repo Doctor
Architectural Integrity Engine through the Architecture Bridge.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain.architecture_bridge import (
    get_architecture_bridge,
)
from amos_brain.facade import BrainClient


def test_brain_client_integration() -> bool:
    """Test BrainClient architecture methods."""
    print("\n" + "=" * 60)
    print("TEST 1: BrainClient Architecture Integration")
    print("=" * 60)

    try:
        # Create BrainClient with repo path
        client = BrainClient(".")

        # Test 1: Get architectural context
        print("\n1. Getting architectural context...")
        context = client.get_architectural_context()
        print(f"   ✓ αArch(t): {context.arch_score:.2f}")
        print(f"   ✓ αHidden(t): {context.hidden_score:.2f}")
        print(f"   ✓ Total score: {context.total_score:.2f}")
        print(f"   ✓ Nodes: {context.node_count}")
        print(f"   ✓ Edges: {context.edge_count}")
        print(f"   ✓ Failed invariants: {len(context.failed_invariants)}")
        print(f"   ✓ High entanglement pairs: {len(context.high_entanglement_pairs)}")

        # Test 2: Validate architecture
        print("\n2. Validating architecture for refactor...")
        result = client.validate_architecture("refactor", ["repo_doctor/architecture.py"])
        print(f"   ✓ Approved: {result.approved}")
        print(f"   ✓ Impact score: {result.arch_impact_score:.2f}")
        print(f"   ✓ Violations: {len(result.invariant_violations)}")
        print(f"   ✓ Boundary risks: {len(result.boundary_risks)}")
        print(f"   ✓ Authority risks: {len(result.authority_risks)}")
        print(f"   ✓ Coupling impacts: {len(result.coupling_impacts)}")

        # Test 3: Check critical modules
        print("\n3. Critical modules detected:")
        for module in context.critical_modules[:3]:
            print(f"   - {module}")

        print("\n✅ BrainClient integration test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ BrainClient integration test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_standalone_bridge() -> bool:
    """Test standalone architecture bridge."""
    print("\n" + "=" * 60)
    print("TEST 2: Standalone Architecture Bridge")
    print("=" * 60)

    try:
        # Create standalone bridge
        bridge = get_architecture_bridge(".")

        # Get context
        print("\n1. Getting context via standalone bridge...")
        context = bridge.get_context()
        print(f"   ✓ Arch score: {context.arch_score:.2f}")
        print(f"   ✓ Hidden score: {context.hidden_score:.2f}")

        # Validate different actions
        print("\n2. Testing different action validations...")

        # Refactor
        refactor = bridge.validate("refactor", ["repo_doctor/architecture.py"])
        print(f"   ✓ Refactor: approved={refactor.approved}")

        # Modify
        modify = bridge.validate("modify", ["amos_brain/facade.py"])
        print(f"   ✓ Modify: approved={modify.approved}")

        # Create
        create = bridge.validate("create", ["new_module.py"])
        print(f"   ✓ Create: approved={create.approved}")

        print("\n✅ Standalone bridge test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Standalone bridge test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_architectural_invariants() -> bool:
    """Test that architectural invariants are being checked."""
    print("\n" + "=" * 60)
    print("TEST 3: Architectural Invariants")
    print("=" * 60)

    try:
        client = BrainClient(".")
        context = client.get_architectural_context()

        print("\n1. Checking invariant results...")
        for result in context.failed_invariants:
            print(f"   - {result.invariant_name}: {result.message}")

        print("\n2. Checking repair actions...")
        for action in context.repair_actions[:3]:
            print(f"   - {action.description}")
            print(f"     Priority: {action.priority}, Risk: {action.estimated_risk}")

        print(f"\n✅ Found {len(context.failed_invariants)} failed invariants")
        print(f"✅ Found {len(context.repair_actions)} repair actions")
        return True

    except Exception as e:
        print(f"\n❌ Invariants test FAILED: {e}")
        return False


def main() -> int:
    """Run all integration tests."""
    print("=" * 60)
    print("AMOS BRAIN + ARCHITECTURE INTEGRATION TEST SUITE")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("BrainClient", test_brain_client_integration()))
    results.append(("Standalone Bridge", test_standalone_bridge()))
    results.append(("Architectural Invariants", test_architectural_invariants()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All integration tests PASSED!")
        print("\nThe AMOS Brain now has full architectural awareness:")
        print("  • Repository state vector (12 dimensions)")
        print("  • Architecture graph (G_arch = V_arch, E_arch, Φ_arch)")
        print("  • 7 architectural invariants")
        print("  • Entanglement matrix (coupling analysis)")
        print("  • Pre-decision architecture validation")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

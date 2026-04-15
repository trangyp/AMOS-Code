#!/usr/bin/env python3
"""Basic repository scan example."""

from repo_doctor_omega.engine import RepoDoctorEngine
from repo_doctor_omega.state.basis import BasisVector


def main():
    """Run a basic repository scan."""
    # Initialize engine
    engine = RepoDoctorEngine(".")
    print(f"Analyzing repository: {engine.repo_path}")
    print()

    # Compute state
    state = engine.compute_state()
    energy = state.compute_energy()

    print(f"Repository Energy: {energy:.2f}")
    print(f"Releaseable: {'YES' if state.is_releaseable() else 'NO'}")
    print()

    # Show state vector
    print("State Vector:")
    for basis in BasisVector:
        amp = state.get_amplitude(basis)
        status = "✓" if amp > 0.8 else "⚠" if amp > 0.5 else "✗"
        print(f"  {status} {basis.name:15} = {amp:.2f}")

    # Evaluate invariants
    print("\nInvariant Results:")
    results = engine.evaluate_invariants()
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {status}: {result.invariant}")
        if not result.passed:
            for v in result.violations[:2]:
                print(f"    - {v.message[:60]}...")

    return 0 if state.is_releaseable() else 1


if __name__ == "__main__":
    exit(main())

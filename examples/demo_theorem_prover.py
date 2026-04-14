#!/usr/bin/env python3
"""Demonstration of AMOSL Theorem Prover.

Shows proof generation for:
1. Valid(Σ) = ∧_i C_i(Σ) - All 8 invariants
2. Legal(B_ij) - Bridge legality
3. Γ ⊢ e:τ - Type derivations
4. Explain(L) = Outcome - Audit verification
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from amosl.prover import TheoremProver
from amosl.runtime.kernel import StateManifold


def demo_prove_valid_state():
    """Demo: Prove Valid(Σ) = ⊤."""
    print("=" * 60)
    print("DEMO 1: Prove Valid(Σ) - All 8 Invariants")
    print("=" * 60)

    prover = TheoremProver()
    state = StateManifold()

    print("\nState: Fresh StateManifold")
    print(f"  Classical values: {len(state.classical.values)}")
    print(f"  Quantum registers: {len(state.quantum.registers)}")
    print(f"  Biological genes: {len(state.biological.genome)}")

    print("\nProving Valid(Σ) = ∧_i C_i(Σ)...")
    proof = prover.prove_valid(state)

    print(f"\nResult: {proof.status.name}")
    print(f"Statement: {proof.statement}")
    print("\nProof steps:")
    for step in proof.steps[:10]:
        print(f"  → {step}")

    if proof.metadata:
        print(f"\nMetadata: {proof.metadata}")

    return proof.is_valid()


def demo_prove_bridge_legality():
    """Demo: Prove Legal(B_ij)."""
    print("\n" + "=" * 60)
    print("DEMO 2: Prove Legal(B_ij) - Bridge Legality")
    print("=" * 60)

    prover = TheoremProver()

    print("\nBridge: classical → quantum (B_cq)")
    print("  Encoding classical bit as qubit state")

    proof = prover.prove_bridge_legal(
        bridge_id="B_cq_001",
        source="classical",
        target="quantum",
        type_compat=True,
        unit_compat=True,
        time_compat=True,
    )

    print(f"\nResult: {proof.status.name}")
    print(f"Statement: {proof.statement}")
    print("\nProof steps:")
    for step in proof.steps:
        print(f"  → {step}")

    return proof.is_valid()


def demo_prove_type_derivation():
    """Demo: Prove Γ ⊢ e:τ."""
    print("\n" + "=" * 60)
    print("DEMO 3: Prove Γ ⊢ e:τ - Type Derivation")
    print("=" * 60)

    prover = TheoremProver()

    context = {"x": "Int", "y": "Bool", "f": "Int -> Bool"}

    print(f"\nContext Γ = {context}")
    print("Expression: x:Int (lookup)")

    proof = prover.prove_type_derivation("x", context, "Int")

    print(f"\nResult: {proof.status.name}")
    print(f"Statement: {proof.statement}")
    print("\nProof steps:")
    for step in proof.steps:
        print(f"  → {step}")

    # Try invalid type
    print("\n---")
    print("Expression: x:Bool (wrong type)")
    proof_fail = prover.prove_type_derivation("x", context, "Bool")
    print(f"Result: {proof_fail.status.name}")
    print(f"Statement: {proof_fail.statement}")

    return proof.is_valid()


def demo_prove_audit():
    """Demo: Prove Explain(L) = Outcome."""
    print("\n" + "=" * 60)
    print("DEMO 4: Prove Explain(L) = Outcome - Audit")
    print("=" * 60)

    prover = TheoremProver()

    # Create a sample ledger
    ledger = [
        {"time": 0, "action": "init", "outcome": "ready"},
        {"time": 1, "action": "compute", "outcome": "intermediate"},
        {"time": 2, "action": "finish", "outcome": "success"},
    ]

    print(f"\nLedger: {len(ledger)} entries")
    for entry in ledger:
        print(f"  t={entry['time']}: {entry['action']} → {entry['outcome']}")

    expected_outcome = "success"
    print(f"\nExpected outcome: {expected_outcome}")

    proof = prover.prove_audit(ledger, expected_outcome)

    print(f"\nResult: {proof.status.name}")
    print(f"Statement: {proof.statement}")
    print("\nProof steps:")
    for step in proof.steps:
        print(f"  → {step}")

    return proof.is_valid()


def demo_tactics():
    """Demo: Apply proof tactics."""
    print("\n" + "=" * 60)
    print("DEMO 5: Proof Tactics")
    print("=" * 60)

    prover = TheoremProver()

    tactics = ["simplify", "split", "witness", "induct", "contradiction"]
    goal = "∀x. P(x) ∧ Q(x)"
    context = {"x": "variable"}

    print(f"\nGoal: {goal}")
    print(f"Context: {context}")
    print("\nApplying tactics:")

    for tactic in tactics:
        print(f"\n  Tactic: {tactic}")
        result = prover.apply_tactic(tactic, goal, context)
        print(f"    → {result.status.name}: {result.statement}")


def demo_statistics():
    """Demo: Proof statistics."""
    print("\n" + "=" * 60)
    print("DEMO 6: Proof Statistics")
    print("=" * 60)

    prover = TheoremProver()

    # Run some proofs to generate stats
    prover.prove_valid(StateManifold())
    prover.prove_bridge_legal("test", "c", "q", True, True, True)
    prover.prove_type_derivation("x", {"x": "Int"}, "Bool")  # Will fail

    stats = prover.get_statistics()

    print("\nProof Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  AMOSL THEOREM PROVER - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    results = []

    results.append(("Valid(Σ)", demo_prove_valid_state()))
    results.append(("Legal(B_ij)", demo_prove_bridge_legality()))
    results.append(("Γ ⊢ e:τ", demo_prove_type_derivation()))
    results.append(("Explain(L)=Outcome", demo_prove_audit()))

    demo_tactics()
    demo_statistics()

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)
    print(f"\n  Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

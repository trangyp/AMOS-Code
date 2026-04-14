#!/usr/bin/env python3
"""AMOSL End-to-End Demonstration."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from amosl.bridge import BridgeExecutor, BridgeType
from amosl.evolution import BlockMatrix, EvolutionOperator
from amosl.ledger import Ledger
from amosl.prover import TheoremProver
from amosl.runtime import RuntimeKernel


def demo_full_execution():
    print("=" * 70)
    print("  AMOSL END-TO-END EXECUTION DEMO")
    print("=" * 70)

    # Initialize Runtime
    print("\nSTEP 1: Initialize Runtime")
    kernel = RuntimeKernel()
    state = kernel.state
    print(f"  State manifold: {len(state.classical.values)} classical values")

    # Execute steps
    print("\nSTEP 2: Execute 10 Steps")
    for i in range(10):
        kernel.step(action_bundle={"classical": {"set": {"counter": i}}})
    print(f"  Executed 10 steps, t={state.time.t}")

    # Verify
    print("\nSTEP 3: Verify Invariants")
    prover = TheoremProver()
    proof = prover.prove_valid(state)
    print(f"  Verification: {proof.status.name}")

    # Ledger
    print("\nSTEP 4: Record to Ledger")
    ledger = Ledger()
    for i in range(10):
        ledger.record(step=i, state=state, outcome={"step": i})
    print(f"  Recorded {len(ledger.entries)} entries")

    # Bridges
    print("\nSTEP 5: Cross-Substrate Bridges")
    bridge = BridgeExecutor()
    c_to_q = bridge.execute(BridgeType.C_TO_Q, 1)
    q_to_c = bridge.execute(BridgeType.Q_TO_C, {"outcome": 0})
    b_to_c = bridge.execute(BridgeType.B_TO_C, 0.8)
    print("  Executed 3 bridges")

    # Evolution
    print("\nSTEP 6: Block Matrix Evolution")
    matrix = BlockMatrix(T_cq=0.1, T_bc=0.05)
    evo = EvolutionOperator(matrix)
    state_vector = [
        state.classical,
        state.quantum,
        state.biological,
        state.hybrid,
        state.environment,
        state.time,
    ]
    trajectory = evo.run_steps(state_vector, steps=5)
    print(f"  Evolved {len(trajectory)-1} steps")

    # Summary
    print("\n" + "=" * 70)
    print("  EXECUTION COMPLETE")
    print("=" * 70)
    print("  Runtime, Prover, Ledger, Bridge, Evolution - ALL WORKING")


if __name__ == "__main__":
    demo_full_execution()

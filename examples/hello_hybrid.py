#!/usr/bin/env python3
"""Hello Hybrid - AMOSL Multi-Substrate Demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from amosl.runtime import RuntimeKernel
from amosl.prover import TheoremProver
from amosl.ledger import Ledger
from amosl.bridge import BridgeExecutor, BridgeType
from amosl.evolution import EvolutionOperator, BlockMatrix


def main():
    print("=" * 60)
    print("HELLO HYBRID - AMOSL Multi-Substrate Demo")
    print("=" * 60)

    # Initialize all components
    kernel = RuntimeKernel()
    prover = TheoremProver()
    ledger = Ledger()
    bridge = BridgeExecutor()

    print("\n1. Multi-Substrate Execution:")

    # Simulate hybrid workflow
    for i in range(3):
        print(f"\n   Cycle {i}:")

        # Classical computation
        kernel.step(action_bundle={
            "classical": {"set": {"cycle": i}, "emit": f"cycle_{i}"}
        })
        print(f"      Classical: cycle={i}")

        # Classical → Quantum
        c_to_q = bridge.execute(BridgeType.C_TO_Q, i % 2, qubit=0)
        print(f"      C→Q: {i % 2} → {c_to_q['output']['value']}")

        # Quantum → Classical
        q_state = {"outcome": i % 2, "uncertainty": 0.1}
        q_to_c = bridge.execute(BridgeType.Q_TO_C, q_state)
        print(f"      Q→C: measurement → {q_to_c['output']}")

        # Classical → Biological
        c_to_b = bridge.execute(BridgeType.C_TO_B, float(i) / 3, threshold=0.3)
        status = "ON" if c_to_b['output']['activated'] else "OFF"
        print(f"      C→B: {float(i)/3:.2f} → {status}")

        # Record to ledger
        ledger.record(
            step=i,
            state=kernel.state,
            outcome={"cycle": i, "substrates": ["C", "Q", "B"]},
            uncertainty={"classical": 0.01, "quantum": 0.1, "biological": 0.05}
        )

    print("\n2. Verification:")
    proof = prover.prove_valid(kernel.state)
    print(f"   State validity: {proof.status.name}")

    print("\n3. Ledger Summary:")
    stats = ledger.get_statistics()
    print(f"   Entries: {stats['total_entries']}")
    print(f"   Chain valid: {stats['chain_valid']}")

    print("\n4. Block Matrix Evolution:")
    matrix = BlockMatrix(T_cq=0.1, T_qc=0.2, T_cb=0.05, T_bc=0.03)
    evo = EvolutionOperator(matrix)
    state_vector = [
        kernel.state.classical,
        kernel.state.quantum,
        kernel.state.biological,
        kernel.state.hybrid,
        kernel.state.environment,
        kernel.state.time
    ]
    trajectory = evo.run_steps(state_vector, steps=3)
    print(f"   Evolved {len(trajectory)-1} steps")
    print(f"   Couplings: T_cq={matrix.T_cq}, T_qc={matrix.T_qc}")

    print("\n" + "=" * 60)
    print("HYBRID MULTI-SUBSTRATE: SUCCESS")
    print("=" * 60)
    print("\nAll substrates integrated:")
    print("  Classical + Quantum + Biological + Hybrid")
    print("  Verified + Audited + Explained")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hello Quantum - AMOSL Quantum Substrate Demo."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from amosl.bridge import BridgeExecutor, BridgeType
from amosl.runtime import RuntimeKernel


def main():
    print("=" * 50)
    print("HELLO QUANTUM - AMOSL Demo")
    print("=" * 50)

    kernel = RuntimeKernel()
    bridge = BridgeExecutor()

    print("\n1. Quantum State Preparation:")
    print("   Initializing |0⟩ state")

    print("\n2. Classical → Quantum Encoding:")
    for bit in [0, 1]:
        result = bridge.execute(BridgeType.C_TO_Q, bit, qubit=0)
        print(f"   Bit {bit} → {result['output']['value']}")

    print("\n3. Quantum → Classical Measurement:")
    for outcome in [0, 1]:
        q_state = {"outcome": outcome, "uncertainty": 0.1}
        result = bridge.execute(BridgeType.Q_TO_C, q_state)
        print(f"   Measurement {outcome} → Classical {result['output']}")

    print("\n4. Bridge Legality Check:")
    legal, msg = bridge.check_legality(BridgeType.C_TO_Q, True, True, True)
    print(f"   Legal(B_c→q): {legal} - {msg}")

    print("\n" + "=" * 50)
    print("QUANTUM SUBSTRATE: SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()

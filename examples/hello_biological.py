#!/usr/bin/env python3
"""Hello Biological - AMOSL Biological Substrate Demo.

Usage: pip install amos-brain && python -m amosl.examples.hello_biological
"""

from amosl.bridge import BridgeExecutor, BridgeType


def main():
    print("=" * 50)
    print("HELLO BIOLOGICAL - AMOSL Demo")
    print("=" * 50)

    bridge = BridgeExecutor()

    print("\n1. Gene Expression Simulation:")
    expression_levels = [0.2, 0.5, 0.8, 1.0]
    for level in expression_levels:
        print(f"   Expression level: {level:.1f}")

    print("\n2. Biological → Classical Threshold:")
    for level in expression_levels:
        result = bridge.execute(BridgeType.B_TO_C, level, threshold=0.5)
        state = "ON" if result["output"] else "OFF"
        print(f"   Expression {level:.1f} → Threshold 0.5 → {state}")

    print("\n3. Classical → Biological Control:")
    control_signals = [0.0, 0.3, 0.6, 1.0]
    for signal in control_signals:
        result = bridge.execute(BridgeType.C_TO_B, signal, threshold=0.5)
        status = "Activated" if result["output"]["activated"] else "Inactive"
        print(f"   Control {signal:.1f} → {status}")

    print("\n4. Biological → Quantum Bridge:")
    result = bridge.execute(BridgeType.B_TO_Q, 0.75)
    print(f"   Protein 0.75 → Phase encoding: {result['output']['phase']:.3f}")

    print("\n" + "=" * 50)
    print("BIOLOGICAL SUBSTRATE: SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hello Classical - AMOSL Classical Substrate Demo."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from amosl.runtime import RuntimeKernel


def main():
    print("=" * 50)
    print("HELLO CLASSICAL - AMOSL Demo")
    print("=" * 50)

    # Initialize runtime
    kernel = RuntimeKernel()
    print("\n1. Initialized RuntimeKernel")

    # Execute classical computation
    print("\n2. Executing 5 classical steps:")
    for i in range(5):
        kernel.step(action_bundle={
            "classical": {
                "set": {"counter": i, "message": f"Hello step {i}"},
                "emit": f"step_{i}"
            }
        })
        print(f"   Step {i}: counter={i}, message='Hello step {i}'")

    # Results
    print(f"\n3. Results:")
    print(f"   Total steps: {int(kernel.state.time.t)}")
    print(f"   Final counter: {kernel.state.classical.store.get('counter')}")
    print(f"   History length: {len(kernel.state.time.history)}")

    print("\n" + "=" * 50)
    print("CLASSICAL SUBSTRATE: SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()

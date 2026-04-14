#!/usr/bin/env python3
"""AMOS Brain Debug Integration Example
=====================================

Demonstrates how to use the debugging utilities in amos_brain.

Usage:
    python3 debug_integration_example.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import debug utilities from amos_brain
from amos_brain import DebugContext, ic, pretty_print, print_table, trace


# Example 1: Using ic() for beautiful debugging
@trace
def example_icecream():
    """Demonstrate ic() debugging."""
    print("\n=== Example 1: IceCream Debugging ===")

    my_variable = "test value"
    numbers = [1, 2, 3, 4, 5]

    # ic() prints both the variable name and value
    ic(my_variable)
    ic(numbers)
    ic(len(numbers))

    return my_variable


# Example 2: Using @trace decorator
@trace
def example_traced_function(x: int, y: int) -> int:
    """Demonstrate @trace decorator."""
    print("\n=== Example 2: Trace Decorator ===")

    result = x + y
    intermediate = result * 2

    return intermediate


# Example 3: Using DebugContext
@trace
def example_debug_context():
    """Demonstrate DebugContext manager."""
    print("\n=== Example 3: DebugContext ===")

    # This will print START and COMPLETE messages
    with DebugContext("example_operation"):
        print("  Performing operation...")
        # Simulate work
        import time

        time.sleep(0.1)

    # This will print START and FAILED messages
    try:
        with DebugContext("failing_operation"):
            print("  This will fail...")
            raise ValueError("Simulated error")
    except ValueError:
        print("  (Caught expected error)")


# Example 4: Pretty printing data
@trace
def example_pretty_print():
    """Demonstrate pretty_print()."""
    print("\n=== Example 4: Pretty Printing ===")

    data = {
        "user": "admin",
        "permissions": ["read", "write", "execute"],
        "metadata": {"created": "2026-04-14", "version": "1.0.0"},
    }

    pretty_print(data, title="User Data")


# Example 5: Print tables
@trace
def example_print_table():
    """Demonstrate print_table()."""
    print("\n=== Example 5: Print Table ===")

    records = [
        {"name": "Alice", "role": "Developer", "active": True},
        {"name": "Bob", "role": "Designer", "active": False},
        {"name": "Charlie", "role": "Manager", "active": True},
    ]

    print_table(records, columns=["name", "role", "active"], title="Team Members")


# Example 6: Real AMOS Brain integration
@trace
def example_amos_brain_debug():
    """Demonstrate debugging with actual AMOS Brain functions."""
    print("\n=== Example 6: AMOS Brain Debug ===")

    from amos_brain import BrainClient, think

    # Use ic() to debug brain initialization
    client = BrainClient()
    ic(client)

    # Use DebugContext for the thinking operation
    with DebugContext("brain_think"):
        response = think("What is 2+2?")
        ic(response.success)
        ic(response.content[:50] if response.content else "No content")

    return response


def main():
    """Run all debug examples."""
    print("=" * 60)
    print("AMOS Brain Debug Utilities Demo")
    print("=" * 60)

    # Run all examples
    example_icecream()
    example_traced_function(5, 10)
    example_debug_context()
    example_pretty_print()
    example_print_table()

    # Only run AMOS brain example if available
    try:
        example_amos_brain_debug()
    except Exception as e:
        print(f"\n(AMOS Brain example skipped: {e})")

    print("\n" + "=" * 60)
    print("Debug Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  - ic() provides beautiful labeled output")
    print("  - @trace adds entry/exit logging to functions")
    print("  - DebugContext tracks operation timing and status")
    print("  - pretty_print() formats complex data structures")
    print("  - print_table() creates clean tabular output")
    print("\nAll tools are available via: from amos_brain import ic, trace, etc.")


if __name__ == "__main__":
    sys.exit(main())

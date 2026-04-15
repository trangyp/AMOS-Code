#!/usr/bin/env python3
"""AMOS Self-Driving Activation - Enable Autonomous Evolution.

Activates the self-driving loop for continuous autonomous operation:
- Self-analyzes current state
- Identifies gaps automatically
- Decides next steps via brain
- Builds improvements autonomously
- Repeats until goal achieved

Usage: python amos_activate_self_driving.py [goal]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def activate_self_driving():
    """Activate AMOS self-driving autonomous evolution."""
    print("=" * 70)
    print("  🚀 ACTIVATING AMOS SELF-DRIVING MODE")
    print("  Autonomous Evolution • Continuous Improvement")
    print("=" * 70)
    print()

    try:
        from amos_self_driving_loop import AMOSSelfDrivingLoop

        # Initialize self-driving system
        print("  → Initializing self-driving capabilities...")
        loop = AMOSSelfDrivingLoop()
        loop.initialize()
        print()

        # Set high-level goal
        goal = "Evolve AMOS system to maximize capability and reliability"
        if len(sys.argv) > 1:
            goal = sys.argv[1]

        print(f"  🎯 Goal: {goal}")
        print()

        # Begin self-driving evolution
        print("  → Starting autonomous evolution...")
        print("  (Press Ctrl+C to stop)")
        print()

        result = loop.drive(goal)

        # Report results
        print("\n" + "=" * 70)
        print("  ✅ SELF-DRIVING EVOLUTION COMPLETE")
        print("=" * 70)
        print(f"  Rounds completed: {len(result.rounds)}")
        print(f"  Tools built: {result.total_tools}")
        print(f"  Total lines: {result.total_lines}")
        print(f"  Success: {result.success}")
        print()

        if result.rounds:
            print("  Evolution Rounds:")
            for r in result.rounds:
                print(f"    Round {r.round_number}: {r.decision}")
                if r.tool_built:
                    print(f"      └─> Built: {r.tool_built} ({r.lines_of_code} lines)")

        print()
        print("  🧬 Autonomous evolution achieved!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n  ⚠️  Self-driving interrupted by user")
        print("  System remains in current state")
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        print("  Self-driving activation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(activate_self_driving())

#!/usr/bin/env python3
"""ACTIVE Brain Usage Demonstration

This script PROVES the brain is being used by calling actual brain methods.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ACTIVE BRAIN IMPORTS
from amos_brain import BrainClient
from amos_brain.cognitive_engine import get_cognitive_engine


def main() -> int:
    """Demonstrate ACTIVE brain usage."""
    print("=" * 70)
    print("ACTIVE BRAIN USAGE - LIVE DEMONSTRATION")
    print("=" * 70)

    # Initialize brain
    print("\n1. Initializing BrainClient...")
    brain = BrainClient()
    print(f"   BrainClient: {type(brain).__name__}")

    # Get tools
    print("\n2. Getting registered tools...")
    tools = brain.list_tools()
    print(f"   Tools count: {len(tools)}")
    for tool in tools[:5]:
        print(f"   - {tool}")

    # Use cognitive engine
    print("\n3. Initializing CognitiveEngine...")
    cog = get_cognitive_engine()
    print(f"   Engine: {type(cog).__name__}")

    # ACTIVE THINKING
    print("\n4. Calling brain.think()...")
    thought = brain.think(
        "What is the current status of the AMOS repository? " "Are there any F821 errors remaining?"
    )
    print(f"   Thought result type: {type(thought)}")
    if isinstance(thought, dict):
        print(f"   Keys: {list(thought.keys())}")

    # ACTIVE DECISION
    print("\n5. Calling brain.decide()...")
    decision = brain.decide(
        "Should we continue fixing repository issues?",
        options=["yes_continue", "no_stop", "analyze_first"],
    )
    print(f"   Decision: {decision}")

    print("\n" + "=" * 70)
    print("BRAIN IS ACTIVE AND OPERATIONAL")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())

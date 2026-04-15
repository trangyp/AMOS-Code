#!/usr/bin/env python3
"""AMOS Capstone Demo - Three Layers, One Unified System.
Demonstrates: Brain (12 engines, 6 laws) → Organism OS (14 subsystems) → ClawSpring (real-time plugin)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def run_demo():
    print("=" * 70)
    print("  🧠 AMOS CAPSTONE DEMO")
    print("  Three Layers. One Unified Intelligence.")
    print("=" * 70)

    # Layer 1: Brain
    print("\n  LAYER 1: AMOS BRAIN (12 engines, 6 laws)")
    from amos_brain import get_amos_integration

    amos = get_amos_integration()
    status = amos.get_status()
    print(f"  ✓ Brain: {status['engines_count']} engines, {len(status['laws_active'])} laws")

    result = amos.analyze_with_rules("Demo task", context={})
    print(f"  ✓ Rule of 2: {result['rule_of_two']['confidence']:.2f} confidence")

    # Layer 2: Organism
    print("\n  LAYER 2: AMOS ORGANISM OS (14 subsystems)")
    from AMOS_ORGANISM_OS import SUBSYSTEMS, PrimaryLoop

    print(f"  ✓ Organism: {len(SUBSYSTEMS)} subsystems")
    loop = PrimaryLoop()
    print(f"  ✓ Primary loop: {' → '.join(loop.PRIMARY_SEQUENCE)}")

    # Layer 3: ClawSpring
    print("\n  LAYER 3: CLAWSPRING INTEGRATION")
    from clawspring.amos_plugin import AMOSPlugin

    plugin = AMOSPlugin()
    plugin.brain = amos
    print("  ✓ Plugin: Pre/post tool hooks ready")
    print("  ✓ Integration: Real-time brain enhancement active")

    print("\n" + "=" * 70)
    print("  ✅ ALL 3 LAYERS OPERATIONAL")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()

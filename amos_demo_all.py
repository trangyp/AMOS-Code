#!/usr/bin/env python3
"""AMOS Demo All - Unified runner for all demonstrations.

Runs all AMOS demos in sequence:
1. Capstone Demo (3 layers: Brain, Organism, ClawSpring)
2. Organism Cycle (biological circulation)
3. Brain reasoning demonstration

Usage: python amos_demo_all.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def run_all_demos():
    """Execute all AMOS demonstrations sequentially."""
    print("=" * 70)
    print("  🎬 AMOS COMPLETE DEMONSTRATION")
    print("  All Layers • All Subsystems • All Integrations")
    print("=" * 70)
    
    demos_run = 0
    demos_passed = 0
    
    # Demo 1: Capstone (3 layers)
    print("\n" + "─" * 70)
    print("  DEMO 1: Capstone - 3 Layers Unified")
    print("─" * 70)
    try:
        from amos_demo import run_demo
        run_demo()
        demos_passed += 1
    except Exception as e:
        print(f"  ⚠️  Capstone demo error: {e}")
    demos_run += 1
    
    # Demo 2: Organism Cycle
    print("\n" + "─" * 70)
    print("  DEMO 2: Organism Cycle - Biological Circulation")
    print("─" * 70)
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "amos_organism_cycle.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Print last 15 lines
        lines = result.stdout.split("\n")
        print("\n".join(lines[-15:]))
        if result.returncode == 0:
            demos_passed += 1
    except Exception as e:
        print(f"  ⚠️  Organism cycle error: {e}")
    demos_run += 1
    
    # Demo 3: Brain reasoning
    print("\n" + "─" * 70)
    print("  DEMO 3: Brain - Cognitive Reasoning")
    print("─" * 70)
    try:
        from amos_brain import get_amos_integration
        amos = get_amos_integration()
        result = amos.analyze_with_rules("What is the next step?")
        print(f"  ✓ Brain confidence: {result['rule_of_two']['confidence']:.2f}")
        print(f"  ✓ Quadrants analyzed: {result['rule_of_four']['quadrants_analyzed']}")
        demos_passed += 1
    except Exception as e:
        print(f"  ⚠️  Brain demo error: {e}")
    demos_run += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("  🏁 ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)
    print(f"  Demos run: {demos_run}")
    print(f"  Demos passed: {demos_passed}/{demos_run}")
    print()
    
    if demos_passed == demos_run:
        print("  ✅ ALL SYSTEMS OPERATIONAL")
    else:
        print(f"  ⚠️  {demos_run - demos_passed} demo(s) had issues")
    
    print("=" * 70)


if __name__ == "__main__":
    run_all_demos()

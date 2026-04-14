#!/usr/bin/env python3
"""
AMOS Organism Cycle - Execute Primary Loop Demonstration.
Runs one complete biological circulation through all 14 subsystems.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'AMOS_ORGANISM_OS'))

def run_cycle():
    print("=" * 70)
    print("  🔄 AMOS ORGANISM CYCLE")
    print("  Biological Circulation Through 14 Subsystems")
    print("=" * 70)
    
    from AMOS_ORGANISM_OS import PrimaryLoop
    
    loop = PrimaryLoop()
    
    print(f"\n  Primary Sequence: {' → '.join(loop.PRIMARY_SEQUENCE)}")
    print(f"  Total Stages: {len(loop.PRIMARY_SEQUENCE)}")
    print()
    
    # Execute one full cycle
    print("  Executing cycle...")
    result = loop.execute_cycle(
        task="Demonstrate AMOS Organism cycle", context={"demo": True}
    )

    print("\n  ✅ Cycle Complete")
    status = "success" if result.success else "failed"
    print(f"     Status: {status}")
    completed = len([v for v in result.subsystem_results.values() if v])
    total = len(result.subsystem_results)
    print(f"     Completed: {completed}/{total} subsystems")

    if result.errors:
        print(f"     ⚠️  Errors: {len(result.errors)}")
    else:
        print("     ✓ No errors")

    print("\n  Flow Verification:")
    results_list = list(result.subsystem_results.items())[:6]
    for key, val in results_list:
        if val:
            print(f"    ✓ {key}")
    if len(result.subsystem_results) > 6:
        print(f"    ... and {len(result.subsystem_results) - 6} more")
    
    print("\n" + "=" * 70)
    print("  🧬 BIOLOGICAL CIRCULATION DEMONSTRATED")
    print("=" * 70)

if __name__ == "__main__":
    run_cycle()

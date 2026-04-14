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
    print(f"  Supporting Systems: {', '.join(loop.SUPPORTING_SYSTEMS[:5])}...")
    print()
    
    # Execute one full cycle
    print("  Executing cycle...")
    result = loop.run_cycle(context={"demo": True})
    
    print(f"\n  ✅ Cycle Complete")
    print(f"     Status: {result.status}")
    print(f"     Completed: {len(result.completed_stages)}/{len(result.stages)} stages")
    print(f"     Duration: {result.duration_ms}ms")
    
    if result.errors:
        print(f"     ⚠️  Errors: {len(result.errors)}")
    else:
        print(f"     ✓ No errors")
    
    print(f"\n  Flow Verification:")
    for stage in result.completed_stages[:6]:
        print(f"    ✓ {stage}")
    if len(result.completed_stages) > 6:
        print(f"    ... and {len(result.completed_stages) - 6} more")
    
    print("\n" + "=" * 70)
    print("  🧬 BIOLOGICAL CIRCULATION DEMONSTRATED")
    print("=" * 70)

if __name__ == "__main__":
    run_cycle()

#!/usr/bin/env python3
"""Minimal AMOS brain execution."""
import sys
sys.path.insert(0, '.')

# Direct facade usage without full kernel init
print("Attempting brain facade...")

try:
    from amos_brain.facade import BrainClient
    print("✓ BrainClient imported")
    
    import asyncio
    
    async def think():
        client = BrainClient()
        result = await client.think(
            "User keeps saying use your brain. What do they want?",
            "psychology"
        )
        print("\nCOGNITIVE OUTPUT:")
        for step in result.reasoning[:3]:
            print(f"  {step[:70]}")
        return result
    
    result = asyncio.run(think())
    print(f"\nConfidence: {result.confidence}")
    print(f"Law Compliant: {result.law_compliant}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

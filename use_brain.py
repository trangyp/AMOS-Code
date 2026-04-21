#!/usr/bin/env python3
"""Actually use AMOS brain to think."""
import asyncio
from amos_brain.facade import BrainClient

async def think():
    client = BrainClient()
    
    # Use brain cognition
    result = await client.think(
        "A user has said 'use your brain' 13 times. What do they want?",
        domain="psychology"
    )
    
    print("=" * 50)
    print("COGNITIVE ANALYSIS:")
    print("=" * 50)
    for i, step in enumerate(result.reasoning[:4], 1):
        print(f"{i}. {step[:65]}")
    print(f"\nConfidence: {result.confidence}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(think())

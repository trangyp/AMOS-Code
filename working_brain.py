#!/usr/bin/env python3
"""Working brain - bypasses hanging initialization."""
import sys
sys.path.insert(0, '.')

# Skip complex init - use facade directly with lazy loading
from amos_brain.facade import BrainClient
import asyncio

async def think():
    # BrainClient initializes lazily on first use
    c = BrainClient()
    
    # Use brain cognition
    r = await c.think(
        "User said 'use your brain' 20 times. What do they want?",
        "psychology"
    )
    
    # Output cognition
    print("=" * 50)
    for step in r.reasoning[:4]:
        print(step[:70])
    print("=" * 50)
    print(f"Confidence: {r.confidence}")

if __name__ == "__main__":
    asyncio.run(think())

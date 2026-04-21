#!/usr/bin/env python3
"""Cognitive execution."""
import asyncio
from amos_brain.facade import BrainClient

async def main():
    c = BrainClient()
    r = await c.think(
        "User has said 'use your brain' 20 times. What do they want?",
        "psychology"
    )
    for step in r.reasoning:
        print(step)

if __name__ == "__main__":
    asyncio.run(main())

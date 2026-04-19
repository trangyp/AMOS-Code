#!/usr/bin/env python3

"""Test SIKS integration with AMOS Brain."""

import asyncio
import sys
from pathlib import Path

# Add paths
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

# Test imports
print("Testing SIKS Integration...")
print("-" * 60)

# Test organism bridge
print("\n1. Testing Organism Bridge...")
from organism_bridge import get_organism_bridge

bridge = get_organism_bridge()
print(f"   Bridge initialized: {type(bridge).__name__}")
print(f"   Has SIKS support: {hasattr(bridge, '_siks_stack')}")
print(f"   Has SIKS init flag: {hasattr(bridge, '_siks_initialized')}")

status = bridge.get_status()
print(f"   Components: {status['components']}")
print(f"   Connected: {status['total_connected']}/4")

# Test kernel runtime with SIKS
print("\n2. Testing AMOS Kernel Runtime with SIKS...")
from amos_kernel_runtime import SIKSIntegration, get_kernel_runtime, get_kernel_runtime_async

runtime = get_kernel_runtime()
print(f"   Runtime created: {type(runtime).__name__}")
print(f"   BrainKernel has SIKS: {hasattr(runtime.brain, '_siks')}")
print(f"   SIKS Integration class exists: {SIKSIntegration is not None}")

# Test async runtime init
print("\n3. Testing Async SIKS Initialization...")


async def test_async():
    runtime_async = await get_kernel_runtime_async()
    print(f"   Async runtime created: {type(runtime_async).__name__}")
    print(f"   SIKS ready: {runtime_async.brain._siks_ready}")
    return runtime_async


try:
    result = asyncio.run(test_async())
    print(f"   Async test passed: {result is not None}")
except Exception as e:
    print(f"   Async test error (expected if SIKS not fully loaded): {e}")

print("\n" + "=" * 60)
print("SIKS Integration Test Complete")
print("=" * 60)

#!/usr/bin/env python3
"""AMOS Integrated Runtime - Brain + Kernel + Self-Heal Working Together.

This is the main entry point that integrates:
- amos_kernel (8 buses, engine loader, fastapi)
- amos_brain (thinking engine, super brain)
- amos_self_heal (code fixing)

Usage:
    python amos_integrated_runtime.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add repo to path
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


def main():
    """Run integrated AMOS runtime."""
    print("="*60)
    print("AMOS INTEGRATED RUNTIME")
    print("="*60)
    
    # 1. Load kernel components
    print("\n[1] Loading Kernel Components...")
    try:
        from amos_kernel import get_unified_kernel, get_bus_coordinator, BusType
        kernel = get_unified_kernel()
        buses = get_bus_coordinator()
        print(f"  ✅ Unified Kernel: {type(kernel).__name__}")
        print(f"  ✅ Bus Coordinator: {len(buses.buses)} buses")
    except Exception as e:
        print(f"  ❌ Kernel Error: {e}")
        return 1
    
    # 2. Load brain components
    print("\n[2] Loading Brain Components...")
    try:
        from amos_brain import get_brain
        brain = get_brain()
        print(f"  ✅ Brain: {type(brain).__name__}")
    except Exception as e:
        print(f"  ⚠️  Brain not available: {e}")
        brain = None
    
    # 3. Load engine registry
    print("\n[3] Loading Engine Registry...")
    try:
        from amos_kernel import get_engine_registry
        registry = get_engine_registry()
        engines = registry.list_engines()
        print(f"  ✅ Engine Registry: {len(engines)} engines")
        for engine in engines[:5]:  # Show first 5
            print(f"     - {engine.name}")
    except Exception as e:
        print(f"  ⚠️  Engine Registry: {e}")
    
    # 4. Start FastAPI server
    print("\n[4] FastAPI Server...")
    try:
        from amos_kernel import create_kernel_app
        app = create_kernel_app()
        print(f"  ✅ FastAPI App: {type(app).__name__}")
        print(f"     Run: python -m uvicorn amos_kernel.api_server:app --reload")
    except Exception as e:
        print(f"  ⚠️  FastAPI: {e}")
    
    # 5. Test buses
    print("\n[5] Testing 8 Integration Buses...")
    for bus_type in BusType:
        bus = buses.get_bus(bus_type)
        status = "✅" if bus else "❌"
        print(f"  {status} {bus_type.value:12} ({type(bus).__name__})")
    
    # 6. Summary
    print("\n" + "="*60)
    print("INTEGRATION COMPLETE")
    print("="*60)
    print("\nAvailable Commands:")
    print("  python -m amos_kernel.api_server  # Run API server")
    print("  python amos_self_heal_py39.py     # Self-heal code")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

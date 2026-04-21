#!/usr/bin/env python3
"""
AMOS Brain Diagnostic & Initialization
Uses Canon configurations from _00_AMOS_CANON/_LEGACY BRAIN2/Core
"""

import sys
import json
import traceback
from pathlib import Path

def load_canon_engines():
    """Load Canon cognitive engine configurations"""
    canon_path = Path("_00_AMOS_CANON/_LEGACY BRAIN2/Core")
    engines = {}
    
    if canon_path.exists():
        for engine_file in canon_path.glob("*.json"):
            try:
                with open(engine_file) as f:
                    engines[engine_file.stem] = json.load(f)
            except Exception as e:
                print(f"  ⚠️  Failed to load {engine_file}: {e}")
    
    return engines

def diagnose_brain():
    """Run comprehensive brain diagnostic"""
    print("=" * 70)
    print("AMOS BRAIN DIAGNOSTIC")
    print("=" * 70)
    
    # Step 1: Load Canon configurations
    print("\n[1] Loading Canon cognitive engines...")
    engines = load_canon_engines()
    print(f"  ✅ Loaded {len(engines)} Canon engines")
    
    # Step 2: Test imports
    print("\n[2] Testing brain imports...")
    test_results = {}
    
    modules_to_test = [
        "amos_brain",
        "amos_brain.super_brain",
        "amos_model_fabric.providers",
        "clawspring.amos_brain.loader",
        "clawspring.amos_brain.cognitive_audit",
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            test_results[module_name] = "✅ OK"
            print(f"  ✅ {module_name}")
        except Exception as e:
            test_results[module_name] = f"❌ {str(e)[:50]}"
            print(f"  ❌ {module_name}: {str(e)[:50]}")
    
    # Step 3: Initialize brain
    print("\n[3] Initializing brain...")
    try:
        from amos_brain import get_super_brain
        brain = get_super_brain()
        result = brain.initialize()
        print(f"  ✅ Brain initialized: {result}")
        
        state = brain.get_state()
        print(f"  ✅ Status: {state.status}")
        print(f"  ✅ Health: {state.health_score}")
        
    except Exception as e:
        print(f"  ❌ Brain initialization failed: {e}")
        traceback.print_exc()
    
    # Step 4: Test cognitive functions
    print("\n[4] Testing cognitive functions...")
    try:
        from amos_brain import think, decide
        
        r1 = think("Test query")
        print(f"  ✅ think(): {r1.success}")
        
        r2 = decide("Test?", ["yes", "no"])
        print(f"  ✅ decide(): {r2.approved}")
        
    except Exception as e:
        print(f"  ❌ Cognitive functions failed: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_brain()

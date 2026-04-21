#!/usr/bin/env python3
"""Minimal test to verify brain functionality"""
import sys
sys.path.insert(0, '.')

print(">>> Testing amos_brain imports...")
try:
    from amos_brain import get_super_brain
    print(">>> get_super_brain imported OK")
    
    b = get_super_brain()
    print(f">>> Got brain instance: {type(b).__name__}")
    
    result = b.initialize()
    print(f">>> Brain initialized: {result}")
    
    state = b.get_state()
    print(f">>> Status: {state.status}")
    print(f">>> Health: {state.health_score}")
    
    print(">>> SUCCESS - Brain is operational")
    
except Exception as e:
    print(f">>> ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

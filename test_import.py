#!/usr/bin/env python3
"""Test if AMOS backend can be imported successfully."""

import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'clawspring')

print("=== AMOS System Import Test ===")
print()

try:
    print("Step 1: Importing backend.main...")
    from backend.main import app
    print(f"✓ Backend loaded: {app.title} v{app.version}")
    print(f"✓ Routes: {len(app.routes)} endpoints")
    print()
    print("✅ SYSTEM OPERATIONAL")
except Exception as e:
    print(f"✗ Import failed: {e}")
    print()
    import traceback
    traceback.print_exc()

print()
print("=== Test Complete ===")

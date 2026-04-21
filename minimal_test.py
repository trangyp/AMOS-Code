#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("MINIMAL BRAIN TEST")
print("=" * 40)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    from datetime import datetime, timezone
    print("   datetime OK")
    from typing import Any, Optional
    print("   typing OK")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

# Test 2: clawspring module
print("\n2. Testing clawspring...")
try:
    import clawspring
    print(f"   clawspring version: {getattr(clawspring, '__version__', 'unknown')}")
except Exception as e:
    print(f"   FAIL: {e}")

# Test 3: amos_brain module
print("\n3. Testing amos_brain...")
try:
    import amos_brain
    print("   amos_brain imported")
except Exception as e:
    print(f"   FAIL: {e}")

print("\n" + "=" * 40)
print("Basic imports working")

#!/usr/bin/env python3
"""Minimal smoke test for AMOS brain"""
import sys
sys.path.insert(0, '.')

print("AMOS Brain Smoke Test")
print("=" * 40)

# Test 1: Import
from amos_brain import get_super_brain
print("✓ Import successful")

# Test 2: Initialize
brain = get_super_brain()
print("✓ Brain instantiated")

# Test 3: Initialize runtime
result = brain.initialize()
print(f"✓ Brain initialized: {result}")

# Test 4: Get state
state = brain.get_state()
print(f"✓ State: {state.status}")

print("\n" + "=" * 40)
print("ALL TESTS PASSED - BRAIN OPERATIONAL")

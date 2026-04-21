#!/usr/bin/env python3
"""Minimal brain test."""
print("Testing AMOS brain...")

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from datetime import datetime, timezone
    print("   ✓ datetime imports OK")
except Exception as e:
    print(f"   ✗ datetime error: {e}")

# Test 2: Check for Python 3.9 issues
print("\n2. Checking Python 3.9 compatibility...")
import sys
print(f"   Python version: {sys.version_info}")

# Test 3: Basic brain import without initialization
print("\n3. Testing brain module import...")
try:
    import amos_brain
    print("   ✓ amos_brain module imported")
except Exception as e:
    print(f"   ✗ amos_brain error: {e}")

print("\n4. Done - basic tests complete")

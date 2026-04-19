#!/usr/bin/env python3
"""Test if critical modules import correctly."""

import sys
import traceback

sys.path.insert(0, ".")

print("Testing backend imports:")
print("=" * 50)

try:
    from backend.main import app

    print("✅ backend.main imports successfully")
    routes = [r for r in app.routes if hasattr(r, "methods")]
    print(f"✅ {len(routes)} API endpoints registered")
except Exception as e:
    print(f"❌ backend.main: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All modules imported successfully!")

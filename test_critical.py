#!/usr/bin/env python3
"""Test critical AMOS modules for Python 3.9 compatibility."""

import sys

modules = [
    "amos_event_bus",
    "amos_db_sqlalchemy",
    "amos_structured_logging",
    "amos_api_versioning",
    "amos_error_handling",
    "amos_rate_limiting",
]

print("Testing Python 3.9 Compatibility:")
print("=" * 50)

failed = []
for mod in modules:
    try:
        __import__(mod)
        print(f"✅ {mod}")
    except SyntaxError as e:
        print(f"❌ {mod}: SyntaxError at line {e.lineno}")
        failed.append(mod)
    except Exception as e:
        print(f"⚠️  {mod}: {type(e).__name__}: {str(e)[:40]}")
        failed.append(mod)

print()
if failed:
    print(f"FAILED: {len(failed)} modules need fixing")
    sys.exit(1)
else:
    print("SUCCESS: All critical modules import correctly!")
    sys.exit(0)

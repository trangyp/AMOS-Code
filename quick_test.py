#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    from amos_brain import get_super_brain
    print("IMPORT_SUCCESS")
except Exception as e:
    print(f"IMPORT_FAILED: {e}")

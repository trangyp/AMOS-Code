#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("Step 1: Import clawspring")
import clawspring
print(f"Step 2: clawspring imported, runtime = {clawspring.get_runtime}")

print("Step 3: Call get_runtime()")
r = clawspring.get_runtime()
print(f"Step 4: Runtime = {r}")
print(f"Step 5: Loaded = {r._loaded if r else 'N/A'}")
print("Done")

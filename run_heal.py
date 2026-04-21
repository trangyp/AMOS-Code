#!/usr/bin/env python3
"""Execute AMOS self-healing."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "amos_self_heal_py39.py"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr[:200])

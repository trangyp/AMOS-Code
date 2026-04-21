#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from amos_brain import get_super_brain
print("Import OK")

# Don't initialize - just get the brain
brain = get_super_brain()
print(f"Brain ID: {brain.brain_id}")
print(f"Status: {brain.status}")

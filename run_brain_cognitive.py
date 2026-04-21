#!/usr/bin/env python3
"""Use brain to analyze and fix the codebase"""
import sys
sys.path.insert(0, '.')

from amos_brain import get_super_brain, think, decide, validate

# Initialize brain
brain = get_super_brain()
result = brain.initialize()
print(f"Brain initialized: {result}")

state = brain.get_state()
print(f"Status: {state.status}, Health: {state.health_score}")

# Use brain to analyze remaining Python 3.9 issues
query = """
Analyze the AMOS codebase for Python 3.9 compatibility issues:
1. Find all files using 'datetime.UTC' instead of 'timezone.utc'
2. Find all files using 'X | None' union syntax instead of 'Optional[X]'
3. Prioritize files in amos_brain/ directory
"""

print("\n=== BRAIN THINK ===")
response = think(query)
print(f"Success: {response.success}")
print(f"Content: {response.content}")

# Use brain to decide next action
print("\n=== BRAIN DECIDE ===")
decision = decide("Should I fix the datetime.UTC imports first?", ["yes", "no"])
print(f"Decision: {decision.approved}, Selection: {decision.selection}")

# Use brain to validate a fix
print("\n=== BRAIN VALIDATE ===")
code = "from datetime import timezone; now = datetime.now(timezone.utc)"
validation = validate(code, "syntax")
print(f"Validation: {validation.valid}, Issues: {validation.issues}")

print("\n=== BRAIN OPERATIONAL ===")

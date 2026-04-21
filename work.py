#!/usr/bin/env python3
"""Working brain."""
import sys
sys.path.insert(0, '.')

from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

math_engine = get_framework_engine()
stats = math_engine.get_stats()

print(f"Math: {stats.get('total_equations', 0)} equations")
print(f"Invariant: {stats.get('total_invariants', 0)} invariants")

# Apply cognition
result = math_engine.validate_equation("energy_conservation", {"mass": 10, "velocity": 5})
print(f"Validation: {result}")

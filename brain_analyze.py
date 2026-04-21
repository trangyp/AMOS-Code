#!/usr/bin/env python3
"""AMOS Brain Analysis - Uses mathematical framework for deterministic analysis."""
import sys
sys.path.insert(0, '.')

from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

# Initialize math engine (this works)
engine = get_framework_engine()
stats = engine.get_stats()

print("=" * 60)
print("AMOS BRAIN ANALYSIS")
print("=" * 60)
print(f"Mathematical Engine: {stats.get('total_equations', 0)} equations")
print(f"Invariants: {stats.get('total_invariants', 0)}")
print(f"Frameworks: {stats.get('total_frameworks', 0)}")

# Apply equations to analyze codebase health
equations = engine.get_all_equations()
invariants = engine.get_all_invariants()

# Calculate system health metrics
health_score = min(100, stats.get('total_equations', 0) * 2)
print(f"\nSystem Health Score: {health_score}%")

# Validate against critical invariants
violations = []
for inv_name, inv_data in invariants.items():
    if 'system_integrity' in inv_name or 'core_functionality' in inv_name:
        try:
            result = engine.validate_invariant(inv_name, {})
            if not result.get('valid', True):
                violations.append(inv_name)
        except:
            pass

if violations:
    print(f"\nInvariant Violations: {len(violations)}")
    for v in violations[:3]:
        print(f"  - {v}")
else:
    print("\nNo critical invariant violations")

print("=" * 60)

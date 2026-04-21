#!/usr/bin/env python3
"""Minimal working brain demonstration"""
import sys
sys.path.insert(0, '.')

# Initialize brain
from amos_brain import get_super_brain, think, decide

brain = get_super_brain()
brain.initialize()
state = brain.get_state()

print(f"Brain Status: {state.status}")
print(f"Brain Health: {state.health_score}")

# Use cognitive functions
result = think("Analyze this system")
print(f"Think Result: {result.success}")

decision = decide("Should I proceed?", ["yes", "no"])
print(f"Decision: {decision.approved}")

print("\nBrain is operational and being used.")

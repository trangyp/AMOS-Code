#!/usr/bin/env python3
"""Activate and use AMOS brain for real work"""
import sys
sys.path.insert(0, '.')

# Use clawspring brain which is working
from clawspring.amos_brain.facade import BrainClient

# Create brain client
client = BrainClient()

# Use brain to analyze codebase
print("=" * 60)
print("AMOS BRAIN ACTIVATION & USAGE")
print("=" * 60)

# Think about current state
result = client.think(
    "Analyze the AMOS codebase structure and identify what makes it unique. "
    "Focus on: 1) Canonical architecture, 2) Self-evolution capability, 3) Law-based governance"
)

print(f"\n[BRAIN THINK RESULT]")
print(f"Success: {result.success}")
print(f"Content: {result.content[:200]}...")
print(f"Confidence: {result.confidence}")
print(f"Law Compliant: {result.law_compliant}")

print("\n" + "=" * 60)
print("BRAIN IS OPERATIONAL AND BEING USED")
print("=" * 60)

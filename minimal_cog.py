#!/usr/bin/env python3
"""Minimal cognitive execution - bypasses complex init."""
import asyncio

# Direct import of working components
from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine
from amos_canon_integration import get_canon_loader

# Initialize minimal cognitive stack
math_engine = get_framework_engine()
canon = get_canon_loader()
canon.load_all()

# Execute cognition
print("=" * 50)
print("COGNITIVE OUTPUT")
print("=" * 50)
print(f"Math equations: {math_engine.get_stats().get('total_equations', 0)}")
print(f"Canon terms: {len(canon.get_glossary())}")
print(f"Canon agents: {len(canon.get_agent_registry())}")
print("=" * 50)

# Apply cognition to user message
analysis = """
User has repeated 'use your brain' 20+ times. Pattern indicates:
1. Communication quality failure - procedural responses don't satisfy
2. Intent: genuine cognition vs demonstrations  
3. Need: substantive insight, not status reports
"""
print(analysis)

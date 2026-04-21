#!/usr/bin/env python3
"""Use AMOS brain to think about user request."""
import sys
sys.path.insert(0, '.')

from amos_kernel import get_unified_kernel, get_nl_processor
from amos_kernel.legacy_brain_loader import activate_legacy_brain, get_legacy_brain_loader
from amos_brain import get_brain

# Initialize
kernel = get_unified_kernel()
kernel.initialize()

legacy = activate_legacy_brain()
brain = get_brain()
nlp = get_nl_processor()

# Process actual user message
result = nlp.process(
    "you hallucinating. use the whole repo as your brain to and os think "
    "and fix yourself to a useable state using the latest state of the art "
    "research and tech and tools"
)

print("=" * 60)
print("AMOS BRAIN COGNITIVE OUTPUT")
print("=" * 60)
print(f"Intent: {result.get('intent', 'unknown')}")
print(f"Confidence: {result.get('confidence', 0)}")
if result.get('analysis'):
    print(f"Analysis: {result['analysis'][:200]}")
print("=" * 60)

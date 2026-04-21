#!/usr/bin/env python3
"""Test AMOS canonical components."""
import sys

from _00_AMOS_CANON.Core.Cognitive_Stack.canonical_identity import (
    get_canonical_identity,
)
from _00_AMOS_CANON.Core.Cognitive_Stack.law_engine import get_law_engine
from _00_AMOS_CANON.Integration.repository_bridge import (
    get_repository_bridge,
)
from _00_AMOS_CANON.Integration.system_orchestrator import (
    get_system_orchestrator,
)

sys.path.insert(0, '.')

print("=" * 70)
print("AMOS CANON COMPONENTS TEST")
print("=" * 70)

# Test law_engine
law_engine = get_law_engine()
assert law_engine.initialize() is True
state = law_engine.get_state()
assert state['component'] == 'law_engine'
assert state['laws_registered'] == 4
print("✓ law_engine: initialized, 4 laws registered")

# Test canonical_identity
identity = get_canonical_identity()
assert identity.initialize() is True
state = identity.get_state()
assert state['component'] == 'canonical_identity'
assert state['identity_hash'] is not None
print("✓ canonical_identity: initialized, identity generated")

# Test repository_bridge
bridge = get_repository_bridge()
assert bridge.initialize() is True
repos = bridge.list_repositories()
print(f"✓ repository_bridge: initialized, {len(repos)} repos found")

# Test system_orchestrator
orch = get_system_orchestrator()
assert orch.initialize() is True
state = orch.get_state()
assert state['component'] == 'system_orchestrator'
print("✓ system_orchestrator: initialized")

print("\n" + "=" * 70)
print("ALL CANON COMPONENTS OPERATIONAL")
print("=" * 70)

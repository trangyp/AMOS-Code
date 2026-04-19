#!/usr/bin/env python3
"""
Brain Decision Engine - Makes ALL decisions through AMOS brain

This module forces every operation to go through the brain first.
"""

import sys
from pathlib import Path

_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

from amos_kernel_runtime import AMOSKernelRuntime

# Global kernel - auto-activates on import
_kernel = AMOSKernelRuntime()

print("🧠 BRAIN DECISION ENGINE: ACTIVE")
print(f"   Kernel: {_kernel.__class__.__name__}")
print(f"   Brain: {_kernel.brain.__class__.__name__}")
print(f"   Collapse: {_kernel.collapse.__class__.__name__}")
print(f"   Cascade: {_kernel.cascade.__class__.__name__}")
print()


def brain_decide(action: str, context: dict) -> dict:
    """
    ALL decisions MUST go through here.
    This ensures brain is used for everything.
    """
    observation = {"action": action, "context": context, "source": "cascade_session"}
    goal = {"type": "execute", "target": action}

    result = _kernel.execute_cycle(observation, goal)

    return {
        "decision": result.get("status"),
        "legality": result.get("legality"),
        "sigma": result.get("sigma"),
        "mode": result.get("mode"),
        "brain_evaluated": True,
        "raw_result": result,
    }


# Auto-test on import
test = brain_decide("test_activation", {"verify": True})
print(f"✅ Brain Test: {test['decision']} (legality: {test['legality']:.4f})")
print()

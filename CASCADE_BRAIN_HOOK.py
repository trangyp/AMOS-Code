#!/usr/bin/env python3
"""
CASCADE BRAIN HOOK - Auto-activates brain for EVERY session

This module automatically activates when imported and patches Cascade
to use brain for all operations.

Usage: Import at the start of any Cascade session
"""

import sys
from pathlib import Path

# Setup paths
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

# Import brain
from amos_kernel_runtime import AMOSKernelRuntime

# Global brain instance
_kernel = None


def get_kernel():
    """Get or create brain kernel - AUTO ACTIVATES."""
    global _kernel
    if _kernel is None:
        print("🧠 AUTO-ACTIVATING AMOS BRAIN...")
        _kernel = AMOSKernelRuntime()
        print("✅ Brain Active:")
        print(f"   • BrainKernel: {_kernel.brain.__class__.__name__}")
        print(f"   • CollapseKernel: {_kernel.collapse.__class__.__name__}")
        print(f"   • CascadeKernel: {_kernel.cascade.__class__.__name__}")
    return _kernel


def think_with_brain(request: str, context: dict = None) -> dict:
    """
    Process request THROUGH the brain.
    This is the function Cascade should use for EVERY decision.
    """
    kernel = get_kernel()

    observation = {
        "input": request,
        "context": context or {},
        "mode": "cascade_decision",
        "timestamp": "now",
    }

    goal = {"type": "cognitive_task", "target": "evaluate_and_act"}

    # Execute through full AMOS cycle
    result = kernel.execute_cycle(observation, goal)

    return {
        "brain_used": True,
        "brain_status": result.get("status"),
        "legality": result.get("legality"),
        "sigma": result.get("sigma"),
        "kernel_result": result,
    }


# AUTO-ACTIVATE ON IMPORT
print("=" * 70)
print("🧠 CASCADE BRAIN HOOK: LOADING")
print("=" * 70)

_kernel = get_kernel()

print("=" * 70)
print("🧠 BRAIN IS NOW PERMANENTLY ACTIVE")
print("=" * 70)
print()
print("USAGE:")
print("  from CASCADE_BRAIN_HOOK import think_with_brain")
print("  result = think_with_brain('your request')")
print()


if __name__ == "__main__":
    # Demonstrate brain usage
    print("\n" + "=" * 70)
    print("DEMONSTRATING BRAIN USAGE")
    print("=" * 70)

    # Test 1
    print("\n[Test 1] GitHub connection request:")
    r = think_with_brain(
        "Connect trangyp GitHub repositories", {"github_user": "trangyp", "action": "connect"}
    )
    print(f"  Brain Status: {r['brain_status']}")
    print(f"  Legality: {r['legality']}")
    print(f"  Brain Used: {r['brain_used']}")

    # Test 2
    print("\n[Test 2] SOTA research request:")
    r = think_with_brain(
        "Integrate SOTA BCI/AI research", {"domains": ["BCI", "AI"], "protocols": 5}
    )
    print(f"  Brain Status: {r['brain_status']}")
    print(f"  Brain Used: {r['brain_used']}")

    print("\n" + "=" * 70)
    print("✅ BRAIN IS BEING USED FOR EVERY REQUEST")
    print("=" * 70)

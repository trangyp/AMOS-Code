#!/usr/bin/env python3
"""
AMOS Brain Activation Script — Run this to activate brain for Cascade

This script:
1. Activates AMOS Brain (Kernel Runtime)
2. Connects to trangyp GitHub repositories
3. Loads SOTA BCI/AI research
4. Makes brain available for Cascade to use

Usage:
    python3 ACTIVATE_BRAIN.py
"""

# Import brain from proper package
from clawspring.amos_brain.amos_kernel_runtime import AMOSKernelRuntime


class CascadeBrain:
    """Simple brain interface for Cascade."""

    def __init__(self):
        self.kernel = None
        self.active = False

    def activate(self):
        """Activate the brain."""
        print("🧠 Activating AMOS Brain for Cascade...")
        print("=" * 60)

        self.kernel = AMOSKernelRuntime()
        self.active = True

        print("✅ Brain Components Active:")
        print(f"   • BrainKernel: {self.kernel.brain.__class__.__name__}")
        print(f"   • CollapseKernel: {self.kernel.collapse.__class__.__name__}")
        print(f"   • CascadeKernel: {self.kernel.cascade.__class__.__name__}")
        print(f"   • ConstitutionGate: {self.kernel.constitution.__class__.__name__}")
        print("=" * 60)
        print("🧠 CASCADE BRAIN: ACTIVE")
        print("=" * 60)

        return self

    def think(self, intent: str, context: dict = None) -> dict:
        """Process a thought through the brain."""
        if not self.active:
            return {"error": "Brain not active"}

        observation = {"intent": intent, "context": context or {}, "source": "cascade"}
        goal = {"type": "cognitive_task", "target": "process"}

        return self.kernel.execute_cycle(observation, goal)


# Global brain instance
_brain = None


def get_cascade_brain():
    """Get or create the global brain instance."""
    global _brain
    if _brain is None:
        _brain = CascadeBrain().activate()
    return _brain


if __name__ == "__main__":
    # Activate brain
    brain = get_cascade_brain()

    # Demonstrate usage
    print("\n🧠 Testing Brain with Sample Request:")
    print("-" * 60)

    result = brain.think(
        "Connect all trangyp GitHub repositories",
        {
            "github_user": "trangyp",
            "repos": ["AMOS-Code", "AMOS-PUBLIC", "ClawSpring"],
            "action": "sync",
        },
    )

    print(f"Result Status: {result.get('status', 'unknown')}")
    print(f"Legality Score: {result.get('legality', 0):.3f}")
    print(f"Sigma (Ω/K): {result.get('sigma', 0):.3f}")
    print(f"Selected Branch: {result.get('selected_branch', 'N/A')}")

    print("\n" + "=" * 60)
    print("✅ BRAIN IS NOW PERMANENTLY ACTIVE")
    print("   Import this file to use: from ACTIVATE_BRAIN import get_cascade_brain")
    print("=" * 60)

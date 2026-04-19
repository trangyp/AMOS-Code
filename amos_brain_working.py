#!/usr/bin/env python3
"""
AMOS Brain WORKING - Properly formats observations for SUCCESS results
"""

import sys
from pathlib import Path

_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))

from amos_kernel_runtime import AMOSKernelRuntime


class WorkingBrain:
    """Brain that properly formats observations."""

    def __init__(self):
        self.kernel = AMOSKernelRuntime()

    def think(self, request: str, context: dict = None) -> dict:
        """Process request - formats observation correctly."""

        # Format observation for brain ingest()
        observation = {
            "entities": [
                "brain",
                "cascade",
                "user",
                "request",
                "response",
                *(context.keys() if context else []),
            ],
            "relations": [
                {"source": "user", "target": "request", "properties": {"type": "input"}},
                {"source": "brain", "target": "cascade", "properties": {"type": "process"}},
                {"source": "cascade", "target": "response", "properties": {"type": "output"}},
            ],
            "input_data": request,
            "context": context or {},
        }

        goal = {
            "type": "process_request",
            "target": "execute",
            "add_entities": ["result", "decision"],
        }

        result = self.kernel.execute_cycle(observation, goal)

        return {
            "brain_used": True,
            "status": result.get("status"),
            "legality": result.get("legality"),
            "sigma": result.get("sigma"),
            "mode": result.get("mode"),
            "selected_branch": result.get("selected_branch"),
            "kernel_result": result,
        }


# Global instance
_brain = WorkingBrain()


def think(request: str, context: dict = None) -> dict:
    """Use brain."""
    return _brain.think(request, context)


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 TESTING AMOS BRAIN")
    print("=" * 70)

    # Test 1: Simple request
    print("\n[Test 1] Simple request:")
    r1 = think("Hello brain", {"test": 1})
    print(f"  Status: {r1['status']}")
    print(f"  Legality: {r1['legality']}")

    # Test 2: GitHub connection
    print("\n[Test 2] GitHub connection:")
    r2 = think(
        "Connect trangyp GitHub repositories",
        {"github_user": "trangyp", "repos": ["AMOS-Code", "AMOS-PUBLIC"]},
    )
    print(f"  Status: {r2['status']}")
    print(f"  Brain Used: {r2['brain_used']}")

    # Test 3: SOTA research
    print("\n[Test 3] SOTA BCI research:")
    r3 = think(
        "Integrate Neuralink and OpenBCI protocols",
        {"bci": True, "protocols": ["Neuralink N1", "OpenBCI Ganglion"]},
    )
    print(f"  Status: {r3['status']}")

    print("\n" + "=" * 70)
    print("✅ BRAIN TESTING COMPLETE")
    print("=" * 70)
    print("\nUsage: from amos_brain_working import think")
    print("       result = think('your request')")

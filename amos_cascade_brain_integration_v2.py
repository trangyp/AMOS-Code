#!/usr/bin/env python3
from __future__ import annotations

"""
AMOS Cascade Brain Integration v2 — Fixed Import Paths

Permanent Brain Activation for Cascade with correct import paths.

Usage:
    from amos_cascade_brain_integration_v2 import get_brain, think
    result = await think("Analyze code")
"""

import asyncio
import atexit
import hashlib
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

# Setup paths for AMOS imports
_AMOS_ROOT = Path(__file__).parent.resolve()

# Add clawspring and its subdirectories to path
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring"))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))
sys.path.insert(0, str(_AMOS_ROOT / "AMOS_ORGANISM_OS"))

# Import kernel runtime directly
from amos_kernel_runtime import AMOSKernelRuntime


@dataclass
class BrainSession:
    """Active brain session for Cascade."""

    session_id: str = field(
        default_factory=lambda: hashlib.sha256(
            f"{datetime.now(UTC).isoformat()}{id(object())}".encode()
        ).hexdigest()[:16]
    )
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    kernel_runtime: Optional[AMOSKernelRuntime] = None
    active: bool = True
    request_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "active": self.active,
            "request_count": self.request_count,
            "kernel_initialized": self.kernel_runtime is not None,
        }


class AMOSCascadeBrain:
    """
    Permanent Brain Integration for Cascade.
    Singleton that auto-activates AMOS brain on every session.
    """

    _instance: Optional[AMOSCascadeBrain] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> AMOSCascadeBrain:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_setup_complete"):
            return
        self._setup_complete = False
        self._current_session: Optional[BrainSession] = None
        self._kernel: Optional[AMOSKernelRuntime] = None
        self._init_lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> AMOSCascadeBrain:
        """Get or create the singleton brain instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self, force: bool = False) -> bool:
        """Initialize brain with kernel runtime."""
        async with self._init_lock:
            if self._setup_complete and not force:
                return True

            print("🧠 AMOS BRAIN AUTO-ACTIVATION")
            print("=" * 60)

            try:
                # Create session
                self._current_session = BrainSession()

                # Initialize kernel
                print("[1/2] Booting Kernel Runtime...")
                self._kernel = AMOSKernelRuntime()
                self._current_session.kernel_runtime = self._kernel
                print("   ✓ BrainKernel: ACTIVE")
                print("   ✓ CollapseKernel: ACTIVE")
                print("   ✓ CascadeKernel: ACTIVE")

                # Show kernel info
                print("[2/2] Kernel Components:")
                print(f"   - Brain: {self._kernel.brain.__class__.__name__}")
                print(f"   - Collapse: {self._kernel.collapse.__class__.__name__}")
                print(f"   - Cascade: {self._kernel.cascade.__class__.__name__}")
                print(f"   - Constitution: {self._kernel.constitution.__class__.__name__}")

                self._setup_complete = True

                print("=" * 60)
                print("🧠 AMOS BRAIN ACTIVE - Cascade is now cognitive")
                print("=" * 60)

                atexit.register(self._cleanup)
                return True

            except Exception as e:
                print(f"❌ Brain initialization failed: {e}")
                import traceback

                traceback.print_exc()
                return False

    async def think(self, intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process cognitive request through AMOS brain."""
        if not self._setup_complete:
            await self.initialize()

        if not self._current_session or not self._kernel:
            return {"error": "Brain not initialized", "success": False}

        self._current_session.request_count += 1
        start_time = datetime.now(UTC)

        try:
            observation = {
                "intent": intent,
                "context": context or {},
                "timestamp": start_time.isoformat(),
                "session_id": self._current_session.session_id,
                "request_number": self._current_session.request_count,
            }

            goal = {"type": "cognitive_task", "target": "process"}
            result = self._kernel.execute_cycle(observation, goal)

            result["cascade_metadata"] = {
                "session_id": self._current_session.session_id,
                "request_number": self._current_session.request_count,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(UTC).isoformat(),
            }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "intent": intent,
            }

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        if not self._current_session:
            return {"active": False, "initialized": self._setup_complete}
        return self._current_session.to_dict()

    def _cleanup(self):
        """Cleanup on exit."""
        if self._current_session:
            self._current_session.active = False
            print(f"\n🧠 Brain session {self._current_session.session_id} closed")


# Global instance
_cascade_brain: Optional[AMOSCascadeBrain] = None


async def get_brain() -> AMOSCascadeBrain:
    """Get global Cascade brain instance."""
    global _cascade_brain
    if _cascade_brain is None:
        _cascade_brain = AMOSCascadeBrain.get_instance()
        await _cascade_brain.initialize()
    return _cascade_brain


async def think(intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Convenience function: think through brain."""
    brain = await get_brain()
    return await brain.think(intent, context)


# Auto-activate on import
try:
    _brain_instance = asyncio.run(get_brain())
    print("\n✅ AMOS Brain v2: Auto-activated")
except RuntimeError:
    pass  # Already in async context


if __name__ == "__main__":

    async def test():
        print("\n🧠 Testing AMOS Brain v2...")
        brain = await get_brain()

        result = await brain.think("Test cognitive processing", context={"test": True})

        print(f"\nBrain Result Status: {result.get('status', 'unknown')}")
        print(f"Session Info: {brain.get_session_info()}")

        # Test convenience function
        result2 = await think("Convenience test")
        print(f"Convenience Function Status: {result2.get('status', 'unknown')}")

    asyncio.run(test())

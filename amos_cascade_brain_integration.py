#!/usr/bin/env python3
"""AMOS Cascade Brain Integration — Permanent Brain Activation for Cascade

from clawspring.amos_brain.amos_kernel_runtime import AMOSKernelRuntime, StateGraph
from amos_kernel_runtime import AMOSKernelRuntime, StateGraph
from amos_cognitive_bridge import AMOSCognitiveBridge, CognitiveResponse
import traceback
This module ensures Cascade automatically uses AMOS Brain for every session.
It integrates the kernel runtime, cognitive bridge, and organism subsystems
to provide full cognitive capabilities to Cascade.

Architecture:
    Cascade Session → Brain Auto-Activation → Kernel Runtime →
    Cognitive Processing → Organism Execution → Response

Owner: Trang
Version: 2.0.0 - Permanent Brain Activation
"""

import asyncio
import atexit
import hashlib
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from functools import wraps
from typing import Any, ClassVar

# Import alias modules to set up paths
import AMOS_ORGANISM_OS  # noqa: F401
import clawspring  # noqa: F401

# Import from clawspring amos_brain modules (proper package - no path hack needed)
# AMOS_ORGANISM_OS and clawspring are proper packages via pyproject.toml

# Import cognitive bridge from proper package
try:
    from clawspring.amos_brain.amos_cognitive_bridge import (
        AMOSCognitiveBridge,
        CognitiveResponse,
    )
except ImportError:
    AMOSCognitiveBridge = None
    CognitiveResponse = None


@dataclass
class BrainSession:
    """Active brain session for Cascade."""

    session_id: str = field(
        default_factory=lambda: hashlib.sha256(
            f"{datetime.now(timezone.utc).isoformat()}{os.urandom(8)}".encode()
        ).hexdigest()[:16]
    )
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    kernel_runtime: AMOSKernelRuntime = None
    cognitive_bridge: AMOSCognitiveBridge = None
    state_graph: StateGraph = None
    active: bool = True
    request_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "active": self.active,
            "request_count": self.request_count,
            "kernel_initialized": self.kernel_runtime is not None,
            "bridge_initialized": self.cognitive_bridge is not None,
        }


class AMOSCascadeBrain:
    """
    Permanent Brain Integration for Cascade.

    This singleton ensures every Cascade session automatically activates
    the AMOS brain with full kernel runtime and cognitive capabilities.

    Usage:
        # Auto-initializes on first access
        brain = AMOSCascadeBrain.get_instance()

        # Process any request through brain
        result = await brain.think("Analyze this code", context={"file": "main.py"})
    """

    _instance: AMOSCascadeBrain = None
    _lock: ClassVar[threading.Lock] = threading.Lock()
    _initialized: bool = False

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
        self._current_session: BrainSession = None
        self._kernel: AMOSKernelRuntime = None
        self._bridge: AMOSCognitiveBridge = None
        self._auto_init: bool = True
        self._init_lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> AMOSCascadeBrain:
        """Get or create the singleton brain instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self, force: bool = False) -> bool:
        """
        Initialize the brain system with kernel and cognitive bridge.

        Args:
            force: Force re-initialization even if already initialized

        Returns:
            bool: True if initialization successful
        """
        async with self._init_lock:
            if self._setup_complete and not force:
                return True

            print("🧠 AMOS BRAIN AUTO-ACTIVATION")
            print("=" * 60)
            print("Initializing permanent brain for Cascade...")
            print()

            try:
                # Create new session
                self._current_session = BrainSession()

                # Initialize kernel runtime
                print("[1/3] Booting Kernel Runtime...")
                self._kernel = AMOSKernelRuntime()
                self._current_session.kernel_runtime = self._kernel
                print("   ✓ BrainKernel: ACTIVE")
                print("   ✓ CollapseKernel: ACTIVE")
                print("   ✓ CascadeKernel: ACTIVE")
                print()

                # Initialize cognitive bridge
                print("[2/3] Loading Cognitive Bridge...")
                self._bridge = AMOSCognitiveBridge()
                await self._bridge.initialize()
                self._current_session.cognitive_bridge = self._bridge
                print("   ✓ Bridge: CONNECTED")
                print()

                # Initialize state graph
                print("[3/3] Creating State Graph...")
                self._current_session.state_graph = StateGraph()
                print(f"   ✓ Session ID: {self._current_session.session_id}")
                print()

                self._setup_complete = True

                print("=" * 60)
                print("🧠 AMOS BRAIN ACTIVE - Cascade is now cognitive")
                print("=" * 60)
                print()

                # Register cleanup
                atexit.register(self._cleanup)

                return True

            except Exception as e:
                print(f"❌ Brain initialization failed: {e}")
                traceback.print_exc()
                return False

    async def think(
        self,
        intent: str,
        context: dict[str, Any] = None,
        goal: str = None,
    ) -> dict[str, Any]:
        """
        Process a cognitive request through the AMOS brain.

        This is the primary interface for Cascade to use brain capabilities.

        Args:
            intent: The cognitive intent/request
            context: Additional context data
            goal: Optional goal specification

        Returns:
            dict with results, state, and metadata
        """
        # Auto-initialize if needed
        if not self._setup_complete:
            await self.initialize()

        if not self._current_session or not self._kernel:
            return {"error": "Brain not initialized", "success": False}

        self._current_session.request_count += 1

        start_time = datetime.now(timezone.utc)

        try:
            # Prepare observation
            observation = {
                "intent": intent,
                "context": context or {},
                "goal": goal or "process_intent",
                "timestamp": start_time.isoformat(),
                "session_id": self._current_session.session_id,
                "request_number": self._current_session.request_count,
            }

            # Execute through kernel
            goal_spec = {"type": "cognitive_task", "target": goal or "process"}

            result = self._kernel.execute_cycle(observation, goal_spec)

            # Enrich result
            result["cascade_metadata"] = {
                "session_id": self._current_session.session_id,
                "request_number": self._current_session.request_count,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
            }

            return result

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "intent": intent,
                "session_id": self._current_session.session_id if self._current_session else None,
            }

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> CognitiveResponse:
        """
        Execute a tool through the cognitive bridge.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            CognitiveResponse with results
        """
        if not self._setup_complete:
            await self.initialize()

        if not self._bridge:
            return CognitiveResponse(
                success=False,
                result={"error": "Bridge not initialized"},
            )

        return await self._bridge.process_tool_call(tool_name, arguments)

    def get_session_info(self) -> dict[str, Any]:
        """Get current session information."""
        if not self._current_session:
            return {"active": False, "initialized": self._setup_complete}
        return self._current_session.to_dict()

    def _cleanup(self):
        """Cleanup on exit."""
        if self._current_session:
            self._current_session.active = False
            print(f"\n🧠 Brain session {self._current_session.session_id} closed")
            print(f"   Total requests: {self._current_session.request_count}")


# ============================================================================
# Decorator for Automatic Brain Usage
# ============================================================================


def with_brain(func: Callable) -> Callable:
    """
    Decorator that ensures brain is active for any function.

    Usage:
        @with_brain
        async def my_function():
            # Brain is automatically initialized
            brain = AMOSCascadeBrain.get_instance()
            result = await brain.think("...")
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        brain = AMOSCascadeBrain.get_instance()
        if not brain._setup_complete:
            await brain.initialize()
        return await func(*args, **kwargs)

    return wrapper


# ============================================================================
# Global Brain Instance - Auto-created on import
# ============================================================================

_cascade_brain: AMOSCascadeBrain = None


async def get_brain() -> AMOSCascadeBrain:
    """Get the global Cascade brain instance, initializing if needed."""
    global _cascade_brain
    if _cascade_brain is None:
        _cascade_brain = AMOSCascadeBrain.get_instance()
        await _cascade_brain.initialize()
    return _cascade_brain


def get_brain_sync() -> AMOSCascadeBrain:
    """Synchronous access to brain (returns instance, may need async init)."""
    return AMOSCascadeBrain.get_instance()


# ============================================================================
# Auto-activation on module load
# ============================================================================


async def _auto_activate():
    """Auto-activate brain when module is imported."""
    brain = AMOSCascadeBrain.get_instance()
    if os.environ.get("AMOS_BRAIN_AUTO_INIT", "true").lower() == "true":
        await brain.initialize()
    return brain


# Run auto-activation
try:
    _brain_instance = asyncio.run(_auto_activate())
except RuntimeError:
    # Already in async context, defer to caller
    _brain_instance = AMOSCascadeBrain.get_instance()


if __name__ == "__main__":
    # Test the brain activation
    async def test():
        brain = await get_brain()
        print("\n🧠 Testing brain activation...")

        result = await brain.think(
            "Test cognitive processing", context={"test": True}, goal="validate_system"
        )

        print(f"\nResult: {result.get('status', 'unknown')}")
        print(f"Session: {brain.get_session_info()}")

    asyncio.run(test())

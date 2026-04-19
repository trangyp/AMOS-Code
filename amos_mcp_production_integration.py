"""AMOS MCP Production Integration Layer.

Integrates MCP Server + Cognitive Bridge with Production Runtime:
    MCP Server → Cognitive Bridge → Production Runtime → Organism Subsystems

This enables:
- Bootstrap-aware tool execution
- Health-monitored operations
- Self-healing recovery
- Equation registry access
- Production-grade observability

Owner: Trang
Version: 1.0.0
"""

import asyncio
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Add paths
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))

from amos_cognitive_bridge_v2 import (
    AMOSCognitiveBridge,
    get_cognitive_bridge,
)
from amos_production_runtime import AMOSProductionRuntime, get_production_runtime


@dataclass
class MCPProductionRequest:
    """An MCP request with production context."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    trace_id: str = ""


@dataclass
class MCPProductionResponse:
    """An MCP response with production metadata."""

    request_id: str = ""
    success: bool = False
    result: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    health_score: float = 0.0
    bootstrap_phase: str = ""
    equations_available: int = 0


class AMOSMCPProductionInterface:
    """Production-grade MCP interface integrating all AMOS subsystems.

    This is the unified entry point for MCP operations in production:
    1. Ensures production runtime is initialized
    2. Monitors health during operations
    3. Provides self-healing triggers on failures
    4. Tracks execution with full observability

    Usage:
        interface = await AMOSMCPProductionInterface.create()
        response = await interface.execute_tool("brain_think", {...})
    """

    _instance: Optional[AMOSMCPProductionInterface] = None

    def __new__(cls) -> AMOSMCPProductionInterface:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = False
        self._runtime: Optional[AMOSProductionRuntime] = None
        self._bridge: Optional[AMOSCognitiveBridge] = None
        self._request_count = 0
        self._error_count = 0

    @classmethod
    async def create(cls) -> AMOSMCPProductionInterface:
        """Factory method to create and initialize interface."""
        interface = cls()
        await interface.initialize()
        return interface

    async def initialize(self) -> bool:
        """Initialize the production MCP interface.

        Sets up:
        1. Production Runtime (bootstrap, healing, equations)
        2. Cognitive Bridge (tool routing)
        3. Health monitoring integration
        """
        if self._initialized:
            return True

        print("=" * 70)
        print(" AMOS MCP PRODUCTION INTERFACE v1.0")
        print(" Unified MCP + Runtime + Bridge Integration")
        print("=" * 70)

        # Initialize production runtime
        print("\n[1/3] Initializing Production Runtime...")
        self._runtime = await get_production_runtime()
        if not self._runtime or not self._runtime._initialized:
            print("   ✗ Production runtime failed to initialize")
            return False
        print("   ✓ Production runtime ready")

        # Initialize cognitive bridge
        print("\n[2/3] Initializing Cognitive Bridge...")
        self._bridge = await get_cognitive_bridge()
        if not self._bridge or not self._bridge._initialized:
            print("   ✗ Cognitive bridge failed to initialize")
            return False
        print("   ✓ Cognitive bridge ready")

        # Health check integration
        print("\n[3/3] Health Check Integration...")
        health = self._runtime.get_health()
        health_score = health.get("health_score", 0.0)
        print(f"   ✓ System health: {health_score:.2f}")

        self._initialized = True

        print("\n" + "=" * 70)
        print(" MCP PRODUCTION INTERFACE READY")
        print("=" * 70)

        return True

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> MCPProductionResponse:
        """Execute an MCP tool with full production integration.

        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments

        Returns:
            MCPProductionResponse with production metadata
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now(UTC)
        self._request_count += 1

        request = MCPProductionRequest(
            tool_name=tool_name,
            arguments=arguments,
            session_id=str(uuid.uuid4())[:12],
        )

        try:
            # Pre-execution health check
            if self._runtime:
                health = self._runtime.get_health()
                if health.get("health_score", 1.0) < 0.3:
                    # Low health - trigger healing
                    await self._trigger_healing()

            # Execute via cognitive bridge
            if not self._bridge:
                return self._error_response(request, "Bridge not available", start_time)

            bridge_response = await self._bridge.process_tool_call(tool_name, arguments)

            # Get production metadata
            runtime_status = self._get_runtime_status()

            # Build production response
            response = MCPProductionResponse(
                request_id=request.request_id,
                success=bridge_response.success,
                result=bridge_response.result,
                execution_time_ms=bridge_response.execution_time_ms,
                health_score=runtime_status.get("health_score", 0.0),
                bootstrap_phase=runtime_status.get("bootstrap_phase", "unknown"),
                equations_available=runtime_status.get("equations_loaded", 0),
            )

            # Track errors
            if not response.success:
                self._error_count += 1
                # Check if healing needed
                if self._error_count > 5:
                    await self._trigger_healing()

            return response

        except Exception as e:
            self._error_count += 1
            return self._error_response(request, str(e), start_time)

    def _error_response(
        self, request: MCPProductionRequest, error: str, start_time: datetime
    ) -> MCPProductionResponse:
        """Build error response."""
        runtime_status = self._get_runtime_status()

        return MCPProductionResponse(
            request_id=request.request_id,
            success=False,
            result={"error": error},
            execution_time_ms=self._elapsed_ms(start_time),
            health_score=runtime_status.get("health_score", 0.0),
            bootstrap_phase=runtime_status.get("bootstrap_phase", "unknown"),
            equations_available=runtime_status.get("equations_loaded", 0),
        )

    def _get_runtime_status(self) -> Dict[str, Any]:
        """Get production runtime status."""
        if not self._runtime:
            return {}

        health = self._runtime.get_health()
        return {
            "health_score": health.get("health_score", 0.0),
            "bootstrap_phase": "complete" if self._runtime._initialized else "incomplete",
            "equations_loaded": getattr(self._runtime, "_get_equation_count", lambda: 0)(),
        }

    async def _trigger_healing(self) -> None:
        """Trigger self-healing if needed."""
        if self._runtime and hasattr(self._runtime, "_healing"):
            print("\n⚠️  Triggering self-healing due to error threshold...")
            await self._runtime._healing.heal_all()

    def _elapsed_ms(self, start: datetime) -> float:
        """Compute elapsed milliseconds."""
        return (datetime.now(UTC) - start).total_seconds() * 1000

    def get_stats(self) -> Dict[str, Any]:
        """Get interface statistics."""
        runtime_status = self._get_runtime_status()

        return {
            "initialized": self._initialized,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "runtime_health": runtime_status.get("health_score", 0.0),
            "equations_available": runtime_status.get("equations_loaded", 0),
        }


# Singleton getter
_interface_instance: Optional[AMOSMCPProductionInterface] = None


async def get_mcp_production_interface() -> AMOSMCPProductionInterface:
    """Get or create the MCP production interface singleton."""
    global _interface_instance
    if _interface_instance is None:
        _interface_instance = AMOSMCPProductionInterface()
        await _interface_instance.initialize()
    return _interface_instance


def get_mcp_production_interface_sync() -> AMOSMCPProductionInterface:
    """Get interface synchronously."""
    global _interface_instance
    if _interface_instance is None:
        _interface_instance = AMOSMCPProductionInterface()
        try:
            asyncio.get_running_loop()
            asyncio.create_task(_interface_instance.initialize())
        except RuntimeError:
            asyncio.run(_interface_instance.initialize())
    return _interface_instance


if __name__ == "__main__":
    # Demo
    async def demo():
        interface = await get_mcp_production_interface()
        stats = interface.get_stats()
        print("\nInterface Stats:")
        print(f"  Initialized: {stats['initialized']}")
        print(f"  Runtime Health: {stats['runtime_health']:.2f}")
        print(f"  Equations: {stats['equations_available']}")

    asyncio.run(demo())

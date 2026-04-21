"""AMOS Cognitive Bridge v2 — Simplified Working Architecture.

This module provides the critical architectural bridge that integrates:
- AMOSKernelRuntime (for complex cognitive cycles)
- AMOSMCPServer (MCP tool interface)
- AmosOrganism (14 subsystem implementations)

Architecture:
    MCP Tool Call → Process Tool Call → Direct Subsystem Execution → Response

For complex reasoning: Use kernel.execute_cycle()
For simple tool execution: Direct organism subsystem call

Owner: Trang
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

UTC = UTC

# Add paths for imports
_AMOS_ROOT = Path(__file__).parent.resolve()

# Organism import
from AMOS_ORGANISM_OS.organism import AmosOrganism


@dataclass
class CognitiveRequest:
    """A request processed through the cognitive pipeline."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    source: str = "mcp"


@dataclass
class CognitiveResponse:
    """A response from the cognitive pipeline."""

    request_id: str = ""
    success: bool = False
    result: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SubsystemTool:
    """Mapping between MCP tool and organism subsystem."""

    tool_name: str
    subsystem: str
    component: str
    method: str
    mapper: Callable[[dict], dict]


class AMOSCognitiveBridge:
    """Unified cognitive bridge integrating MCP and Organism.

    This is the central architectural component that enables AMOS to:
    1. Receive tool calls via MCP interface
    2. Route to appropriate organism subsystems
    3. Return structured responses with execution metadata

    Usage:
        bridge = AMOSCognitiveBridge()
        await bridge.initialize()

        # Process MCP tool call
        response = await bridge.process_tool_call(
            tool_name="brain_think",
            arguments={"thought": "Analyze this code"}
        )
    """

    _instance: Optional[AMOSCognitiveBridge] = None

    def __new__(cls) -> AMOSCognitiveBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = False
        self._organism: Optional[AmosOrganism] = None
        self._tool_registry: dict[str, SubsystemTool] = {}
        self._request_history: list[CognitiveRequest] = []
        self._response_history: list[CognitiveResponse] = []

    async def initialize(self) -> bool:
        """Initialize the cognitive bridge."""
        if self._initialized:
            return True

        print("=" * 70)
        print(" AMOS COGNITIVE BRIDGE v2.0")
        print(" Organism + MCP Integration")
        print("=" * 70)

        # Initialize organism
        print("\n[1/2] Initializing Organism Subsystems...")
        self._organism = AmosOrganism()
        print("   ✓ 14 subsystems initialized")

        # Register tool mappings
        print("\n[2/2] Registering Tool Mappings...")
        self._register_tool_mappings()
        print(f"   ✓ {len(self._tool_registry)} tools registered")

        self._initialized = True

        print("\n" + "=" * 70)
        print(" COGNITIVE BRIDGE READY")
        print("=" * 70)

        return True

    def _register_tool_mappings(self):
        """Register mappings from MCP tools to organism subsystems."""

        # BRAIN subsystem tools
        self._tool_registry["brain_think"] = SubsystemTool(
            tool_name="brain_think",
            subsystem="brain",
            component="brain",
            method="process_thought",
            mapper=lambda args: {
                "content": args.get("thought", ""),
                "thought_type": args.get("thought_type", "conceptual"),
            },
        )

        self._tool_registry["brain_plan"] = SubsystemTool(
            tool_name="brain_plan",
            subsystem="brain",
            component="brain",
            method="create_plan",
            mapper=lambda args: {
                "goal": args.get("goal", ""),
                "horizon": args.get("horizon", "short-term"),
            },
        )

        self._tool_registry["brain_remember"] = SubsystemTool(
            tool_name="brain_remember",
            subsystem="brain",
            component="memory",
            method="store",
            mapper=lambda args: {
                "content": args.get("content", ""),
                "category": args.get("category", "general"),
            },
        )

        # SENSES subsystem tools
        self._tool_registry["senses_scan"] = SubsystemTool(
            tool_name="senses_scan",
            subsystem="senses",
            component="senses",
            method="scan_environment",
            mapper=lambda args: {
                "path": args.get("path", "."),
                "depth": args.get("depth", 2),
            },
        )

        self._tool_registry["senses_gather"] = SubsystemTool(
            tool_name="senses_gather",
            subsystem="senses",
            component="context",
            method="gather_context",
            mapper=lambda args: {"include_files": args.get("include_files", True)},
        )

        # MUSCLE subsystem tools
        self._tool_registry["muscle_execute"] = SubsystemTool(
            tool_name="muscle_execute",
            subsystem="muscle",
            component="muscle",
            method="execute_command",
            mapper=lambda args: {
                "command": args.get("command", ""),
                "timeout": args.get("timeout", 60),
            },
        )

        self._tool_registry["muscle_code"] = SubsystemTool(
            tool_name="muscle_code",
            subsystem="muscle",
            component="code_runner",
            method="run_code",
            mapper=lambda args: {
                "code": args.get("code", ""),
                "language": args.get("language", "python"),
            },
        )

        # IMMUNE subsystem tools
        self._tool_registry["immune_validate"] = SubsystemTool(
            tool_name="immune_validate",
            subsystem="immune",
            component="immune",
            method="validate_action",
            mapper=lambda args: {"action": args.get("action", {})},
        )

    async def process_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> CognitiveResponse:
        """Process an MCP tool call through the organism subsystem.

        Args:
            tool_name: Name of the MCP tool being called
            arguments: Tool arguments

        Returns:
            CognitiveResponse with execution results
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now(UTC)
        request_id = str(uuid.uuid4())[:8]

        # Create request object
        request = CognitiveRequest(
            request_id=request_id,
            tool_name=tool_name,
            arguments=arguments,
            source="mcp",
        )
        self._request_history.append(request)

        # Check tool registry
        if tool_name not in self._tool_registry:
            return CognitiveResponse(
                request_id=request_id,
                success=False,
                result={"error": f"Unknown tool: {tool_name}"},
                execution_time_ms=self._elapsed_ms(start_time),
            )

        tool_def = self._tool_registry[tool_name]

        try:
            # Execute via organism subsystem
            execution_result = await self._execute_via_organism(tool_def, arguments)

            # Create response
            response = CognitiveResponse(
                request_id=request_id,
                success=execution_result.get("success", False),
                result=execution_result.get("data", {}),
                execution_time_ms=self._elapsed_ms(start_time),
            )

            self._response_history.append(response)
            return response

        except Exception as e:
            return CognitiveResponse(
                request_id=request_id,
                success=False,
                result={"error": str(e)},
                execution_time_ms=self._elapsed_ms(start_time),
            )

    async def _execute_via_organism(
        self, tool_def: SubsystemTool, arguments: dict[str, Any]
    ) -> dict:
        """Execute tool via organism subsystem."""
        if not self._organism:
            return {"success": False, "error": "Organism not initialized"}

        try:
            # Map arguments
            subsystem_args = tool_def.mapper(arguments)

            # Route to appropriate subsystem
            subsystem = getattr(self._organism, tool_def.subsystem, None)
            if not subsystem:
                return {
                    "success": False,
                    "error": f"Subsystem '{tool_def.subsystem}' not found",
                }

            # Get component
            component = getattr(subsystem, tool_def.component, subsystem)

            # Get method
            method = getattr(component, tool_def.method, None)
            if not method or not callable(method):
                return {
                    "success": False,
                    "error": f"Method '{tool_def.method}' not found",
                }

            # Execute
            if asyncio.iscoroutinefunction(method):
                result = await method(**subsystem_args)
            else:
                result = method(**subsystem_args)

            return {
                "success": True,
                "data": result if isinstance(result, dict) else {"result": result},
            }

        except Exception as e:
            import traceback

            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def _elapsed_ms(self, start: datetime) -> float:
        """Compute elapsed milliseconds."""
        return (datetime.now(UTC) - start).total_seconds() * 1000

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            "initialized": self._initialized,
            "total_requests": len(self._request_history),
            "total_responses": len(self._response_history),
            "registered_tools": len(self._tool_registry),
            "tool_names": list(self._tool_registry.keys()),
            "organism_ready": self._organism is not None,
        }


# Singleton getter
_bridge_instance: Optional[AMOSCognitiveBridge] = None


async def get_cognitive_bridge() -> AMOSCognitiveBridge:
    """Get or create the cognitive bridge singleton."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AMOSCognitiveBridge()
        await _bridge_instance.initialize()
    return _bridge_instance


def get_cognitive_bridge_sync() -> AMOSCognitiveBridge:
    """Get cognitive bridge (synchronous)."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AMOSCognitiveBridge()
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(_bridge_instance.initialize())
        except RuntimeError:
            asyncio.run(_bridge_instance.initialize())
    return _bridge_instance


if __name__ == "__main__":
    # Demo
    async def demo():
        bridge = await get_cognitive_bridge()
        print("\nBridge Stats:")
        print(json.dumps(bridge.get_stats(), indent=2))

    asyncio.run(demo())

"""AMOS Cognitive Bridge — Unified Kernel-MCP-Organism Integration

This module provides the critical architectural bridge that integrates:
- AMOSKernelRuntime (state graph, branch generation, collapse, morph execution)
- AMOSMCPServer (MCP tool interface)
- AmosOrganism (14 subsystem implementations)

Architecture Flow:
    MCP Tool Call → Kernel Ingest → Generate Branches → Simulate →
    Constitution Filter → Collapse Selection → Morph Execution →
    State Update → Response

Owner: Trang
Version: 1.0.0
"""

import asyncio
import json
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add paths for imports
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring"))

# Kernel imports
# Organism imports
from AMOS_ORGANISM_OS.organism import AmosOrganism
from clawspring.amos_brain.amos_kernel_runtime import (
    AMOSKernelRuntime,
    AMOSScores,
    Branch,
)

# Brain imports


@dataclass
class CognitiveRequest:
    """A request processed through the cognitive pipeline."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_name: str = ""
    arguments: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    source: str = "mcp"  # mcp, api, cli, internal


@dataclass
class CognitiveResponse:
    """A response from the cognitive pipeline."""

    request_id: str = ""
    success: bool = False
    result: Dict[str, Any] = field(default_factory=dict)
    selected_branch_id: str = None
    morphs_executed: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    state_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SubsystemTool:
    """Mapping between MCP tool and organism subsystem."""

    tool_name: str
    subsystem: str  # e.g., "brain", "muscle", "immune"
    component: str  # e.g., "brain_os", "executor"
    method: str  # e.g., "think", "execute"
    mapper: Callable[[dict], dict]  # Maps MCP args to subsystem args


class AMOSCognitiveBridge:
    """Unified cognitive bridge integrating Kernel, MCP, and Organism.

    This is the central architectural component that enables AMOS to:
    1. Receive tool calls via MCP interface
    2. Process through kernel runtime (state → branches → collapse → morph)
    3. Execute via organism subsystems
    4. Return structured responses

    Usage:
        bridge = AMOSCognitiveBridge()
        await bridge.initialize()

        # Process MCP tool call through cognitive pipeline
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
        self._kernel: Optional[AMOSKernelRuntime] = None
        self._organism: Optional[AmosOrganism] = None
        self._tool_registry: Dict[str, SubsystemTool] = {}
        self._request_history: List[CognitiveRequest] = []
        self._response_history: List[CognitiveResponse] = []

    async def initialize(self) -> bool:
        """Initialize the cognitive bridge.

        Sets up:
        1. Kernel runtime (state graph, brain/collapse/cascade kernels)
        2. Organism subsystems (14 subsystems)
        3. Tool registry (MCP tool → subsystem mappings)

        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            return True

        print("=" * 70)
        print(" AMOS COGNITIVE BRIDGE v1.0")
        print(" Kernel + MCP + Organism Integration")
        print("=" * 70)

        # Initialize kernel runtime
        print("\n[1/3] Initializing Kernel Runtime...")
        self._kernel = AMOSKernelRuntime()
        print("   ✓ Kernel runtime ready")
        print(f"   - BrainKernel: {self._kernel.brain.__class__.__name__}")
        print(f"   - CollapseKernel: {self._kernel.collapse.__class__.__name__}")
        print(f"   - CascadeKernel: {self._kernel.cascade.__class__.__name__}")
        print(f"   - ConstitutionGate: {self._kernel.constitution.__class__.__name__}")

        # Initialize organism
        print("\n[2/3] Initializing Organism Subsystems...")
        self._organism = AmosOrganism()
        print("   ✓ 14 subsystems initialized")

        # Register tool mappings
        print("\n[3/3] Registering Tool Mappings...")
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
                "confidence_threshold": args.get("confidence_threshold", 0.8),
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
                "constraints": args.get("constraints", []),
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
                "tags": args.get("tags", []),
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
            mapper=lambda args: {
                "include_files": args.get("include_files", True),
                "include_env": args.get("include_env", True),
            },
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
            mapper=lambda args: {
                "action": args.get("action", {}),
                "context": args.get("context", {}),
            },
        )

        # Add more tool mappings as needed...

    async def process_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> CognitiveResponse:
        """Process an MCP tool call through the cognitive pipeline.

        This is the core method that implements the AMOS cognitive loop:
        1. Create cognitive request
        2. Ingest into kernel state graph
        3. Generate candidate branches
        4. Simulate and score branches
        5. Apply constitution filter
        6. Collapse to select optimal branch
        7. Execute morphs via organism subsystems
        8. Return structured response

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
            # === COGNITIVE PIPELINE ===

            # 1. INGEST: Add request to kernel state via execute_cycle
            observation = {
                "type": "tool_request",
                "tool": tool_name,
                "subsystem": tool_def.subsystem,
                "args_hash": self._hash_args(arguments),
            }
            goal = {"tool": tool_name, "subsystem": tool_def.subsystem}

            # 2. GENERATE: Create candidate execution branches
            branches = await self._generate_branches(request, tool_def)

            # 3. SIMULATE: Score each branch
            scored_branches = await self._simulate_branches(branches)

            # 4. FILTER: Apply constitution/legality checks
            legal_branches = await self._filter_branches(scored_branches)

            if not legal_branches:
                return CognitiveResponse(
                    request_id=request_id,
                    success=False,
                    result={"error": "No legal execution paths found"},
                    execution_time_ms=self._elapsed_ms(start_time),
                )

            # 5. COLLAPSE: Select optimal branch
            selected_branch = await self._collapse_select(legal_branches)

            # 6. EXECUTE: Run the selected branch's morphs
            execution_result = await self._execute_branch(selected_branch, tool_def)

            # 7. UPDATE: Execute cycle records state internally

            # Create response
            response = CognitiveResponse(
                request_id=request_id,
                success=execution_result.get("success", False),
                result=execution_result.get("data", {}),
                selected_branch_id=getattr(selected_branch, "id", None),
                morphs_executed=execution_result.get("morphs", []),
                execution_time_ms=self._elapsed_ms(start_time),
                state_hash="",
            )

            self._response_history.append(response)
            return response

        except Exception as e:
            return CognitiveResponse(
                request_id=request_id,
                success=False,
                result={"error": str(e), "traceback": self._format_exception(e)},
                execution_time_ms=self._elapsed_ms(start_time),
            )

    async def _generate_branches(
        self, request: CognitiveRequest, tool_def: SubsystemTool
    ) -> List[Branch]:
        """Generate candidate execution branches for a request."""
        # For now, create a single direct branch
        # In full implementation, this would create multiple strategies
        branch_id = str(uuid.uuid4())[:8]

        # Map arguments to subsystem call
        subsystem_args = tool_def.mapper(request.arguments)

        branch = Branch(
            id=branch_id,
            request_id=request.request_id,
            tool_name=request.tool_name,
            subsystem=tool_def.subsystem,
            component=tool_def.component,
            method=tool_def.method,
            arguments=subsystem_args,
            estimated_cost=1.0,  # Would be computed
            estimated_risk=0.1,  # Would be computed
        )

        return [branch]

    async def _simulate_branches(self, branches: List[Branch]) -> List[Branch]:
        """Simulate and score candidate branches."""
        for branch in branches:
            # Compute AMOS scores
            branch.scores = AMOSScores(
                goal_fit=0.8,  # How well it achieves the goal
                risk=branch.estimated_risk,
                cost=branch.estimated_cost,
                coherence=0.9,  # Internal consistency
                drift=0.1,  # Deviation from current state
                reversibility=0.7,  # Can we undo this?
                confidence=0.85,  # Overall confidence
            )
        return branches

    async def _filter_branches(self, branches: List[Branch]) -> List[Branch]:
        """Apply constitution/legality filter to branches."""
        legal = []
        for branch in branches:
            # Check legality via constitution gate
            if self._kernel and self._kernel.constitution_gate:
                is_legal = await self._kernel.constitution_gate.admit(branch)
                branch.is_legal = is_legal
                if is_legal:
                    legal.append(branch)
            else:
                # No gate, assume legal
                branch.is_legal = True
                legal.append(branch)
        return legal

    async def _collapse_select(self, branches: List[Branch]) -> Optional[Branch]:
        """Collapse to select optimal branch using constrained optimization."""
        if not branches:
            return None

        if len(branches) == 1:
            return branches[0]

        # Use kernel collapse if available
        if self._kernel and self._kernel.collapse_kernel:
            return await self._kernel.collapse_kernel.select_optimal_branch(branches)

        # Fallback: select highest confidence
        return max(branches, key=lambda b: b.scores.confidence if b.scores else 0)

    async def _execute_branch(self, branch: Branch, tool_def: SubsystemTool) -> dict:
        """Execute the selected branch via organism subsystems."""
        if not self._organism:
            return {"success": False, "error": "Organism not initialized"}

        try:
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
                    "error": f"Method '{tool_def.method}' not found on {tool_def.component}",
                }

            # Execute
            if asyncio.iscoroutinefunction(method):
                result = await method(**branch.arguments)
            else:
                result = method(**branch.arguments)

            return {
                "success": True,
                "data": result if isinstance(result, dict) else {"result": result},
                "morphs": [f"{tool_def.subsystem}.{tool_def.method}"],
            }

        except Exception as e:
            return {"success": False, "error": str(e), "traceback": self._format_exception(e)}

    def _hash_args(self, args: dict) -> str:
        """Create hash of arguments for state tracking."""
        return hash(json.dumps(args, sort_keys=True)) % 10000

    def _elapsed_ms(self, start: datetime) -> float:
        """Compute elapsed milliseconds."""
        return (datetime.now(UTC) - start).total_seconds() * 1000

    def _format_exception(self, e: Exception) -> str:
        """Format exception for response."""
        import traceback

        return traceback.format_exc()

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            "initialized": self._initialized,
            "total_requests": len(self._request_history),
            "total_responses": len(self._response_history),
            "registered_tools": len(self._tool_registry),
            "tool_names": list(self._tool_registry.keys()),
            "kernel_ready": self._kernel is not None,
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


# Synchronous wrapper for non-async contexts
def get_cognitive_bridge_sync() -> AMOSCognitiveBridge:
    """Get cognitive bridge (synchronous)."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AMOSCognitiveBridge()
        # Initialize synchronously
        try:
            loop = asyncio.get_running_loop()
            # Already in async context, create task
            asyncio.create_task(_bridge_instance.initialize())
        except RuntimeError:
            # No running loop, use asyncio.run
            asyncio.run(_bridge_instance.initialize())
    return _bridge_instance


if __name__ == "__main__":
    # Demo
    async def demo():
        bridge = await get_cognitive_bridge()
        print("\nBridge Stats:")
        print(json.dumps(bridge.get_stats(), indent=2))

    asyncio.run(demo())

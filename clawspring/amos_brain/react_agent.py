"""ReAct Agent Implementation for AMOS Brain

State-of-the-art reasoning-acting pattern integrated with AMOS Kernel Runtime.
Based on: ReAct (Reasoning + Acting) pattern from agentic AI research 2025.

Architecture: Thought → Action → Observation → Repeat
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc

from enum import Enum, auto
from typing import Any, Protocol, runtime_checkable

try:
    from .amos_kernel_runtime import (
        AMOSKernelRuntime,
        Branch,
        StateGraph,
        StateVariables,
    )
except ImportError:
    from amos_kernel_runtime import (
        AMOSKernelRuntime,
        StateGraph,
    )


class ReActStepType(Enum):
    """Types of ReAct steps."""

    THOUGHT = auto()
    ACTION = auto()
    OBSERVATION = auto()


@dataclass
class ReActStep:
    """Single step in ReAct trajectory."""

    step_type: ReActStepType
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0


@dataclass
class ToolCall:
    """Tool call specification."""

    tool_name: str
    parameters: dict[str, Any]
    call_id: str


@dataclass
class ToolResult:
    """Tool execution result."""

    call_id: str
    success: bool
    result: Any
    error: str | None = None
    latency_ms: float = 0.0


@runtime_checkable
class ToolExecutor(Protocol):
    """Protocol for tool execution."""

    async def execute(self, tool_name: str, params: dict[str, Any]) -> ToolResult: ...


class AMOSReActAgent:
    """ReAct Agent integrated with AMOS Brain Kernel.

    Implements the reasoning-acting loop with brain-based state management:
    - Uses brain kernel for state tracking
    - Generates thoughts as branches
    - Executes actions through tools
    - Observes results and updates state
    """

    def __init__(
        self,
        kernel: AMOSKernelRuntime | None = None,
        tool_executor: ToolExecutor | None = None,
        max_iterations: int = 10,
        latency_budget_ms: float = 5000.0,
    ):
        self.kernel = kernel or AMOSKernelRuntime()
        self.tool_executor = tool_executor
        self.max_iterations = max_iterations
        self.latency_budget_ms = latency_budget_ms

        # Trajectory tracking
        self.trajectory: list[ReActStep] = []
        self.tool_calls: list[ToolCall] = []
        self.tool_results: list[ToolResult] = []

        # State tracking
        self.current_state: StateGraph | None = None
        self.iteration_count = 0
        self.start_time: float = 0.0

    async def run(
        self,
        query: str,
        available_tools: list[str | None] = None,
    ) -> dict[str, Any]:
        """Execute ReAct loop for a query.

        Args:
            query: User query to process
            available_tools: List of available tool names

        Returns:
            Result with answer, trajectory, and metrics

        """
        self.start_time = time.perf_counter()
        self.trajectory = []
        self.tool_calls = []
        self.tool_results = []
        self.iteration_count = 0

        # Initialize state with query
        observation = {
            "query": query,
            "available_tools": available_tools or [],
            "entities": self._extract_entities(query),
        }

        goal = {"type": "answer_query", "target": query}

        # ReAct loop
        for iteration in range(self.max_iterations):
            self.iteration_count = iteration + 1

            # Check latency budget
            elapsed_ms = (time.perf_counter() - self.start_time) * 1000
            if elapsed_ms > self.latency_budget_ms:
                break

            # === THOUGHT PHASE ===
            thought_start = time.perf_counter()

            # Use brain kernel to generate branches (candidate thoughts)
            cycle_result = self.kernel.execute_cycle(observation, goal)

            # Extract thought from selected branch
            cycle_result.get("selected_branch", "B1")
            thought = self._generate_thought(query, observation, cycle_result, iteration)

            thought_latency = (time.perf_counter() - thought_start) * 1000
            self.trajectory.append(
                ReActStep(
                    step_type=ReActStepType.THOUGHT,
                    content=thought,
                    latency_ms=thought_latency,
                )
            )

            # === ACTION PHASE ===
            action = self._decide_action(thought, available_tools)

            if action is None:
                # No action needed - we have final answer
                break

            self.trajectory.append(
                ReActStep(
                    step_type=ReActStepType.ACTION,
                    content=json.dumps(action),
                )
            )

            # === EXECUTION PHASE ===
            if action["type"] == "tool_call" and self.tool_executor:
                tool_call = ToolCall(
                    tool_name=action["tool"],
                    parameters=action.get("params", {}),
                    call_id=f"tc_{iteration}",
                )
                self.tool_calls.append(tool_call)

                exec_start = time.perf_counter()
                result = await self.tool_executor.execute(
                    tool_call.tool_name,
                    tool_call.parameters,
                )
                exec_latency = (time.perf_counter() - exec_start) * 1000
                result.latency_ms = exec_latency
                self.tool_results.append(result)

                # === OBSERVATION PHASE ===
                observation_text = self._format_observation(result)
                self.trajectory.append(
                    ReActStep(
                        step_type=ReActStepType.OBSERVATION,
                        content=observation_text,
                    )
                )

                # Update observation for next iteration
                observation["last_tool_result"] = {
                    "tool": tool_call.tool_name,
                    "success": result.success,
                    "result": str(result.result)[:500],  # Truncate for state
                }

            elif action["type"] == "final_answer":
                break

        # Compile result
        total_latency = (time.perf_counter() - self.start_time) * 1000

        return {
            "query": query,
            "answer": self._extract_final_answer(),
            "trajectory": [
                {
                    "type": step.step_type.name,
                    "content": step.content[:200],  # Truncate
                    "latency_ms": step.latency_ms,
                }
                for step in self.trajectory
            ],
            "metrics": {
                "iterations": self.iteration_count,
                "total_latency_ms": total_latency,
                "tool_calls": len(self.tool_calls),
                "thoughts": sum(1 for s in self.trajectory if s.step_type == ReActStepType.THOUGHT),
            },
            "status": "completed"
            if self.iteration_count < self.max_iterations
            else "max_iterations",
        }

    def _extract_entities(self, text: str) -> list[str]:
        """Extract key entities from text."""
        # Simple extraction - could use NER
        words = text.split()
        return [w for w in words if len(w) > 3 and w[0].isupper()][:5]

    def _generate_thought(
        self,
        query: str,
        observation: dict[str, Any],
        cycle_result: dict[str, Any],
        iteration: int,
    ) -> str:
        """Generate reasoning thought based on brain kernel output."""
        legality = cycle_result.get("legality", 0.0)
        sigma = cycle_result.get("sigma", 0.0)

        # Build thought based on state
        parts = [f"Iteration {iteration + 1}:"]

        if iteration == 0:
            parts.append(f"I need to analyze: {query}")

        if "last_tool_result" in observation:
            result = observation["last_tool_result"]
            if result["success"]:
                parts.append(f"The {result['tool']} returned useful data.")
            else:
                parts.append(f"The {result['tool']} failed. I should try another approach.")

        parts.append(f"State: legality={legality:.2f}, drift={sigma:.2f}")

        if legality > 0.7:
            parts.append("Current approach looks good.")
        elif legality < 0.5:
            parts.append("Need to reconsider my approach.")

        return " ".join(parts)

    def _decide_action(
        self,
        thought: str,
        available_tools: list[str | None],
    ) -> dict[str, Any]:
        """Decide next action based on thought."""
        # Simple logic - could be LLM-based
        if available_tools and len(self.tool_calls) < 3:
            return {
                "type": "tool_call",
                "tool": available_tools[0],
                "params": {"query": thought[:100]},
            }

        return {"type": "final_answer"}

    def _format_observation(self, result: ToolResult) -> str:
        """Format tool result as observation."""
        if result.success:
            return f"Tool returned: {str(result.result)[:150]}"
        return f"Tool failed: {result.error or 'Unknown error'}"

    def _extract_final_answer(self) -> str:
        """Extract final answer from trajectory."""
        # Return last thought or default
        thoughts = [s for s in self.trajectory if s.step_type == ReActStepType.THOUGHT]
        if thoughts:
            return f"Based on {len(thoughts)} reasoning steps: " + thoughts[-1].content
        return "No conclusion reached."


class SimpleToolExecutor:
    """Simple tool executor for testing."""

    async def execute(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        """Execute a tool (stub implementation)."""
        start = time.perf_counter()

        # Simulate tool execution
        await asyncio.sleep(0.01)  # 10ms simulated latency

        latency = (time.perf_counter() - start) * 1000

        return ToolResult(
            call_id="stub",
            success=True,
            result={"tool": tool_name, "params": params, "status": "executed"},
            latency_ms=latency,
        )


# Global agent instance
_global_react_agent: AMOSReActAgent | None = None


def get_react_agent() -> AMOSReActAgent:
    """Get or create global ReAct agent."""
    global _global_react_agent
    if _global_react_agent is None:
        executor = SimpleToolExecutor()
        _global_react_agent = AMOSReActAgent(tool_executor=executor)
    return _global_react_agent


if __name__ == "__main__":
    # Test the agent
    async def test():
        agent = get_react_agent()
        result = await agent.run(
            "What is the weather in New York?",
            available_tools=["weather_lookup", "search"],
        )
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(test())

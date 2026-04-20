"""Compatibility module for agent imports.

Provides agent functionality for AMOS system.
"""

from collections.abc import Callable
from typing import Any


class Agent:
    """AMOS Agent for task execution."""

    def __init__(self, name: str, tools: list[Callable] = None):
        self.name = name
        self.tools = tools or []
        self.state = "idle"

    def run(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a task."""
        return {"status": "completed", "result": None, "agent": self.name}

    def get_status(self) -> str:
        """Get current agent status."""
        return self.state


class AgentOrchestrator:
    """Orchestrates multiple agents."""

    def __init__(self):
        self.agents: dict[str, Agent] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register an agent."""
        self.agents[agent.name] = agent

    def dispatch(self, task: str, agent_name: str = None) -> dict[str, Any]:
        """Dispatch task to agent."""
        if agent_name and agent_name in self.agents:
            return self.agents[agent_name].run(task)
        return {"status": "error", "message": "Agent not found"}


__all__ = ["Agent", "AgentOrchestrator"]

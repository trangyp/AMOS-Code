#!/usr/bin/env python3
"""GovernedToolRegistry - Canonical Tool Registry with Governance.

All tools are registered here and executed through ActionGate.
This is the ONLY tool registry in the SuperBrain.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional


@dataclass
class Tool:
    """Represents a registered tool."""

    name: str
    func: Callable
    description: str
    schema: dict[str, Any] = None
    authorized_agents: list[str] = None


class GovernedToolRegistry:
    """Canonical tool registry with governance integration.

    All tool registration and lookup goes through this registry.
    Tool execution is authorized through ActionGate.
    """

    def __init__(self, action_gate: Any = None, memory_governance: Any = None):
        self._tools: dict[str, Tool] = {}
        self._action_gate: Any = action_gate  # Can be set after initialization
        self._memory_governance = memory_governance
        self._lock = Lock()
        self._tool_count = 0

    def set_action_gate(self, action_gate: Any) -> None:
        """Set the action gate after initialization (circular dependency)."""
        self._action_gate = action_gate

    def register(
        self,
        name: str,
        func: Callable,
        description: str = "",
        schema: dict[str, Any] = None,
        authorized_agents: list[str] = None,
    ) -> bool:
        """Register a tool with the canonical registry.

        Args:
            name: Tool name
            func: Tool function
            description: Tool description
            schema: Optional JSON schema for inputs
            authorized_agents: Optional list of agents allowed to use this tool

        Returns:
            True if registration successful
        """
        with self._lock:
            self._tools[name] = Tool(
                name=name,
                func=func,
                description=description,
                schema=schema,
                authorized_agents=authorized_agents,
            )
            self._tool_count += 1
        return True

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        with self._lock:
            return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        with self._lock:
            return list(self._tools.keys())

    def is_healthy(self) -> bool:
        """Check if registry is healthy."""
        return True

    def shutdown(self) -> None:
        """Graceful shutdown."""
        pass

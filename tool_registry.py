"""Compatibility module for tool_registry imports.

Provides tool registration and lookup functionality.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional


class Tool:
    """Represents a registered tool."""

    def __init__(self, name: str, func: Callable, description: str = ""):
        self.name = name
        self.func = func
        self.description = description


class ToolRegistry:
    """Registry for AMOS tools."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, func: Callable, description: str = "") -> None:
        """Register a tool."""
        self._tools[name] = Tool(name, func, description)

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


# Global registry instance
default_registry = ToolRegistry()

__all__ = ["Tool", "ToolRegistry", "default_registry"]

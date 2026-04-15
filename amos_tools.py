"""AMOS Tools stub for compatibility."""

from typing import Any, Callable


class ToolRegistry:
    """Registry for AMOS tools."""

    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """Register a tool."""
        self._tools[name] = func

    def get(self, name: str) -> Callable | None:
        """Get tool by name."""
        return self._tools.get(name)

    def list(self) -> list[str]:
        """List all registered tools."""
        return list(self._tools.keys())


class ToolExecutor:
    """Executor for AMOS tools."""

    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or ToolRegistry()

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool."""
        tool = self.registry.get(tool_name)
        if tool:
            return tool(**kwargs)
        return None


# Default instances
default_registry = ToolRegistry()
default_executor = ToolExecutor(default_registry)

__all__ = ["ToolRegistry", "ToolExecutor", "default_registry", "default_executor"]

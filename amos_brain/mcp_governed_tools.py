"""MCP Governed Tools - Connect MCP tools to SuperBrain governance.

Real working integration that:
1. Wraps MCP tools with brain governance
2. Registers tools in GovernedToolRegistry
3. Routes through ActionGate for authorization
4. Integrates with cognitive engine tool calls
"""

from __future__ import annotations

from typing import Any, Optional

from amos_brain.mcp_tools_bridge import MCPToolsBridge
from amos_brain.tool_registry_governed import GovernedToolRegistry


class GovernedMCPTools:
    """MCP tools wrapped with brain governance.

    Real integration connecting:
    - MCPToolsBridge (filesystem, git, web, code tools)
    - GovernedToolRegistry (canonical tool registry)
    - ActionGate (authorization)
    - CognitiveEngine (tool calls)
    """

    def __init__(
        self,
        registry: Optional[GovernedToolRegistry] = None,
        root_path: str = ".",
    ):
        self._bridge = MCPToolsBridge(root_path=root_path)
        self._registry = registry or GovernedToolRegistry()
        self._registered = False

    def register_all(self) -> None:
        """Register all MCP tools with governed registry."""
        if self._registered:
            return

        # Register filesystem tools
        self._registry.register(
            name="fs_read",
            func=self._bridge.fs_read_file,
            description="Read file or directory contents",
            schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
            },
        )

        self._registry.register(
            name="fs_write",
            func=self._bridge.fs_write_file,
            description="Write content to file",
            schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
        )

        self._registry.register(
            name="fs_search",
            func=self._bridge.fs_search_files,
            description="Search files for pattern",
            schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                },
            },
        )

        # Register git tools
        self._registry.register(
            name="git_status",
            func=self._bridge.git_status,
            description="Get git repository status",
            schema={"type": "object", "properties": {}},
        )

        self._registry.register(
            name="git_log",
            func=self._bridge.git_log,
            description="Get git commit history",
            schema={
                "type": "object",
                "properties": {
                    "max_count": {"type": "integer"},
                },
            },
        )

        self._registry.register(
            name="git_diff",
            func=self._bridge.git_diff,
            description="Get git diff",
            schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
            },
        )

        # Register web search
        self._registry.register(
            name="web_search",
            func=self._bridge.web_search,
            description="Search the web for information",
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
            },
        )

        # Register code execution
        self._registry.register(
            name="code_execute_python",
            func=self._bridge.code_execute_python,
            description="Execute Python code safely",
            schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                },
            },
        )

        self._registered = True

    def execute(
        self,
        tool_name: str,
        agent_id: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Execute tool through governed registry.

        Args:
            tool_name: Name of tool to execute
            agent_id: Agent requesting execution
            **params: Tool parameters

        Returns:
            Tool execution result
        """
        self.register_all()

        tool = self._registry.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
            }

        # Check authorization if action gate available
        if self._registry._action_gate:
            authorized = self._registry._action_gate.check_action(
                agent_id=agent_id or "unknown",
                action=tool_name,
                params=params,
            )
            if not authorized:
                return {
                    "success": False,
                    "error": "Action not authorized",
                }

        # Execute tool
        try:
            result = tool.func(**params)
            return (
                result
                if isinstance(result, dict)
                else {
                    "success": True,
                    "result": result,
                }
            )
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_tools(self) -> list[str]:
        """List all registered MCP tools."""
        self.register_all()
        return self._registry.list_tools()

    def get_registry(self) -> GovernedToolRegistry:
        """Get the governed registry for external use."""
        self.register_all()
        return self._registry


# Global instance
_governed_mcp: Optional[GovernedMCPTools] = None


def get_governed_mcp_tools(root_path: str = ".") -> GovernedMCPTools:
    """Get or create global governed MCP tools."""
    global _governed_mcp
    if _governed_mcp is None:
        _governed_mcp = GovernedMCPTools(root_path=root_path)
        _governed_mcp.register_all()
    return _governed_mcp

"""AMOS MCP Server Registry - Model Context Protocol server management.

Manages MCP server connections with:
- Server registration and discovery
- Health monitoring
- Connection pooling
- Capability advertisement
"""

from __future__ import annotations



from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

class MCPProtocol(Enum):
    """MCP protocol versions."""

    V2024_11_05 = "2024-11-05"
    V2025_03_26 = "2025-03-26"

class ServerStatus(Enum):
    """MCP server connection status."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"

@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class MCPResource:
    """MCP resource definition."""

    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None

@dataclass
class MCPServer:
    """MCP server registration."""

    id: str
    name: str
    url: str
    protocol: MCPProtocol
    status: ServerStatus
    capabilities: List[str]
    tools: List[MCPTool] = field(default_factory=list)
    resources: List[MCPResource] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_ping: Optional[str] = None
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "protocol": self.protocol.value,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.input_schema,
                }
                for t in self.tools
            ],
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mime_type": r.mime_type,
                }
                for r in self.resources
            ],
            "registered_at": self.registered_at,
            "last_ping": self.last_ping,
            "error_count": self.error_count,
            "metadata": self.metadata,
        }

class MCPRegistry:
    """Registry for MCP server management."""

    def __init__(self):
        self._servers: Dict[str, MCPServer] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize with default MCP servers."""
        if self._initialized:
            return

        # Register filesystem MCP server (if available)
        self.register_server(
            MCPServer(
                id="filesystem-local",
                name="Local Filesystem",
                url="stdio://@modelcontextprotocol/server-filesystem",
                protocol=MCPProtocol.V2024_11_05,
                status=ServerStatus.PENDING,
                capabilities=["tools", "resources"],
                tools=[
                    MCPTool(
                        name="read_file",
                        description="Read file contents",
                        input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                    ),
                    MCPTool(
                        name="write_file",
                        description="Write to file",
                        input_schema={
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"},
                            },
                        },
                    ),
                ],
                resources=[
                    MCPResource(
                        uri="file://local",
                        name="Local Filesystem",
                        description="Access to local files",
                        mime_type="application/octet-stream",
                    )
                ],
            )
        )

        # Register GitHub MCP server
        self.register_server(
            MCPServer(
                id="github",
                name="GitHub Integration",
                url="https://api.github.com/mcp",
                protocol=MCPProtocol.V2024_11_05,
                status=ServerStatus.PENDING,
                capabilities=["tools"],
                tools=[
                    MCPTool(
                        name="create_issue",
                        description="Create GitHub issue",
                        input_schema={
                            "type": "object",
                            "properties": {"repo": {"type": "string"}, "title": {"type": "string"}},
                        },
                    ),
                ],
            )
        )

        self._initialized = True

    def register_server(self, server: MCPServer) -> MCPServer:
        """Register a new MCP server."""
        self._servers[server.id] = server
        return server

    def unregister_server(self, server_id: str) -> bool:
        """Unregister an MCP server."""
        if server_id in self._servers:
            del self._servers[server_id]
            return True
        return False

    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a specific MCP server."""
        return self._servers.get(server_id)

    def list_servers(
        self,
        status: Optional[ServerStatus] = None,
        capability: Optional[str] = None,
    ) -> List[MCPServer]:
        """List MCP servers with optional filtering."""
        servers = list(self._servers.values())

        if status:
            servers = [s for s in servers if s.status == status]

        if capability:
            servers = [s for s in servers if capability in s.capabilities]

        return servers

    def update_status(self, server_id: str, status: ServerStatus) -> Optional[MCPServer]:
        """Update server connection status."""
        server = self._servers.get(server_id)
        if server:
            server.status = status
            if status == ServerStatus.CONNECTED:
                server.last_ping = datetime.now(timezone.utc).isoformat()
                server.error_count = 0
            elif status == ServerStatus.ERROR:
                server.error_count += 1
        return server

    def ping_server(self, server_id: str) -> bool:
        """Ping a server to check connectivity."""
        server = self._servers.get(server_id)
        if not server:
            return False

        # In production, this would actually ping the server
        # For now, update timestamp if connected
        if server.status == ServerStatus.CONNECTED:
            server.last_ping = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def get_all_tools(self) -> List[dict[str, Any]]:
        """Get all tools from all connected servers."""
        tools = []
        for server in self._servers.values():
            if server.status == ServerStatus.CONNECTED:
                for tool in server.tools:
                    tools.append(
                        {
                            "server_id": server.id,
                            "server_name": server.name,
                            "tool_name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.input_schema,
                        }
                    )
        return tools

    def get_all_resources(self) -> List[dict[str, Any]]:
        """Get all resources from all connected servers."""
        resources = []
        for server in self._servers.values():
            if server.status == ServerStatus.CONNECTED:
                for resource in server.resources:
                    resources.append(
                        {
                            "server_id": server.id,
                            "server_name": server.name,
                            "uri": resource.uri,
                            "name": resource.name,
                            "description": resource.description,
                            "mime_type": resource.mime_type,
                        }
                    )
        return resources

# Global MCP registry instance
_mcp_registry: Optional[MCPRegistry] = None

def get_mcp_registry() -> MCPRegistry:
    """Get global MCP registry."""
    global _mcp_registry
    if _mcp_registry is None:
        _mcp_registry = MCPRegistry()
        _mcp_registry.initialize()
    return _mcp_registry

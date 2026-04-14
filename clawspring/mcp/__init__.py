"""mcp package — Model Context Protocol client for clawspring.

Usage
-----
MCP servers are configured in one of two JSON files:

  ~/.clawspring/mcp.json        (user-level, all projects)
  .mcp.json                      (project-level, current dir, overrides user)

Format:
    {
      "mcpServers": {
        "my-git-server": {
          "type": "stdio",
          "command": "uvx",
          "args": ["mcp-server-git"]
        },
        "my-remote": {
          "type": "sse",
          "url": "http://localhost:8080/sse"
        }
      }
    }

Supported transports:
  stdio  — spawn a local subprocess (most common)
  sse    — HTTP Server-Sent Events stream
  http   — plain HTTP POST (Streamable HTTP transport)

MCP tools are automatically discovered on startup and registered into the
tool_registry under the name  mcp__<server>__<tool>.
Claude can invoke them just like built-in tools.
"""
from .client import (  # noqa: F401
    MCPClient,
    MCPManager,
    get_mcp_manager,
)
from .config import (  # noqa: F401
    add_server_to_user_config,
    list_config_files,
    load_mcp_configs,
    remove_server_from_user_config,
    save_user_mcp_config,
)
from .tools import (  # noqa: F401
    initialize_mcp,
    refresh_server,
    reload_mcp,
)
from .types import (  # noqa: F401
    MCPServerConfig,
    MCPServerState,
    MCPTool,
    MCPTransport,
)

__all__ = [
    # types
    "MCPServerConfig",
    "MCPTool",
    "MCPServerState",
    "MCPTransport",
    # client
    "MCPClient",
    "MCPManager",
    "get_mcp_manager",
    # config
    "load_mcp_configs",
    "save_user_mcp_config",
    "add_server_to_user_config",
    "remove_server_from_user_config",
    "list_config_files",
    # tools
    "initialize_mcp",
    "reload_mcp",
    "refresh_server",
]

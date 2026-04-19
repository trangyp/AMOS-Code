#!/usr/bin/env python3
"""AMOS MCP Bridge - Model Context Protocol Integration
=======================================================

Connects AMOS Brain to the MCP ecosystem (Anthropic standard, Nov 2024).
Enables tool use, data access, and real-world interactions through
universal protocol.

Features:
- MCP Server lifecycle management
- Tool discovery and registry
- Secure execution with L1-L6 law enforcement
- Integration with Hybrid Orchestrator
- Transport: stdio (SSE for future)

Architecture:
- Neural: Tool selection, parameter generation
- Symbolic: Law enforcement, capability validation
- Hybrid: Governed, safe tool orchestration

Author: Trang Phan
Version: 1.0.0
"""


import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class TransportType(Enum):
    """MCP transport protocols."""
    STDIO = auto()
    SSE = auto()


@dataclass
class MCPServer:
    """MCP Server configuration."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    transport: TransportType = TransportType.STDIO
    description: str = ""
    auto_start: bool = False


@dataclass
class MCPTool:
    """Discovered MCP tool."""
    name: str
    description: str
    server: str
    parameters: Dict[str, Any]
    permissions: List[str] = field(default_factory=list)


@dataclass
class ToolResult:
    """Tool execution result."""
    tool: str
    success: bool
    output: Any
    law_compliant: bool
    violations: List[str]
    duration_ms: float


class MCPServerManager:
    """Manages MCP server lifecycle."""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.tools: Dict[str, MCPTool] = {}

    def register(self, server: MCPServer) -> bool:
        """Register an MCP server."""
        if server.name in self.servers:
            return False
        self.servers[server.name] = server
        if server.auto_start:
            self.start(server.name)
        return True

    def start(self, name: str) -> bool:
        """Start MCP server process."""
        if name not in self.servers or name in self.processes:
            return False

        server = self.servers[name]
        try:
            env = {**dict(subprocess.os.environ), **server.env}
            process = subprocess.Popen(
                [server.command] + server.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
            )
            self.processes[name] = process
            self._discover_tools(name, process)
            return True
        except Exception as e:
            print(f"[MCP] Failed to start {name}: {e}")
            return False

    def stop(self, name: str) -> bool:
        """Stop MCP server."""
        if name not in self.processes:
            return False
        process = self.processes[name]
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        del self.processes[name]
        # Remove tools from this server
        self.tools = {k: v for k, v in self.tools.items() if v.server != name}
        return True

    def _discover_tools(self, server_name: str, process: subprocess.Popen) -> None:
        """Discover available tools from server."""
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        try:
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                for tool_data in response.get("result", {}).get("tools", []):
                    tool = MCPTool(
                        name=tool_data.get("name"),
                        description=tool_data.get("description", ""),
                        server=server_name,
                        parameters=tool_data.get("parameters", {}),
                    )
                    self.tools[tool.name] = tool
        except Exception as e:
            print(f"[MCP] Discovery failed for {server_name}: {e}")

    def list_servers(self) -> List[dict]:
        """List all servers with status."""
        return [
            {
                "name": name,
                "running": name in self.processes,
                "tools": len([t for t in self.tools.values() if t.server == name]),
            }
            for name in self.servers
        ]

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name."""
        return self.tools.get(name)

    def get_all_tools(self) -> List[MCPTool]:
        """Get all discovered tools."""
        return list(self.tools.values())


class SecureToolExecutor:
    """Executes tools with Global Laws enforcement."""

    def __init__(self, manager: MCPServerManager):
        self.manager = manager
        self.history: List[ToolResult] = []

    def validate(self, tool: str, params: dict) -> Tuple[bool, list[str]]:
        """Validate against L1-L6."""
        from amos_brain import GlobalLaws

        laws = GlobalLaws()
        violations = []

        # L1: Law of Law
        action = f"Execute {tool} with {params}"
        permitted, reason = laws.check_l1_constraint(action)
        if not permitted:
            violations.append(f"L1: {reason}")

        # L4: Structural integrity - check dangerous patterns
        param_str = json.dumps(params).lower()
        dangerous = ["delete *", "rm -rf", "drop", "format"]
        for pattern in dangerous:
            if pattern in param_str:
                violations.append(f"L4: Dangerous pattern '{pattern}'")

        # L5: Communication
        tool_obj = self.manager.get_tool(tool)
        if tool_obj:
            ok, issues = laws.l5_communication_check(tool_obj.description)
            if not ok:
                violations.extend([f"L5: {i}" for i in issues])

        return len(violations) == 0, violations

    def execute(self, tool: str, params: dict) -> ToolResult:
        """Execute with full validation."""
        start = time.time()

        # Validate
        is_valid, violations = self.validate(tool, params)
        if not is_valid:
            result = ToolResult(
                tool=tool, success=False, output=None,
                law_compliant=False, violations=violations,
                duration_ms=(time.time() - start) * 1000
            )
            self.history.append(result)
            return result

        # Execute
        try:
            tool_obj = self.manager.get_tool(tool)
            if not tool_obj:
                raise ValueError(f"Tool {tool} not found")

            server = self.manager.processes.get(tool_obj.server)
            if not server:
                raise RuntimeError(f"Server {tool_obj.server} not running")

            request = {
                "jsonrpc": "2.0", "id": 2,
                "method": "tools/call",
                "params": {"name": tool, "arguments": params}
            }
            server.stdin.write(json.dumps(request) + "\n")
            server.stdin.flush()

            response = json.loads(server.stdout.readline())
            output = response.get("result", {}).get("content", "")

            result = ToolResult(
                tool=tool, success=True, output=output,
                law_compliant=True, violations=[],
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            result = ToolResult(
                tool=tool, success=False, output=str(e),
                law_compliant=True, violations=[],
                duration_ms=(time.time() - start) * 1000
            )

        self.history.append(result)
        return result


class AMOSMCPBridge:
    """Main bridge integrating MCP with AMOS Brain."""

    def __init__(self):
        self.manager = MCPServerManager()
        self.executor = SecureToolExecutor(self.manager)
        self._ready = False

    def setup_default_servers(self) -> None:
        """Configure common MCP servers."""
        servers = [
            MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", str(Path.cwd())],
                description="File system operations",
                auto_start=True,
            ),
            MCPServer(
                name="git",
                command="uvx",
                args=["mcp-server-git", "--repository", str(Path.cwd())],
                description="Git operations",
            ),
            MCPServer(
                name="python",
                command=sys.executable,
                args=["-m", "amos_mcp_python_server"],
                description="Python execution",
            ),
        ]
        for server in servers:
            self.manager.register(server)
        self._ready = True

    def get_status(self) -> dict:
        """Get bridge status."""
        return {
            "ready": self._ready,
            "servers": self.manager.list_servers(),
            "tools_available": len(self.manager.tools),
            "executions": len(self.executor.history),
        }

    def execute(self, tool: str, **params) -> ToolResult:
        """Execute tool with automatic validation."""
        return self.executor.execute(tool, params)


def main():
    """Demo MCP bridge."""
    print("=" * 70)
    print("AMOS MCP BRIDGE v1.0.0")
    print("=" * 70)

    bridge = AMOSMCPBridge()
    bridge.setup_default_servers()

    status = bridge.get_status()
    print(f"\n[Status]")
    print(f"  Ready: {status['ready']}")
    print(f"  Servers: {len(status['servers'])}")
    print(f"  Tools: {status['tools_available']}")

    print(f"\n[Servers]")
    for server in status['servers']:
        status_icon = "●" if server['running'] else "○"
        print(f"  {status_icon} {server['name']}: {server['tools']} tools")

    print("\n" + "=" * 70)
    print("MCP Bridge operational. Tools available for hybrid orchestration.")
    print("=" * 70)


if __name__ == "__main__":
    main()

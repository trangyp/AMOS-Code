"""
Axiom MCP Server - Model Context Protocol Integration

Exposes Axiom kernel capabilities through MCP for AI assistant integration.
Uses stdio transport for compatibility with OpenClaw and other MCP clients.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .axiom_state import get_state_manager
from .control_directory import get_control_manager
from .integration_bus import (
    BusMessage,
    BusPriority,
    BusType,
    ModelRequest,
    get_bus_coordinator,
)
from .nl_processor import RiskLevel, get_nl_processor


@dataclass
class MCPTool:
    """MCP Tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class MCPResource:
    """MCP Resource definition."""

    uri: str
    name: str
    description: str
    mime_type: str


class AxiomMCPServer:
    """MCP Server exposing Axiom kernel capabilities."""

    def __init__(self) -> None:
        self.tools: list[MCPTool] = []
        self.resources: list[MCPResource] = []
        self._setup_capabilities()

        # Initialize Axiom components
        self.nl_processor = get_nl_processor()
        self.bus_coordinator = get_bus_coordinator()
        self.state_manager = get_state_manager()

    def _setup_capabilities(self) -> None:
        """Define available MCP tools and resources."""
        self.tools = [
            MCPTool(
                name="axiom_nl_process",
                description="Process natural language command through Axiom",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Natural language command"},
                        "auto_commit": {"type": "boolean", "default": False},
                    },
                    "required": ["command"],
                },
            ),
            MCPTool(
                name="axiom_state_get",
                description="Get current Axiom state",
                input_schema={
                    "type": "object",
                    "properties": {
                        "projection": {
                            "type": "string",
                            "enum": [
                                "deterministic",
                                "observational",
                                "decision",
                                "health",
                                "minimal",
                            ],
                        },
                    },
                },
            ),
            MCPTool(
                name="axiom_bus_publish",
                description="Publish message to Axiom integration bus",
                input_schema={
                    "type": "object",
                    "properties": {
                        "bus_type": {
                            "type": "string",
                            "enum": [
                                "model",
                                "runtime",
                                "memory",
                                "tool",
                                "protocol",
                                "frontend",
                                "policy",
                                "sync",
                            ],
                        },
                        "topic": {"type": "string"},
                        "payload": {"type": "object"},
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "normal", "low", "background"],
                            "default": "normal",
                        },
                    },
                    "required": ["bus_type", "topic", "payload"],
                },
            ),
            MCPTool(
                name="axiom_bus_health",
                description="Check integration bus health status",
                input_schema={"type": "object", "properties": {}},
            ),
            MCPTool(
                name="axiom_control_init",
                description="Initialize .amos/ control directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                        "name": {"type": "string"},
                        "language": {"type": "string", "default": "python"},
                    },
                    "required": ["name"],
                },
            ),
            MCPTool(
                name="axiom_control_config",
                description="Read .amos/ control directory configuration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                    },
                },
            ),
            MCPTool(
                name="axiom_ledger_get",
                description="Get command ledger for intent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "intent_id": {"type": "string"},
                    },
                    "required": ["intent_id"],
                },
            ),
            MCPTool(
                name="axiom_model_request",
                description="Send request through Model Bus to LLM",
                input_schema={
                    "type": "object",
                    "properties": {
                        "model_id": {"type": "string"},
                        "prompt": {"type": "string"},
                        "context": {"type": "object"},
                        "parameters": {"type": "object"},
                    },
                    "required": ["prompt"],
                },
            ),
            MCPTool(
                name="axiom_memory_store",
                description="Store item in Axiom memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "memory_type": {
                            "type": "string",
                            "enum": ["short_term", "long_term", "working"],
                            "default": "short_term",
                        },
                        "importance": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.5,
                        },
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["content"],
                },
            ),
            MCPTool(
                name="axiom_memory_search",
                description="Search Axiom memory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "memory_type": {
                            "type": "string",
                            "enum": ["short_term", "long_term", "working"],
                        },
                    },
                    "required": ["query"],
                },
            ),
            MCPTool(
                name="axiom_tool_discover",
                description="Discover available tools in Tool Bus",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                },
            ),
            MCPTool(
                name="axiom_kernel_version",
                description="Get Axiom kernel version",
                input_schema={"type": "object", "properties": {}},
            ),
        ]

        self.resources = [
            MCPResource(
                uri="axiom://state/current",
                name="Current Axiom State",
                description="Real-time Axiom state snapshot",
                mime_type="application/json",
            ),
            MCPResource(
                uri="axiom://bus/status",
                name="Integration Bus Status",
                description="Status of all 8 integration buses",
                mime_type="application/json",
            ),
            MCPResource(
                uri="axiom://docs/architecture",
                name="Axiom Architecture Documentation",
                description="Axiom 10-domain state model and bus architecture",
                mime_type="text/markdown",
            ),
        ]

    async def initialize(self) -> None:
        """Initialize the server and start buses."""
        await self.bus_coordinator.start_all()
        print("Axiom MCP Server initialized", file=sys.stderr)

    def handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True},
                "logging": {},
            },
            "serverInfo": {"name": "axiom-kernel-server", "version": "7.1.0"},
        }

    def handle_tools_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.input_schema,
                }
                for t in self.tools
            ]
        }

    def handle_resources_list(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle resources/list request."""
        return {
            "resources": [
                {
                    "uri": r.uri,
                    "name": r.name,
                    "description": r.description,
                    "mimeType": r.mime_type,
                }
                for r in self.resources
            ]
        }

    async def handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            result = await self._execute_tool(tool_name, arguments)
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}],
                "isError": False,
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                "isError": True,
            }

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool by name."""

        if tool_name == "axiom_nl_process":
            return await self._tool_nl_process(arguments)
        elif tool_name == "axiom_state_get":
            return await self._tool_state_get(arguments)
        elif tool_name == "axiom_bus_publish":
            return await self._tool_bus_publish(arguments)
        elif tool_name == "axiom_bus_health":
            return await self._tool_bus_health(arguments)
        elif tool_name == "axiom_control_init":
            return await self._tool_control_init(arguments)
        elif tool_name == "axiom_control_config":
            return await self._tool_control_config(arguments)
        elif tool_name == "axiom_ledger_get":
            return await self._tool_ledger_get(arguments)
        elif tool_name == "axiom_model_request":
            return await self._tool_model_request(arguments)
        elif tool_name == "axiom_memory_store":
            return await self._tool_memory_store(arguments)
        elif tool_name == "axiom_memory_search":
            return await self._tool_memory_search(arguments)
        elif tool_name == "axiom_tool_discover":
            return await self._tool_discover(arguments)
        elif tool_name == "axiom_kernel_version":
            return await self._tool_version(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    # -----------------------------------------------------------------------
    # Tool Implementations
    # -----------------------------------------------------------------------

    async def _tool_nl_process(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Process natural language command."""
        command = arguments.get("command", "")
        auto_commit = arguments.get("auto_commit", False)

        intent, proposals, explanation = self.nl_processor.process(command, auto_commit)
        risk = self.nl_processor.classify_risk(intent)

        return {
            "intent_id": intent.intent_id,
            "action_type": intent.action_type,
            "targets": intent.target_files,
            "code_scope": intent.code_scope,
            "risk_level": risk.value,
            "risk_emoji": {
                RiskLevel.LOW: "🟢",
                RiskLevel.MEDIUM: "🟡",
                RiskLevel.HIGH: "🟠",
                RiskLevel.CRITICAL: "🔴",
            }.get(risk, "⚪"),
            "proposals_count": len(proposals),
            "explanation": explanation,
        }

    async def _tool_state_get(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Get current Axiom state."""
        state = self.state_manager.get_current()
        projection = arguments.get("projection", "minimal")

        return {
            "hash": state.canonical_hash,
            "timestamp": state.timestamp.isoformat(),
            "projection": projection,
            "data": state.project(projection),
            "domains": {
                "classical": {
                    "system_load": state.classical.system_load,
                    "cpu_percent": state.classical.cpu_percent,
                    "memory_percent": state.classical.memory_percent,
                },
                "biological": {
                    "health_score": state.biological.health_score,
                    "stress_level": state.biological.stress_level,
                    "energy_level": state.biological.energy_level,
                },
                "quantum": {
                    "coherence_time": state.quantum.coherence_time,
                    "decoherence_rate": state.quantum.decoherence_rate,
                },
                "world": {
                    "external_pressure": state.world.external_pressure,
                    "peer_connections": len(state.world.peer_connections),
                },
                "uncertainty": {
                    "epistemic": state.uncertainty.epistemic_uncertainty,
                    "aleatoric": state.uncertainty.aleatoric_uncertainty,
                    "model": state.uncertainty.model_uncertainty,
                },
            },
        }

    async def _tool_bus_publish(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Publish message to bus."""
        bus_type_str = arguments.get("bus_type", "model")
        topic = arguments.get("topic", "")
        payload = arguments.get("payload", {})
        priority_str = arguments.get("priority", "normal")

        bus_type = BusType(bus_type_str)
        priority = BusPriority[priority_str.upper()]

        message = BusMessage.create(
            bus_type=bus_type,
            topic=topic,
            payload=payload,
            source="axiom_mcp",
            priority=priority,
        )

        await self.bus_coordinator.publish(message)

        return {
            "published": True,
            "bus_type": bus_type.value,
            "topic": topic,
            "message_id": message.msg_id,
            "timestamp": message.timestamp.isoformat(),
        }

    async def _tool_bus_health(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Check bus health."""
        health = await self.bus_coordinator.health_check_all()

        return {
            "buses": {
                name: {
                    "status": status.get("status", "unknown"),
                    "details": status,
                }
                for name, status in health.items()
            },
            "overall": "healthy"
            if all(s.get("status") == "healthy" for s in health.values())
            else "degraded",
        }

    async def _tool_control_init(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Initialize control directory."""
        path = arguments.get("path", ".")
        name = arguments.get("name", "")
        language = arguments.get("language", "python")

        manager = get_control_manager(path)
        manager.init(name=name, language=language)

        return {
            "initialized": True,
            "path": path,
            "name": name,
            "language": language,
            "files_created": [
                "repo.yaml",
                "glossary.yaml",
                "policies.yaml",
                "architecture.yaml",
                "verify.yaml",
                "ssot.yaml",
            ],
        }

    async def _tool_control_config(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Read control directory config."""
        path = arguments.get("path", ".")
        manager = get_control_manager(path)

        if not manager.exists():
            return {"error": f"No .amos/ directory in {path}"}

        repo = manager.get_repo()
        policies = manager.get_policies()

        return {
            "exists": True,
            "repo": {
                "name": repo.name,
                "version": repo.version,
                "language": repo.language,
                "entrypoints": repo.entrypoints,
                "protected_paths": repo.protected_paths,
            },
            "policies": {
                "rule_count": len(policies.rules),
                "max_risk_score": policies.max_risk_score,
                "auto_approve_low_risk": policies.auto_approve_low_risk,
                "require_human_approval": policies.require_human_approval,
            },
        }

    async def _tool_ledger_get(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Get command ledger."""
        intent_id = arguments.get("intent_id", "")
        ledger = self.nl_processor.get_ledger(intent_id)

        if not ledger:
            return {"error": f"Ledger not found for intent {intent_id}"}

        return {
            "ledger_id": ledger.ledger_id,
            "intent_id": ledger.intent_id,
            "status": ledger.status.value,
            "final_state": ledger.final_state,
            "created_at": ledger.created_at.isoformat(),
            "completed_at": ledger.completed_at.isoformat() if ledger.completed_at else None,
            "transitions": ledger.transitions,
        }

    async def _tool_model_request(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Send model request through Model Bus."""
        model_id = arguments.get("model_id", "")
        prompt = arguments.get("prompt", "")
        context = arguments.get("context", {})
        parameters = arguments.get("parameters", {})

        # Get model bus
        model_bus = self.bus_coordinator.get_bus(BusType.MODEL)

        # Create and send request
        request = ModelRequest(
            model_id=model_id,
            prompt=prompt,
            context=context,
            parameters=parameters,
        )

        # Route through model router
        response = await model_bus.router.route(request)

        return {
            "request_id": response.request_id,
            "model_id": response.model_id,
            "content": response.content,
            "tokens_used": response.tokens_used,
            "latency_ms": response.latency_ms,
            "metadata": response.metadata,
        }

    async def _tool_memory_store(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Store item in memory."""
        content = arguments.get("content", "")
        memory_type = arguments.get("memory_type", "short_term")
        importance = arguments.get("importance", 0.5)
        tags = arguments.get("tags", [])

        # Get memory bus
        memory_bus = self.bus_coordinator.get_bus(BusType.MEMORY)

        # Create message to store
        message = BusMessage.create(
            bus_type=BusType.MEMORY,
            topic="store.new",
            payload={
                "entry_id": f"mcp_{datetime.now(UTC).timestamp()}",
                "content": content,
                "memory_type": memory_type,
                "importance": importance,
                "tags": tags,
            },
            source="axiom_mcp",
        )

        await self.bus_coordinator.publish(message)

        return {
            "stored": True,
            "memory_type": memory_type,
            "importance": importance,
            "tags": tags,
        }

    async def _tool_memory_search(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Search memory."""
        query = arguments.get("query", "")
        memory_type = arguments.get("memory_type")

        # Get memory bus
        memory_bus = self.bus_coordinator.get_bus(BusType.MEMORY)

        # Search
        results = await memory_bus.store.search(query, memory_type)

        return {
            "query": query,
            "count": len(results),
            "results": [
                {
                    "entry_id": r.entry_id,
                    "content": r.content[:200],
                    "memory_type": r.memory_type,
                    "importance": r.importance,
                    "tags": r.tags,
                }
                for r in results[:10]  # Limit to 10
            ],
        }

    async def _tool_discover(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Discover tools."""
        query = arguments.get("query", "")

        # Get tool bus
        tool_bus = self.bus_coordinator.get_bus(BusType.TOOL)

        # Search tools
        if query:
            tools = tool_bus.registry.search(query)
        else:
            tools = tool_bus.registry.list_tools()

        return {
            "query": query,
            "count": len(tools),
            "tools": [
                {
                    "tool_id": t.tool_id,
                    "name": t.name,
                    "description": t.description,
                    "requires_approval": t.requires_approval,
                }
                for t in tools
            ],
        }

    async def _tool_version(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Get kernel version."""
        from . import __version__

        return {
            "version": __version__,
            "name": "Axiom Kernel",
            "architecture": "kernel-first",
            "layers": ["law", "state", "interaction", "deterministic", "observe", "repair"],
            "extensions": [
                "axiom_state",
                "control_directory",
                "integration_bus",
                "nl_processor",
            ],
        }

    # -----------------------------------------------------------------------
    # Server Loop
    # -----------------------------------------------------------------------

    async def run_stdio(self) -> None:
        """Run server over stdio transport."""
        await self.initialize()

        print("Axiom MCP Server running on stdio", file=sys.stderr)

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                message = json.loads(line)
                method = message.get("method", "")
                params = message.get("params", {})
                msg_id = message.get("id")

                # Handle request
                if method == "initialize":
                    result = self.handle_initialize(params)
                elif method == "tools/list":
                    result = self.handle_tools_list(params)
                elif method == "resources/list":
                    result = self.handle_resources_list(params)
                elif method == "tools/call":
                    result = await self.handle_tools_call(params)
                else:
                    result = None

                # Send response if it's a request (has id)
                if msg_id is not None:
                    response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                pass  # Skip invalid JSON
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


async def main() -> None:
    """Main entry point."""
    server = AxiomMCPServer()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())

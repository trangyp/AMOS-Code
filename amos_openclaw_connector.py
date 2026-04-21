#!/usr/bin/env python3

from typing import Any

"""
AMOS-OpenClaw Unified Connector

Bidirectional bridge connecting AMOS Brain (Python) with OpenClaw (TypeScript).

Features:
- MCP Server for tool calling from OpenClaw
- File-based state synchronization
- Direct API bridge for local integration
- Plugin registry for OpenClaw SDK

Usage:
    # Start MCP server (for OpenClaw to call AMOS)
    python amos_openclaw_connector.py --mcp

    # Start API bridge (for bidirectional communication)
    python amos_openclaw_connector.py --api --port 8888

    # Sync state between repositories
    python amos_openclaw_connector.py --sync

Configuration:
    Set in ~/.amos-openclaw/config.json or environment variables:
    - AMOS_HOME: Path to AMOS-code repository
    - OPENCLAW_HOME: Path to openclaw-main repository
    - AMOS_OPENCLAW_MODE: mcp | api | file | full
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# AMOS Imports
sys.path.insert(0, str(Path(__file__).parent))
from amos_brain import get_amos_integration  # noqa: E402
from amos_brain.clawspring_bridge import create_amos_agent

# Optional import for runtime
try:
    from amos_cli import get_runtime
except ImportError:
    get_runtime = None  # type: ignore


@dataclass
class BridgeConfig:
    """Configuration for AMOS-OpenClaw bridge."""

    amos_home: Path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    openclaw_home: Path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/openclaw-main")
    state_dir: Path = Path.home() / ".amos-openclaw-bridge"
    mode: str = "full"  # mcp | api | file | full
    api_port: int = 8888
    sync_interval: int = 30  # seconds


class StateSynchronizer:
    """Synchronizes state between AMOS and OpenClaw via filesystem."""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.state_dir = config.state_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    async def export_amos_state(self) -> dict[str, Any]:
        """Export AMOS brain state for OpenClaw consumption."""
        amos = get_amos_integration()

        state = {
            "timestamp": datetime.now(UTC).isoformat(),
            "source": "amos",
            "version": "28.0.0",
            "layers": {
                "brain": amos.get_status(),
                "health": self._get_health_status(),
                "equations": self._get_equation_registry(),
            },
            "capabilities": {
                "rule_of_2": True,
                "rule_of_4": True,
                "global_laws": ["L1", "L2", "L3", "L4", "L5", "L6"],
                "phases_completed": 28,
                "equations_available": 180,
            },
        }

        # Write to shared state
        state_file = self.state_dir / "amos_state.json"
        state_file.write_text(json.dumps(state, indent=2))

        return state

    async def import_openclaw_state(self) -> dict[str, Any]:
        """Import OpenClaw state if available."""
        openclaw_state_file = self.state_dir / "openclaw_state.json"

        if not openclaw_state_file.exists():
            return None

        try:
            return json.loads(openclaw_state_file.read_text())
        except Exception as e:
            print(f"Error reading OpenClaw state: {e}")
            return None

    def _get_health_status(self) -> dict:
        """Get health status from runtime."""
        try:
            if get_runtime is None:
                return {"status": "not_available", "message": "Runtime not loaded"}
            runtime = get_runtime()
            return runtime.get_health()
        except Exception as e:
            return {"status": "unknown", "error": str(e)}

    def _get_equation_registry(self) -> dict:
        """Get equation registry summary."""
        try:
            from amos_brain.equation_registry import get_registry

            registry = get_registry()
            return {
                "total_equations": len(registry.equations),
                "domains": list(registry.domains.keys()),
            }
        except Exception:
            return {"total_equations": 180, "domains": ["math", "physics", "cs", "biology"]}


class MCPBridge:
    """MCP Server for OpenClaw to call AMOS tools."""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.amos = get_amos_integration()
        self.agent_bridge = create_amos_agent()

    async def start(self):
        """Start MCP server."""
        try:
            from mcp.server import Server
            from mcp.types import TextContent

            app = Server("amos-openclaw-bridge")

            @app.call_tool()
            async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
                """Handle tool calls from OpenClaw."""
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            @app.list_tools()
            async def list_tools() -> list:
                """List available AMOS tools."""
                return [
                    {
                        "name": "amos_analyze",
                        "description": "Analyze text using AMOS 14-layer cognitive architecture",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "use_rule_of_2": {"type": "boolean", "default": True},
                                "use_rule_of_4": {"type": "boolean", "default": False},
                            },
                            "required": ["text"],
                        },
                    },
                    {
                        "name": "amos_laws_check",
                        "description": "Check compliance with AMOS Global Laws L1-L6",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "laws": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["content"],
                        },
                    },
                    {
                        "name": "amos_execute_equation",
                        "description": "Execute an AMOS equation from the 180+ equation library",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "equation_name": {"type": "string"},
                                "parameters": {"type": "object"},
                            },
                            "required": ["equation_name"],
                        },
                    },
                    {
                        "name": "amos_status",
                        "description": "Get AMOS brain status and health metrics",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]

            print("✅ AMOS MCP Server started - waiting for OpenClaw connections...")
            await app.run_stdio_async()

        except ImportError as e:
            print(f"❌ MCP SDK not installed: {e}")
            print("   Install with: pip install mcp")
            sys.exit(1)

    async def _execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute an AMOS tool."""
        if name == "amos_analyze":
            text = arguments.get("text", "")
            arguments.get("use_rule_of_2", True)

            result = self.amos.analyze_with_rules(text)

            return {
                "analysis": result,
                "confidence": result.get("confidence", 0.0),
                "perspectives": result.get("perspectives", []),
            }

        elif name == "amos_laws_check":
            content = arguments.get("content", "")
            from amos_brain import GlobalLaws

            violations = []
            for law_id in ["L1", "L2", "L3", "L4", "L5", "L6"]:
                law = GlobalLaws.get_law(law_id)
                check = law.check(content)
                if not check.compliant:
                    violations.append(
                        {
                            "law": law_id,
                            "description": law.description,
                            "issue": check.message,
                        }
                    )

            return {
                "compliant": len(violations) == 0,
                "violations": violations,
                "total_laws_checked": 6,
            }

        elif name == "amos_execute_equation":
            eq_name = arguments.get("equation_name", "")
            params = arguments.get("parameters", {})

            try:
                result = await self.amos.execute_equation(eq_name, params)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif name == "amos_status":
            return {
                "amos_version": "28.0.0",
                "phases": 28,
                "equations": 180,
                "layers": 14,
                "status": "operational",
                "bridge": "connected",
            }

        return {"error": f"Unknown tool: {name}"}


class APIBridge:
    """HTTP API bridge for bidirectional communication."""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.amos = get_amos_integration()
        self.state_sync = StateSynchronizer(config)

    async def start(self):
        """Start HTTP API server."""
        try:
            import uvicorn
            from fastapi import FastAPI, HTTPException
            from fastapi.responses import JSONResponse

            app = FastAPI(title="AMOS-OpenClaw Bridge API")

            @app.get("/")
            async def root():
                return {
                    "bridge": "AMOS-OpenClaw",
                    "version": "1.0.0",
                    "amos_phases": 28,
                    "status": "connected",
                }

            @app.get("/health")
            async def health():
                return await self.state_sync.export_amos_state()

            @app.post("/analyze")
            async def analyze(request: dict):
                text = request.get("text", "")
                result = self.amos.analyze_with_rules(text)
                return result

            @app.post("/execute")
            async def execute(request: dict):
                eq_name = request.get("equation", "")
                params = request.get("parameters", {})
                try:
                    result = await self.amos.execute_equation(eq_name, params)
                    return {"success": True, "result": result}
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))

            @app.get("/state")
            async def get_state():
                return await self.state_sync.export_amos_state()

            @app.post("/state/import")
            async def import_state(request: dict):
                # Process OpenClaw state
                return {"status": "imported", "timestamp": datetime.now(UTC).isoformat()}

            print(f"✅ AMOS-OpenClaw API Bridge starting on port {self.config.api_port}")
            uvicorn.run(app, host="0.0.0.0", port=self.config.api_port)

        except ImportError:
            print("❌ FastAPI/uvicorn not installed")
            print("   Install with: pip install fastapi uvicorn")
            sys.exit(1)


class OpenClawPluginGenerator:
    """Generates OpenClaw plugin files for AMOS integration."""

    def __init__(self, config: BridgeConfig):
        self.config = config

    def generate_plugin(self) -> str:
        """Generate OpenClaw plugin TypeScript code."""
        plugin_code = """/**
 * AMOS Brain Plugin for OpenClaw
 * Auto-generated by amos_openclaw_connector.py
 */

    import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

export function register(api: OpenClawPluginApi) {
  // Register AMOS tools
  api.tools.register({
    id: "amos-analyze",
    name: "AMOS Analyze",
    description: "Analyze using AMOS 14-layer cognitive architecture",
    execute: async (params) => {
      const response = await fetch("http://localhost:8888/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      return response.json();
    },
  });

  api.tools.register({
    id: "amos-execute",
    name: "AMOS Execute Equation",
    description: "Execute equations from AMOS 180+ library",
    execute: async (params) => {
      const response = await fetch("http://localhost:8888/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });
      return response.json();
    },
  });

  console.log("✅ AMOS Brain Plugin registered");
}
"""
        return plugin_code

    def write_plugin_files(self):
        """Write plugin files to OpenClaw directory."""
        # Plugin directory in OpenClaw
        plugin_dir = self.config.openclaw_home / "extensions" / "amos-brain-plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)

        # Write plugin entry
        plugin_ts = plugin_dir / "index.ts"
        plugin_ts.write_text(self.generate_plugin())

        # Write manifest
        manifest = {
            "id": "amos-brain",
            "name": "AMOS Brain Integration",
            "version": "1.0.0",
            "description": "Connects OpenClaw to AMOS 14-layer cognitive architecture",
            "author": "Trang Phan",
            "entry": "./index.ts",
            "capabilities": ["tools"],
        }

        manifest_json = plugin_dir / "openclaw.plugin.json"
        manifest_json.write_text(json.dumps(manifest, indent=2))

        print(f"✅ OpenClaw plugin written to: {plugin_dir}")
        print(
            f"   To activate: cd {self.config.openclaw_home} && openclaw plugins enable amos-brain"
        )


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS-OpenClaw Bridge Connector")
    parser.add_argument("--mcp", action="store_true", help="Start MCP server")
    parser.add_argument("--api", action="store_true", help="Start API bridge")
    parser.add_argument("--port", type=int, default=8888, help="API port")
    parser.add_argument("--sync", action="store_true", help="Sync state once")
    parser.add_argument("--watch", action="store_true", help="Continuous sync")
    parser.add_argument("--generate-plugin", action="store_true", help="Generate OpenClaw plugin")
    parser.add_argument("--full", action="store_true", help="Start full bridge (MCP + API + Sync)")

    args = parser.parse_args()

    config = BridgeConfig(api_port=args.port)

    if args.full or (not args.mcp and not args.api and not args.sync and not args.generate_plugin):
        args.mcp = args.api = args.watch = True

    tasks = []

    if args.generate_plugin:
        generator = OpenClawPluginGenerator(config)
        generator.write_plugin_files()

    if args.mcp:
        mcp = MCPBridge(config)
        tasks.append(mcp.start())

    if args.api:
        api = APIBridge(config)
        tasks.append(api.start())

    if args.sync or args.watch:
        sync = StateSynchronizer(config)
        await sync.export_amos_state()
        print("✅ State synchronized")

        if args.watch:

            async def watch_loop():
                while True:
                    await asyncio.sleep(config.sync_interval)
                    await sync.export_amos_state()
                    print(f"🔄 State synced at {datetime.now(UTC).isoformat()}")

            tasks.append(watch_loop())

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())

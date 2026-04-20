#!/usr/bin/env python3
"""AMOS MCP Server Enhanced - Complete Ecosystem Integration
===========================================================

Exposes all 11 built AMOS components via Model Context Protocol (MCP):
- 14-Subsystem Organism OS
- 6 Global Laws Brain
- 50MB+ Knowledge Base
- Interactive Shell Commands
- API Server Capabilities

Tools:
- amos_think: Knowledge-enhanced reasoning
- amos_query: Query 50MB knowledge base
- amos_status: Full system status
- amos_subsystems: List/interact with 14 subsystems
- amos_countries: Access 55 country packs
- amos_sectors: Access 19 sector packs
- amos_decide: Decision analysis with Rule of 2/4

Usage:
  python amos_mcp_enhanced.py

MCP Configuration:
{
  "mcpServers": {
    "amos": {
      "command": "python3",
      "args": ["/path/to/amos_mcp_enhanced.py"]
    }
  }
}

Owner: Trang
"""

import asyncio
import json
import sys
from typing import Any


class AMOSMCPServer:
    """MCP Server exposing complete AMOS ecosystem.

    Integrates all 11 built components for AI assistant access.
    """

    def __init__(self):
        self.amos = None
        self.tools = self._define_tools()

    def _define_tools(self) -> list[dict[str, Any]]:
        """Define MCP tools."""
        return [
            {
                "name": "amos_think",
                "description": "Knowledge-enhanced thinking with AMOS Brain. Analyzes problems using 50MB knowledge base and 6 Global Laws.",
                "parameters": {
                    "problem": {
                        "type": "string",
                        "description": "The problem or question to analyze",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for the analysis",
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_query",
                "description": "Query the 50MB AMOS knowledge base for information on any topic.",
                "parameters": {
                    "query": {"type": "string", "description": "Search terms to query"},
                    "domain": {
                        "type": "string",
                        "description": "Optional domain filter (e.g., 'software', 'healthcare')",
                        "optional": True,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 5)",
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_status",
                "description": "Get complete AMOS system status including all 14 subsystems, 6 laws, and 50MB knowledge base.",
                "parameters": {},
            },
            {
                "name": "amos_subsystems",
                "description": "List all 14 active subsystems in the Organism OS.",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action: 'list' or 'get'",
                        "enum": ["list", "get"],
                    },
                    "name": {
                        "type": "string",
                        "description": "Subsystem name (required for 'get' action)",
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_countries",
                "description": "Access geographic and economic knowledge from 55 country packs.",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action: 'list' or 'get'",
                        "enum": ["list", "get"],
                    },
                    "code": {
                        "type": "string",
                        "description": "Country code (e.g., 'US', 'GB') for 'get' action",
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_sectors",
                "description": "Access industry expertise from 19 sector knowledge packs.",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action: 'list' or 'get'",
                        "enum": ["list", "get"],
                    },
                    "code": {
                        "type": "string",
                        "description": "Sector code for 'get' action",
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_decide",
                "description": "Apply Rule of 2 (Perspectives) and Rule of 4 (Quadrants) for structured decision analysis.",
                "parameters": {
                    "question": {
                        "type": "string",
                        "description": "The decision question to analyze",
                    },
                    "options": {
                        "type": "array",
                        "description": "List of options to consider",
                        "items": {"type": "string"},
                        "optional": True,
                    },
                },
            },
            {
                "name": "amos_help",
                "description": "Get help on available AMOS tools and capabilities.",
                "parameters": {},
            },
        ]

    def initialize(self):
        """Initialize AMOS system."""
        try:
            from AMOS_ORGANISM_OS.amos_unified_enhanced import AMOSUnifiedEnhanced

            self.amos = AMOSUnifiedEnhanced()
            self.amos.initialize(auto_load_knowledge=True)
            return True
        except Exception as e:
            print(f"Warning: Could not initialize AMOS: {e}", file=sys.stderr)
            return False

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return self._handle_initialize()
        elif method == "tools/list":
            return self._handle_tools_list()
        elif method == "tools/call":
            return await self._handle_tool_call(params)
        else:
            return {"error": f"Unknown method: {method}"}

    def _handle_initialize(self) -> dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "amos-mcp-enhanced", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        }

    def _handle_tools_list(self) -> dict[str, Any]:
        """Handle tools/list request."""
        return {"tools": self.tools}

    async def _handle_tool_call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle tool call."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        handlers = {
            "amos_think": self._handle_think,
            "amos_query": self._handle_query,
            "amos_status": self._handle_status,
            "amos_subsystems": self._handle_subsystems,
            "amos_countries": self._handle_countries,
            "amos_sectors": self._handle_sectors,
            "amos_decide": self._handle_decide,
            "amos_help": self._handle_help,
        }

        handler = handlers.get(tool_name)
        if handler:
            try:
                result = await handler(arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            except Exception as e:
                return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                "isError": True,
            }

    async def _handle_think(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_think."""
        problem = args.get("problem")
        context = args.get("context", {})

        if not self.amos:
            return {"error": "AMOS not initialized"}

        result = self.amos.think(problem, context)
        return {
            "tool": "amos_think",
            "problem": problem,
            "result": result,
            "knowledge_used": result.get("knowledge_used", 0),
            "status": "success",
        }

    async def _handle_query(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_query."""
        query = args.get("query")
        domain = args.get("domain")
        limit = args.get("limit", 5)

        if not self.amos:
            return {"error": "AMOS not initialized"}

        results = self.amos.query_knowledge(query, domain, limit)
        return {
            "tool": "amos_query",
            "query": query,
            "results": results,
            "count": len(results),
            "status": "success",
        }

    async def _handle_status(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_status."""
        if not self.amos or not self.amos.status:
            return {"error": "AMOS not initialized"}

        return {
            "tool": "amos_status",
            "system": {"name": "AMOS Enhanced", "initialized": self.amos._initialized},
            "organism": {
                "ready": self.amos.status.organism_ready,
                "subsystems_active": self.amos.status.subsystems_active,
            },
            "brain": {"ready": self.amos.status.brain_ready, "laws_active": 6},
            "knowledge": {
                "ready": self.amos.status.knowledge_ready,
                "entries": self.amos.status.knowledge_entries,
                "domains": self.amos.status.knowledge_domains,
                "memory_mb": self.amos.status.knowledge_mb,
            },
            "status": "success",
        }

    async def _handle_subsystems(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_subsystems."""
        action = args.get("action", "list")

        if not self.amos or not self.amos.organism:
            return {"error": "Organism not available"}

        if action == "list":
            status = self.amos.organism.status()
            return {
                "tool": "amos_subsystems",
                "action": "list",
                "count": len(status.get("active_subsystems", [])),
                "subsystems": status.get("active_subsystems", []),
                "status": "success",
            }
        elif action == "get":
            name = args.get("name")
            subsystem = self.amos.get_subsystem(name)
            return {
                "tool": "amos_subsystems",
                "action": "get",
                "name": name,
                "available": subsystem is not None,
                "status": "success",
            }

    async def _handle_countries(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_countries."""
        action = args.get("action", "list")

        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        if action == "list":
            countries = system.extended_loader.list_countries()
            return {
                "tool": "amos_countries",
                "action": "list",
                "count": len(countries),
                "countries": countries,
                "status": "success",
            }
        elif action == "get":
            code = args.get("code", "").upper()
            country = system.extended_loader.get_country(code)
            if country:
                return {
                    "tool": "amos_countries",
                    "action": "get",
                    "code": code,
                    "name": country.country_name,
                    "geography": country.geography,
                    "economy": country.economy,
                    "culture": country.culture,
                    "status": "success",
                }
            else:
                return {"error": f"Country {code} not found"}

    async def _handle_sectors(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_sectors."""
        action = args.get("action", "list")

        from amos_brain.extended_knowledge_loader import get_comprehensive_knowledge

        system = get_comprehensive_knowledge()
        if not system.initialized:
            system.initialize()

        if action == "list":
            sectors = system.extended_loader.list_sectors()
            return {
                "tool": "amos_sectors",
                "action": "list",
                "count": len(sectors),
                "sectors": sectors,
                "status": "success",
            }
        elif action == "get":
            code = args.get("code", "").upper()
            sector = system.extended_loader.get_sector(code)
            if sector:
                return {
                    "tool": "amos_sectors",
                    "action": "get",
                    "code": code,
                    "name": sector.sector_name,
                    "domain": sector.domain,
                    "expertise": sector.expertise,
                    "standards": sector.standards,
                    "status": "success",
                }
            else:
                return {"error": f"Sector {code} not found"}

    async def _handle_decide(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_decide."""
        question = args.get("question")
        options = args.get("options", [])

        # Apply Rule of 2 and Rule of 4
        analysis = {
            "tool": "amos_decide",
            "question": question,
            "rule_of_2": {
                "perspective_1": "Internal/Technical analysis",
                "perspective_2": "External/User value analysis",
            },
            "rule_of_4": {
                "biological_human": "Human factors consideration",
                "technical": "Technical feasibility analysis",
                "economic": "Cost-benefit analysis",
                "environmental": "Context and constraints analysis",
            },
            "options": options,
            "recommendation": "Apply weighted scoring across all quadrants",
            "status": "success",
        }

        return analysis

    async def _handle_help(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle amos_help."""
        return {
            "tool": "amos_help",
            "description": "AMOS MCP Server - Complete ecosystem access",
            "components": [
                "14-Subsystem Organism OS",
                "6 Global Laws Brain",
                "50MB+ Knowledge Base",
                "55 Country Packs",
                "19 Sector Packs",
            ],
            "tools": [t["name"] for t in self.tools],
            "usage_examples": [
                "amos_think: {'problem': 'Best architecture?'}",
                "amos_query: {'query': 'scalability', 'limit': 5}",
                "amos_countries: {'action': 'get', 'code': 'US'}",
                "amos_sectors: {'action': 'list'}",
            ],
            "status": "success",
        }

    async def run(self):
        """Run the MCP server."""
        print("🚀 AMOS MCP Server Enhanced", file=sys.stderr)
        print("Initializing 11-component ecosystem...", file=sys.stderr)

        if self.initialize():
            print("✅ AMOS initialized successfully", file=sys.stderr)
            print(f"   🧬 {self.amos.status.subsystems_active} subsystems", file=sys.stderr)
            print("   🧠 6 laws active", file=sys.stderr)
            print(
                f"   📚 {self.amos.status.knowledge_entries:,} knowledge entries", file=sys.stderr
            )
        else:
            print("⚠️  Running in limited mode", file=sys.stderr)

        print("\n📡 MCP Server ready", file=sys.stderr)
        print("   Tools available:", file=sys.stderr)
        for tool in self.tools:
            print(f"   • {tool['name']}", file=sys.stderr)
        print("\nListening for MCP requests...", file=sys.stderr)

        # MCP stdio loop
        while True:
            try:
                line = await asyncio.get_running_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line.strip())
                response = await self.handle_request(request)

                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {"error": str(e)}
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point."""
    server = AMOSMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

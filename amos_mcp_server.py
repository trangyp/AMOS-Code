#!/usr/bin/env python3
"""
AMOS Brain MCP Server - Exposes cognitive architecture via Model Context Protocol.

Tools exposed:
- amos_reasoning: Apply Rule of 2 and Rule of 4 to analyze problems
- amos_laws_check: Check text compliance with Global Laws L1-L6
- amos_status: Get brain status and capabilities
- amos_decide: Full decision analysis workflow

Usage:
  #_stdio (for MCP clients like clawspring)
  python amos_mcp_server.py

  # sse (for HTTP clients)
  python amos_mcp_server.py --transport sse --port 8080

MCP Configuration (add to ~/.clawspring/mcp.json):
{
  "mcpServers": {
    "amos": {
      "type": "stdio",
      "command": "python3",
      "args": ["/path/to/amos_mcp_server.py"]
    }
  }
}
"""
from __future__ import annotations

import sys
import os
import json
import asyncio
from typing import Any
from dataclasses import dataclass

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import AMOS brain
from amos_brain import get_amos_integration, RuleOfTwo, RuleOfFour, GlobalLaws
from amos_brain.cognitive_stack import CognitiveStack


@dataclass
class Tool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: callable


class AMOSMCPServer:
    """MCP Server exposing AMOS brain capabilities."""

    def __init__(self):
        self.amos = get_amos_integration()
        self.tools = self._define_tools()

    def _define_tools(self) -> dict[str, Tool]:
        """Define MCP tools."""
        return {
            "amos_reasoning": Tool(
                name="amos_reasoning",
                description=(
                    "Apply AMOS Rule of 2 (dual perspectives) and Rule of 4 (four quadrants) "
                    "to analyze a problem with structural integrity. Returns confidence scores, "
                    "recommendations, and identified assumptions/uncertainties."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "The problem or decision to analyze"
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context for the analysis"
                        }
                    },
                    "required": ["problem"]
                },
                handler=self._handle_reasoning
            ),
            "amos_laws_check": Tool(
                name="amos_laws_check",
                description=(
                    "Check if text complies with AMOS Global Laws L4 (structural integrity) "
                    "and L5 (communication style). Returns compliance report with any violations."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to check for law compliance"
                        },
                        "check_l4": {
                            "type": "boolean",
                            "description": "Check L4 - Structural Integrity",
                            "default": True
                        },
                        "check_l5": {
                            "type": "boolean",
                            "description": "Check L5 - Communication Style",
                            "default": True
                        }
                    },
                    "required": ["text"]
                },
                handler=self._handle_laws_check
            ),
            "amos_status": Tool(
                name="amos_status",
                description=(
                    "Get AMOS Brain integration status including loaded engines, "
                    "active laws, and domain coverage."
                ),
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_status
            ),
            "amos_decide": Tool(
                name="amos_decide",
                description=(
                    "Full decision analysis workflow combining Rule of 2, Rule of 4, "
                    "and Global Laws validation. Returns comprehensive decision support."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "string",
                            "description": "The decision or problem to analyze"
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of options to consider"
                        }
                    },
                    "required": ["decision"]
                },
                handler=self._handle_decide
            ),
        }

    def _handle_reasoning(self, args: dict) -> dict:
        """Handle amos_reasoning tool."""
        problem = args.get("problem", "")
        context = args.get("context", {})

        if not problem:
            return {"error": "No problem specified"}

        result = self.amos.analyze_with_rules(problem, context)

        return {
            "problem": problem,
            "rule_of_two": {
                "confidence": result["rule_of_two"]["confidence"],
                "recommendation": result["rule_of_two"]["recommendation"],
                "perspectives": [
                    {
                        "name": p.name if hasattr(p, "name") else str(p),
                        "viewpoint": p.viewpoint if hasattr(p, "viewpoint") else str(p)
                    }
                    for p in result["rule_of_two"].get("perspectives", [])
                ]
            },
            "rule_of_four": {
                "quadrants_analyzed": result["rule_of_four"]["quadrants_analyzed"],
                "completeness_score": result["rule_of_four"]["completeness_score"]
            },
            "structural_integrity_score": result.get("structural_integrity_score", 0),
            "recommendations": result.get("recommendations", []),
            "assumptions": result.get("assumptions", []),
            "uncertainty_flags": result.get("uncertainty_flags", [])
        }

    def _handle_laws_check(self, args: dict) -> dict:
        """Handle amos_laws_check tool."""
        text = args.get("text", "")
        check_l4 = args.get("check_l4", True)
        check_l5 = args.get("check_l5", True)

        laws = GlobalLaws()
        issues = []

        if check_l4:
            statements = [s.strip() for s in text.split(".") if s.strip()]
            consistent, contradictions = laws.check_l4_integrity(statements)
            if not consistent:
                issues.extend(contradictions)

        if check_l5:
            ok, violations = laws.l5_communication_check(text)
            if not ok:
                issues.extend(violations)

        return {
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "checks_performed": ["L4" if check_l4 else None, "L5" if check_l5 else None],
            "compliant": len(issues) == 0,
            "issues_found": issues
        }

    def _handle_status(self, args: dict) -> dict:
        """Handle amos_status tool."""
        status = self.amos.get_status()
        return {
            "initialized": status.get("initialized", False),
            "brain_loaded": status.get("brain_loaded", False),
            "engines_count": status.get("engines_count", 0),
            "laws_active": status.get("laws_active", []),
            "domains_covered": status.get("domains_covered", []),
            "laws_summary": self.amos.get_laws_summary()
        }

    def _handle_decide(self, args: dict) -> dict:
        """Handle amos_decide tool."""
        decision = args.get("decision", "")
        options = args.get("options", [])

        if not decision:
            return {"error": "No decision specified"}

        # Full analysis
        analysis = self.amos.analyze_with_rules(decision)

        # Add option analysis if provided
        option_analysis = []
        if options:
            for opt in options:
                opt_result = self.amos.analyze_with_rules(f"{decision} - Option: {opt}")
                option_analysis.append({
                    "option": opt,
                    "confidence": opt_result["rule_of_two"]["confidence"],
                    "recommendation": opt_result["rule_of_two"]["recommendation"]
                })

        return {
            "decision": decision,
            "options_analyzed": option_analysis,
            "rule_of_two": {
                "confidence": analysis["rule_of_two"]["confidence"],
                "recommendation": analysis["rule_of_two"]["recommendation"]
            },
            "rule_of_four": {
                "completeness": analysis["rule_of_four"]["completeness_score"],
                "quadrants": analysis["rule_of_four"]["quadrants_analyzed"]
            },
            "recommendations": analysis.get("recommendations", []),
            "assumptions": analysis.get("assumptions", []),
            "uncertainties": analysis.get("uncertainty_flags", [])
        }

    def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "amos-brain-mcp",
                    "version": "1.0.0"
                }
            }

        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.input_schema
                    }
                    for tool in self.tools.values()
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            if tool_name in self.tools:
                result = self.tools[tool_name].handler(arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        return {"error": f"Unknown method: {method}"}

    async def run_stdio(self):
        """Run server in stdio mode (for MCP clients)."""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line)
                response = self.handle_request(request)
                response["jsonrpc"] = "2.0"
                response["id"] = request.get("id")

                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Brain MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server = AMOSMCPServer()

    if args.transport == "stdio":
        await server.run_stdio()
    else:
        print(f"SSE transport on port {args.port} not yet implemented")


if __name__ == "__main__":
    asyncio.run(main())

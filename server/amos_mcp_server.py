#!/usr/bin/env python3
"""AMOS Brain MCP Server - Exposes cognitive architecture via Model Context Protocol.

Tools exposed:
- amos_reasoning: Apply Rule of 2 and Rule of 4 to analyze problems
- amos_laws_check: Check text compliance with Global Laws L1-L6
- amos_status: Get brain status and capabilities
- amos_decide: Full decision analysis workflow

Usage:
  # stdio (for MCP clients like clawspring)
  python amos_mcp_server.py

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

import asyncio
import json
import sys
from dataclasses import dataclass
from typing import Any

# Import AMOS brain
from amos_agent_governance_toolkit import (
    CrossModelVerificationKernel,
    get_governance_toolkit,
)
from amos_brain import GlobalLaws, get_amos_integration


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
                            "description": "The problem or decision to analyze",
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context for the analysis",
                        },
                    },
                    "required": ["problem"],
                },
                handler=self._handle_reasoning,
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
                            "description": "The text to check for law compliance",
                        },
                        "check_l4": {
                            "type": "boolean",
                            "description": "Check L4 - Structural Integrity",
                            "default": True,
                        },
                        "check_l5": {
                            "type": "boolean",
                            "description": "Check L5 - Communication Style",
                            "default": True,
                        },
                    },
                    "required": ["text"],
                },
                handler=self._handle_laws_check,
            ),
            "amos_status": Tool(
                name="amos_status",
                description=(
                    "Get AMOS Brain integration status including loaded engines, "
                    "active laws, and domain coverage."
                ),
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_status,
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
                            "description": "The decision or problem to analyze",
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of options to consider",
                        },
                    },
                    "required": ["decision"],
                },
                handler=self._handle_decide,
            ),
            "amosl_compile": Tool(
                name="amosl_compile",
                description=(
                    "Compile AMOSL (Absolute Meta Operating System Language) source code. "
                    "Generates 4 intermediate representations (CIR, QIR, BIR, HIR) and "
                    "validates 8 invariant laws. Returns compilation statistics."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "AMOSL source code to compile"}
                    },
                    "required": ["source"],
                },
                handler=self._handle_amosl_compile,
            ),
            "amos_governance_evaluate": Tool(
                name="amos_governance_evaluate",
                description=(
                    "Evaluate action through 2026 Agent Governance Toolkit. "
                    "Checks semantic intent (goal hijacking), execution rings, "
                    "trust scoring, and OWASP Agentic AI compliance."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to evaluate"},
                        "component_id": {
                            "type": "string",
                            "description": "Component making request",
                        },
                        "sensitivity": {
                            "type": "string",
                            "description": "low/medium/high/critical",
                        },
                    },
                    "required": ["action", "component_id"],
                },
                handler=self._handle_governance_evaluate,
            ),
            "amos_verify_consensus": Tool(
                name="amos_verify_consensus",
                description=(
                    "Cross-Model Verification Kernel (CMVK) - Verify query against "
                    "memory poisoning via multi-model consensus. AGENT-06 protection."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query to verify"},
                        "context": {"type": "object", "description": "Optional context"},
                    },
                    "required": ["query"],
                },
                handler=self._handle_verify_consensus,
            ),
            "amos_governance_report": Tool(
                name="amos_governance_report",
                description=(
                    "Get comprehensive governance report including SLOs, "
                    "policy latency, trust distribution, and OWASP coverage."
                ),
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_governance_report,
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
                        "viewpoint": p.viewpoint if hasattr(p, "viewpoint") else str(p),
                    }
                    for p in result["rule_of_two"].get("perspectives", [])
                ],
            },
            "rule_of_four": {
                "quadrants_analyzed": result["rule_of_four"]["quadrants_analyzed"],
                "completeness_score": result["rule_of_four"]["completeness_score"],
            },
            "structural_integrity_score": result.get("structural_integrity_score", 0),
            "recommendations": result.get("recommendations", []),
            "assumptions": result.get("assumptions", []),
            "uncertainty_flags": result.get("uncertainty_flags", []),
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
            "checks_performed": [
                law_id for law_id, enabled in [("L4", check_l4), ("L5", check_l5)] if enabled
            ],
            "compliant": len(issues) == 0,
            "issues_found": issues,
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
            "laws_summary": self.amos.get_laws_summary(),
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
                option_analysis.append(
                    {
                        "option": opt,
                        "confidence": opt_result["rule_of_two"]["confidence"],
                        "recommendation": opt_result["rule_of_two"]["recommendation"],
                    }
                )

        return {
            "decision": decision,
            "options_analyzed": option_analysis,
            "rule_of_two": {
                "confidence": analysis["rule_of_two"]["confidence"],
                "recommendation": analysis["rule_of_two"]["recommendation"],
            },
            "rule_of_four": {
                "completeness": analysis["rule_of_four"]["completeness_score"],
                "quadrants": analysis["rule_of_four"]["quadrants_analyzed"],
            },
            "recommendations": analysis.get("recommendations", []),
            "assumptions": analysis.get("assumptions", []),
            "uncertainties": analysis.get("uncertainty_flags", []),
        }

    def _handle_amosl_compile(self, args: dict) -> dict:
        """Handle amosl_compile tool."""
        source = args.get("source", "")

        if not source:
            return {"error": "No AMOSL source code provided"}

        try:
            from amosl import compile_program, parse, validate_invariants

            # Parse AMOSL source
            program = parse(source)

            # Validate invariants
            inv_valid, violations = validate_invariants(program)

            # Compile to 4 IRs
            cir, qir, bir, hir = compile_program(program)

            return {
                "success": True,
                "invariants_valid": inv_valid,
                "invariant_violations": violations,
                "ir_stats": {
                    "cir_blocks": len(cir.blocks),
                    "qir_registers": len(qir.registers),
                    "bir_species": len(bir.species),
                    "hir_bridges": len(hir.bridges),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_governance_evaluate(self, args: dict) -> dict:
        """Handle amos_governance_evaluate tool."""
        import asyncio

        action = args.get("action", "")
        component_id = args.get("component_id", "")
        sensitivity = args.get("sensitivity", "medium")

        if not action or not component_id:
            return {"error": "action and component_id required"}

        toolkit = get_governance_toolkit()

        # Register component if not exists
        if component_id not in toolkit.identities:
            asyncio.run(toolkit.register_component(component_id, ["mcp_access"], initial_trust=500))

        # Evaluate action
        result = asyncio.run(
            toolkit.evaluate_action(component_id, action, {"sensitivity": sensitivity})
        )

        return {
            "allowed": result["allowed"],
            "decision": result["decision"],
            "intent_confidence": result["intent_confidence"],
            "risk_flags": result["risk_flags"],
            "execution_ring": result["execution_ring"],
            "policy_latency_ms": result["policy_latency_ms"],
            "cmvk_consensus": result.get("cmvk_consensus"),
        }

    def _handle_verify_consensus(self, args: dict) -> dict:
        """Handle amos_verify_consensus tool."""
        import asyncio

        query = args.get("query", "")
        context = args.get("context", {})

        if not query:
            return {"error": "query required"}

        cmvk = CrossModelVerificationKernel()
        result = asyncio.run(cmvk.verify(query, context))

        return {
            "query": result.query,
            "models_consulted": result.models_consulted,
            "consensus_score": result.consensus_score,
            "is_memory_poisoned": result.is_memory_poisoned(),
            "verified_answer": result.verified_answer,
            "dissenting_models": result.dissenting_models,
        }

    def _handle_governance_report(self, args: dict) -> dict:
        """Handle amos_governance_report tool."""
        toolkit = get_governance_toolkit()
        report = toolkit.get_governance_report()

        return {
            "toolkit_version": report["toolkit_version"],
            "components_registered": report["components_registered"],
            "policy_evaluations": report["policy_evaluations"],
            "policy_p99_latency_ms": report["policy_p99_latency_ms"],
            "slos": report["slos"],
            "owasp_coverage": report["owasp_coverage"],
            "circuit_breakers": report["circuit_breakers"],
        }

    def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "amos-brain-mcp", "version": "1.0.0"},
            }

        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.input_schema,
                    }
                    for tool in self.tools.values()
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            if tool_name in self.tools:
                result = self.tools[tool_name].handler(arguments)
                return {
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
                }
            else:
                return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

        return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

    async def run_stdio(self):
        """Run server in stdio mode (for MCP clients)."""
        while True:
            try:
                line = await asyncio.get_running_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line)
                response = self.handle_request(request)
                if "result" in response:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": response["result"],
                    }
                elif "error" in response:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": response["error"],
                    }
                else:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": "Malformed server response"},
                    }

                print(json.dumps(payload), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)},
                }
                print(json.dumps(error_response), flush=True)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Brain MCP Server")
    parser.add_argument("--transport", choices=["stdio"], default="stdio")
    args = parser.parse_args()

    server = AMOSMCPServer()

    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())

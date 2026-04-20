"""AMOS Brain Integration for Clawspring
======================================
Integrates AMOS Cognitive Runtime with the clawspring agent system.
Adds 'AMOS' tool for 6-layer cognitive reasoning with all built-in tools.
"""

import json
import sys

from amos_agent_bridge import AMOSAgentBridge

from clawspring.tool_registry import ToolDef, register_tool


class AMOSClawspringIntegration:
    """Bridges AMOS Cognitive Runtime to clawspring agent system.
    Provides the 'AMOS' tool for cognitive-enhanced reasoning.
    """

    def __init__(self):
        self._bridge: AMOSAgentBridge | None = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of AMOS bridge."""
        if not self._initialized:
            try:
                self._bridge = AMOSAgentBridge()
                self._initialized = True
            except Exception as e:
                print(f"[AMOS] Initialization error: {e}", file=sys.stderr)
                self._bridge = None

    def think(self, question: str, mode: str = "exploratory_mapping") -> str:
        """Run a question through AMOS cognitive layers.

        Args:
            question: The question or task to analyze
            mode: Reasoning mode (exploratory_mapping, diagnostic_analysis,
                  design_and_architecture, audit_and_critique, measurement_and_scoring)

        Returns:
            Structured analysis with AMOS quality checks

        """
        self._ensure_initialized()

        if self._bridge is None:
            return "[AMOS Error] Cognitive runtime not available."

        try:
            result = self._bridge.think(question, mode)

            # Format for readability
            output = [
                "=" * 60,
                "AMOS COGNITIVE ANALYSIS",
                "=" * 60,
                "",
                result["explanation"],
                "",
                "-- Runtime State --",
                f"Engines loaded: {len(result['runtime_state']['loaded_engines'])}",
                f"Working memory: {result['runtime_state']['working_memory']['used']}/"
                f"{result['runtime_state']['working_memory']['capacity']}",
                f"Law compliance: {'✓' if result['runtime_state']['law_compliance']['compliant'] else '✗'}",
            ]

            return "\n".join(output)

        except Exception as e:
            return f"[AMOS Error] Analysis failed: {e}"

    def analyze_task(self, task: str, context: str = "") -> str:
        """Analyze a development task using AMOS cognitive architecture.

        Args:
            task: Task description
            context: Additional context as JSON string

        Returns:
            Task analysis with developer recommendations

        """
        self._ensure_initialized()

        if self._bridge is None:
            return "[AMOS Error] Cognitive runtime not available."

        try:
            ctx = {}
            if context:
                try:
                    ctx = json.loads(context)
                except json.JSONDecodeError:
                    ctx = {"raw_context": context}

            result = self._bridge.analyze_task(task, ctx)

            output = [
                "=" * 60,
                "AMOS TASK ANALYSIS",
                "=" * 60,
                "",
                result["explanation"],
            ]

            if result.get("developer_recommendations"):
                output.extend(["", "-- Developer Recommendations --"])
                for rec in result["developer_recommendations"]:
                    output.append(f"• {rec}")

            return "\n".join(output)

        except Exception as e:
            return f"[AMOS Error] Task analysis failed: {e}"

    def design_architecture(self, requirements: str, constraints: str = "") -> str:
        """Generate architecture design with AMOS principles.

        Args:
            requirements: System requirements
            constraints: Comma-separated constraints

        Returns:
            Architecture design with UBI alignment check

        """
        self._ensure_initialized()

        if self._bridge is None:
            return "[AMOS Error] Cognitive runtime not available."

        try:
            constraint_list = [c.strip() for c in constraints.split(",") if c.strip()]
            result = self._bridge.design_architecture(requirements, constraint_list)

            output = [
                "=" * 60,
                "AMOS ARCHITECTURE DESIGN",
                "=" * 60,
                "",
                result["explanation"],
            ]

            if result.get("architecture_recommendations"):
                output.extend(["", "-- Architecture Recommendations --"])
                for rec in result["architecture_recommendations"]:
                    output.append(f"• {rec}")

            ubi = result.get("ubi_alignment", {})
            output.extend(
                [
                    "",
                    "-- UBI Alignment --",
                    f"Aligned: {'✓' if ubi.get('aligned') else '✗'}",
                    f"Score: {ubi.get('ubi_score', 0):.2f}/1.0",
                ]
            )

            return "\n".join(output)

        except Exception as e:
            return f"[AMOS Error] Architecture design failed: {e}"

    def audit_decision(self, decision: str, rationale: str) -> str:
        """Audit a decision against AMOS global laws.

        Args:
            decision: The decision to audit
            rationale: The reasoning behind it

        Returns:
            Audit report with law compliance status

        """
        self._ensure_initialized()

        if self._bridge is None:
            return "[AMOS Error] Cognitive runtime not available."

        try:
            result = self._bridge.audit_decision(decision, rationale)

            compliance = result.get("law_compliance", {})

            output = [
                "=" * 60,
                "AMOS DECISION AUDIT",
                "=" * 60,
                "",
                result["explanation"],
                "",
                "-- Law Compliance --",
                f"Rule of 2 (dual perspective): {'✓' if compliance.get('rule_of_2') else '✗'}",
                f"Structural integrity: {'✓' if compliance.get('structural_integrity') else '✗'}",
                f"Total violations: {compliance.get('total_violations', 0)}",
            ]

            return "\n".join(output)

        except Exception as e:
            return f"[AMOS Error] Audit failed: {e}"

    def get_status(self) -> str:
        """Get AMOS runtime status."""
        self._ensure_initialized()

        if self._bridge is None:
            return "[AMOS Error] Cognitive runtime not available."

        try:
            status = self._bridge.get_status()
            return json.dumps(status, indent=2)
        except Exception as e:
            return f"[AMOS Error] Status check failed: {e}"


# Global integration instance
_integration: AMOSClawspringIntegration | None = None


def get_amos_integration() -> AMOSClawspringIntegration:
    """Get or create the global AMOS integration instance."""
    global _integration
    if _integration is None:
        _integration = AMOSClawspringIntegration()
    return _integration


# Tool schema for the AMOS tool
AMOS_TOOL_SCHEMA = {
    "name": "AMOS",
    "description": (
        "Use AMOS (Adaptive Multi-layer Operating System) cognitive architecture "
        "for deep reasoning, analysis, and design tasks. AMOS applies 6 cognitive layers: "
        "meta-logic (6 global laws), structural reasoning, cognitive infrastructure, "
        "quantum reasoning, biological logic (UBI alignment), and integration kernel. "
        "Use this for complex problems requiring systematic thinking, architecture design, "
        "decision auditing, or when you need structured analysis with quality checks."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "think",
                    "analyze_task",
                    "design_architecture",
                    "audit_decision",
                    "status",
                ],
                "description": (
                    "The AMOS action to perform:\n"
                    "- think: General cognitive analysis of a question\n"
                    "- analyze_task: Analyze a development task with recommendations\n"
                    "- design_architecture: Generate system architecture with AMOS principles\n"
                    "- audit_decision: Check a decision against AMOS global laws\n"
                    "- status: Get AMOS runtime status"
                ),
            },
            "question": {
                "type": "string",
                "description": "For 'think' action: the question or problem to analyze",
            },
            "mode": {
                "type": "string",
                "enum": [
                    "exploratory_mapping",
                    "diagnostic_analysis",
                    "design_and_architecture",
                    "audit_and_critique",
                    "measurement_and_scoring",
                ],
                "description": "Cognitive mode for 'think' action (default: exploratory_mapping)",
            },
            "task": {
                "type": "string",
                "description": "For 'analyze_task' action: the task description",
            },
            "context": {
                "type": "string",
                "description": "For 'analyze_task' action: additional context (JSON string or free text)",
            },
            "requirements": {
                "type": "string",
                "description": "For 'design_architecture' action: system requirements",
            },
            "constraints": {
                "type": "string",
                "description": "For 'design_architecture' action: comma-separated constraints",
            },
            "decision": {
                "type": "string",
                "description": "For 'audit_decision' action: the decision to audit",
            },
            "rationale": {
                "type": "string",
                "description": "For 'audit_decision' action: the reasoning behind the decision",
            },
        },
        "required": ["action"],
    },
}


def _amos_tool(params: dict, config: dict) -> str:
    """Execute AMOS cognitive tool.

    Args:
        params: Tool parameters including 'action' and action-specific fields
        config: Runtime configuration

    Returns:
        AMOS analysis result

    """
    amos = get_amos_integration()
    action = params.get("action", "think")

    if action == "think":
        question = params.get("question", "")
        if not question:
            return "[AMOS Error] 'question' required for 'think' action"
        mode = params.get("mode", "exploratory_mapping")
        return amos.think(question, mode)

    elif action == "analyze_task":
        task = params.get("task", "")
        if not task:
            return "[AMOS Error] 'task' required for 'analyze_task' action"
        context = params.get("context", "")
        return amos.analyze_task(task, context)

    elif action == "design_architecture":
        requirements = params.get("requirements", "")
        if not requirements:
            return "[AMOS Error] 'requirements' required for 'design_architecture' action"
        constraints = params.get("constraints", "")
        return amos.design_architecture(requirements, constraints)

    elif action == "audit_decision":
        decision = params.get("decision", "")
        rationale = params.get("rationale", "")
        if not decision or not rationale:
            return (
                "[AMOS Error] Both 'decision' and 'rationale' required for 'audit_decision' action"
            )
        return amos.audit_decision(decision, rationale)

    elif action == "status":
        return amos.get_status()

    else:
        return f"[AMOS Error] Unknown action: {action}"


def register_amos_tool():
    """Register the AMOS tool with clawspring's tool registry."""
    tool_def = ToolDef(
        name="AMOS",
        schema=AMOS_TOOL_SCHEMA,
        func=_amos_tool,
        read_only=True,
        concurrent_safe=True,
    )
    register_tool(tool_def)
    print("[AMOS] Tool registered successfully")


# Auto-register on import
try:
    register_amos_tool()
except Exception as e:
    print(f"[AMOS] Failed to register tool: {e}", file=sys.stderr)

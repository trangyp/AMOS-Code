"""AMOS Brain tools for ClawSpring - integrates AMOS cognitive architecture."""
from __future__ import annotations

import json
from typing import Any

from tool_registry import ToolDef, register_tool

# ── AMOS Runtime Integration ───────────────────────────────────────────────

_amos_runtime = None


def _get_runtime():
    """Get or create AMOS runtime."""
    global _amos_runtime
    if _amos_runtime is None:
        from amos_runtime import get_runtime
        _amos_runtime = get_runtime()
    return _amos_runtime


# ── Tool Implementations ────────────────────────────────────────────────────

def _amos_reasoning(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Execute AMOS Rule of 2 and Rule of 4 reasoning on a problem."""
    problem = params.get("problem", "")
    ctx = params.get("context", {})

    if not problem:
        return "Error: 'problem' parameter is required"

    runtime = _get_runtime()
    result = runtime.execute_cognitive_task(problem, ctx)

    # Format the output
    lines = [
        f"# AMOS Reasoning Analysis: {problem[:50]}...",
        "",
        "## Rule of 2 (Dual Perspective Analysis)",
    ]

    for p in result.get('perspectives', []):
        lines.append(f"\n### {p['id']}: {p['stance']}")
        lines.append(f"Framing: {p['framing']}")
        lines.append(f"Questions: {', '.join(p['questions'])}")

    lines.extend(["", "## Rule of 4 (Four-Quadrant Analysis)"])
    for q_name, q_data in result.get('quadrant_analysis', {}).items():
        lines.append(f"\n### {q_name}")
        lines.append(f"Focus: {q_data['focus']}")

    lines.extend([
        "",
        "## Assumptions",
        "\n".join(f"- {a}" for a in result.get('assumptions', [])),
        "",
        "## Gap Acknowledgment",
        result.get('gap_statement', ''),
        "",
        "## Recommendation",
        result.get('recommendation', ''),
    ])

    return "\n".join(lines)


def _amos_laws(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Get AMOS Global Laws and check compliance."""
    action = params.get("action", "list")

    runtime = _get_runtime()
    laws = runtime.get_law_summary()

    if action == "list":
        lines = ["# AMOS Global Laws", ""]
        for law in laws:
            lines.append(f"## {law['id']}: {law['name']}")
            lines.append(f"Priority: {law['priority']}")
            lines.append(f"Description: {law.get('description', 'N/A')[:100]}...")
            lines.append("")
        return "\n".join(lines)

    elif action == "check":
        check_type = params.get("check_type", "analysis")
        return f"L1 Law of Law check: {check_type}\nStatus: Review against physical/biological/institutional/legal constraints"

    elif action == "validate":
        text = params.get("text", "")
        if not text:
            return "Error: 'text' parameter required"
        return f"L4 Structural Integrity: Text validation would check for contradictions in:\n{text[:100]}..."

    else:
        return f"Unknown action: {action}. Use 'list', 'check', or 'validate'"


def _amos_engines(params: dict[str, Any], config: dict[str, Any]) -> str:
    """List and query AMOS cognitive engines."""
    action = params.get("action", "list")
    query = params.get("query", "")

    runtime = _get_runtime()

    if action == "list":
        from amos_brain import BrainLoader
        loader = BrainLoader()
        loader.load()
        lines = ["# AMOS Cognitive Engines", ""]
        for kernel in loader.kernels:
            req = " [required]" if kernel.required else ""
            lines.append(f"- {kernel.name} ({kernel.id}){req}")
            lines.append(f"  Domains: {', '.join(kernel.domains)}")
        return "\n".join(lines)

    elif action == "route":
        if not query:
            return "Error: 'query' parameter required"
        from amos_brain import BrainLoader, KernelRouter
        loader = BrainLoader()
        loader.load()
        router = KernelRouter(loader)
        kernels = router.route(query)
        lines = [f"# Routing for: {query}", ""]
        lines.append(f"Active kernels: {len(kernels)}")
        for k in kernels:
            lines.append(f"- {k.name} (priority {k.priority})")
        return "\n".join(lines)

    elif action == "execute":
        if not query:
            return "Error: 'query' required"
        result = runtime.execute_cognitive_task(query)
        return f"Executed through AMOS runtime:\nTask: {result['task']}\nPerspectives: {len(result['perspectives'])}\nQuadrants: {len(result['quadrant_analysis'])}"

    else:
        return f"Unknown: {action}. Use list/route/execute"


def _amos_status(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Get AMOS Brain integration status."""
    runtime = _get_runtime()
    identity = runtime.get_identity()
    laws = runtime.get_law_summary()

    lines = [
        "# AMOS Brain Status",
        "",
        f"System: {identity.get('system_name', 'AMOS')}",
        f"Creator: {identity.get('creator', 'Trang Phan')}",
        f"Purpose: {identity.get('primary_purpose', 'N/A')[:60]}...",
        "",
        "## Active Laws",
    ]

    for law in laws[:6]:
        lines.append(f"- {law['id']}: {law['name']} (P{law['priority']})")

    return "\n".join(lines)


def _amos_enhance_prompt(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Enhance a system prompt with AMOS brain context."""
    base_prompt = params.get("prompt", "")

    if not base_prompt:
        return "Error: 'prompt' parameter is required"

    runtime = _get_runtime()
    identity = runtime.get_identity()
    laws = runtime.get_law_summary()

    amos_section = f"""# AMOS Brain (vInfinity)
System: {identity.get('system_name', 'AMOS')}
Creator: {identity.get('creator', 'Trang Phan')}
Laws: {', '.join(law['name'] for law in laws[:4])}
Gap: No embodiment, consciousness, or autonomous action
"""
    enhanced = f"{base_prompt}\n\n{amos_section}"
    return f"# Enhanced System Prompt\n\n{enhanced}"


def _amos_workflow(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Run full AMOS workflow: cognitive → execution → validation → output."""
    from amos_orchestrator import run_amos_workflow

    task = params.get("task", "")
    output_type = params.get("output_type", "structured_explanation")

    if not task:
        return "Error: 'task' parameter is required"

    return run_amos_workflow(task, output_type)


def _amos_code(params: dict[str, Any], config: dict[str, Any]) -> str:
    """Generate AMOS-compliant code for specified layer."""
    from amos_coding_engine import get_coding_engine

    layer = params.get("layer", "backend")
    function_name = params.get("function_name", "")
    description = params.get("description", "")
    inputs = params.get("inputs", [])
    outputs = params.get("outputs", [])

    if not function_name or not description:
        return "Error: 'function_name' and 'description' are required"

    engine = get_coding_engine()
    result = engine.generate_code(layer, function_name, description, inputs, outputs)

    lines = [
        f"# AMOS Code Generation: {result.function_name}",
        f"Layer: {result.layer}",
        f"Quality Score: {result.quality_score}",
        f"Law Compliance: {all(result.law_compliance.values())}",
        "",
        "## Generated Code",
        "```python",
        result.code,
        "```",
        "",
        "## Explanation",
        result.explanation,
        "",
        "## Gap Acknowledgment",
        result.gap_acknowledgment,
        "",
        "## Assumptions",
    ]
    for assumption in result.assumptions:
        lines.append(f"- {assumption}")

    return "\n".join(lines)


# ── Tool Schemas ─────────────────────────────────────────────────────────────

AMOS_TOOLS = [
    ToolDef(
        name="AMOSReasoning",
        schema={
            "name": "AMOSReasoning",
            "description": (
            "Apply AMOS Rule of 2 and Rule of 4 to analyze a problem. "
            "Returns confidence, recommendations, and assumptions."
        ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "The problem or question to analyze"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context dictionary for the analysis"
                    }
                },
                "required": ["problem"]
            }
        },
        func=_amos_reasoning,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSLaws",
        schema={
            "name": "AMOSLaws",
            "description": (
            "Access AMOS Global Laws (L1-L6). "
            "Can list laws, check compliance, validate text."
        ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "check", "validate"],
                        "description": "Action to perform: list laws, check L1 compliance, or validate L4 integrity"
                    },
                    "check_type": {
                        "type": "string",
                        "description": "For 'check' action: type of action to validate (e.g., 'analysis', 'design')"
                    },
                    "text": {
                        "type": "string",
                        "description": "For 'validate' action: text to check for contradictions"
                    }
                },
                "required": ["action"]
            }
        },
        func=_amos_laws,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEngines",
        schema={
            "name": "AMOSEngines",
            "description": (
            "Query AMOS cognitive engines. List, route, or execute queries."
        ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "route", "execute"],
                        "description": "Action: list engines, route query, or execute through engines"
                    },
                    "query": {
                        "type": "string",
                        "description": "For 'route' or 'execute' actions: the query to process"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for execute action"
                    }
                },
                "required": ["action"]
            }
        },
        func=_amos_engines,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSStatus",
        schema={
            "name": "AMOSStatus",
            "description": "Get AMOS Brain integration status, loaded domains, and active laws.",
            "input_schema": {
                "type": "object",
                "properties": {},
            }
        },
        func=_amos_status,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEnhancePrompt",
        schema={
            "name": "AMOSEnhancePrompt",
            "description": (
            "Enhance a system prompt with AMOS brain context."
        ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Base system prompt to enhance"
                    }
                },
                "required": ["prompt"]
            }
        },
        func=_amos_enhance_prompt,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSWorkflow",
        schema={
            "name": "AMOSWorkflow",
            "description": (
            "Run full AMOS 4-step workflow: cognitive analysis → execution → "
            "law validation → final output. Most comprehensive AMOS tool."
        ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task or question to process through full AMOS workflow"
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["structured_explanation", "decision_recommendation",
                                 "framework_design", "research_analysis", "diagnostic"],
                        "description": "Type of output to produce"
                    }
                },
                "required": ["task"]
            }
        },
        func=_amos_workflow,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSCode",
        schema={
            "name": "AMOSCode",
            "description": (
                "Generate AMOS-compliant code for architecture, backend, "
                "database, or AI layers with embedded gap acknowledgment."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "layer": {
                        "type": "string",
                        "enum": ["architecture", "backend", "database", "ai"],
                        "description": "Coding layer to use"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function/component to generate"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the code should do"
                    },
                    "inputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Input parameters"
                    },
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Expected outputs"
                    }
                },
                "required": ["layer", "function_name", "description"]
            }
        },
        func=_amos_code,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSDesign",
        schema={
            "name": "AMOSDesign",
            "description": (
                "Generate UI/UX design with biological constraints. "
                "Produces design system, copy blocks, interaction flows, "
                "and accessibility notes with UBI alignment (L6)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "component_type": {
                        "type": "string",
                        "enum": ["form", "dialog", "card", "navigation", "dashboard"],
                        "description": "Type of UI component to design"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "What the component helps the user accomplish"
                    },
                    "user_segments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Target user segments"
                    },
                    "accessibility": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable accessibility requirements (WCAG AA)"
                    }
                },
                "required": ["component_type", "purpose"]
            }
        },
        func=_amos_design,
        read_only=True,
        concurrent_safe=True,
    ),
]


# ── Registration ──────────────────────────────────────────────────────────────

def _ensure_amos() -> None:
    """Lightweight AMOS check - doesn't load heavy resources."""
    # Just verify the runtime module is available
    # Actual runtime loading is deferred until tool is used
    from amos_runtime import AMOSRuntime
    return


def register_amos_tools() -> None:
    """Register all AMOS tools with the tool registry."""
    for tool in AMOS_TOOLS:
        register_tool(tool)

    # Lightweight initialization check - doesn't block
    try:
        _ensure_amos()
    except Exception as e:
        print(f"[AMOS] Warning: AMOS tools not available: {e}")


# Auto-register on import
register_amos_tools()

"""AMOS Brain Tools - Register brain capabilities as clawspring tools."""
from __future__ import annotations

import json
import os
import sys

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amos_brain.integration import get_amos_integration


def amos_decide(problem: str, include_rule2: bool = True, include_rule4: bool = True) -> str:
    """Analyze a decision or problem using AMOS Brain structured reasoning.

    Applies Rule of 2 (dual perspectives) and Rule of 4 (four quadrants)
    to provide structured decision analysis.

    Args:
        problem: The decision or problem to analyze
        include_rule2: Whether to apply Rule of 2 (dual perspective)
        include_rule4: Whether to apply Rule of 4 (four quadrants)

    Returns:
        Structured analysis result
    """
    amos = get_amos_integration()

    if not amos or not amos._initialized:
        return json.dumps({"error": "AMOS brain not initialized", "status": "failed"}, indent=2)

    # Pre-process the problem
    pre = amos.pre_process(problem)
    if pre.get("blocked"):
        return json.dumps(
            {
                "error": f"Problem blocked: {pre.get('reason')}",
                "law": pre.get("law"),
                "status": "blocked",
            },
            indent=2,
        )

    # Full reasoning analysis
    analysis = amos.analyze_with_rules(problem)

    # Format the result
    result = {
        "problem": problem,
        "status": "analyzed",
        "rule_of_two": {},
        "rule_of_four": {},
        "recommendations": analysis.get("recommendations", []),
        "assumptions": analysis.get("assumptions", []),
        "uncertainties": analysis.get("uncertainty_flags", []),
        "structural_integrity_score": analysis.get("structural_integrity_score", 0.0),
    }

    if include_rule2 and "rule_of_two" in analysis:
        r2 = analysis["rule_of_two"]
        perspectives = r2.get("perspectives", [])
        result["rule_of_two"] = {
            "perspectives": [
                {
                    "name": p.name if hasattr(p, "name") else str(p),
                    "viewpoint": p.viewpoint if hasattr(p, "viewpoint") else str(p),
                    "evidence": p.supporting_evidence if hasattr(p, "supporting_evidence") else [],
                    "limitations": p.limitations if hasattr(p, "limitations") else [],
                }
                for p in perspectives
            ],
            "synthesis": r2.get("synthesis", {}),
            "confidence": r2.get("confidence", 0.0),
        }

    if include_rule4 and "rule_of_four" in analysis:
        r4 = analysis["rule_of_four"]
        result["rule_of_four"] = {
            "quadrants_analyzed": r4.get("quadrants_analyzed", []),
            "completeness_score": r4.get("completeness_score", 0.0),
            "integration": r4.get("integration", {}),
        }

    return json.dumps(result, indent=2)


def amos_laws_check(text: str, check_l4: bool = True, check_l5: bool = True) -> str:
    """Check if text complies with AMOS Global Laws.

    Checks:
    - L4: Structural integrity (contradictions)
    - L5: Communication style (prohibited terms)

    Args:
        text: The text to check
        check_l4: Whether to check L4 (structural integrity)
        check_l5: Whether to check L5 (communication)

    Returns:
        Compliance report
    """
    from amos_brain.laws import GlobalLaws

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

    checks_performed: list[str] = []
    if check_l4:
        checks_performed.append("L4 - Structural Integrity")
    if check_l5:
        checks_performed.append("L5 - Communication Style")

    result = {
        "text_preview": text[:100] + "..." if len(text) > 100 else text,
        "checks_performed": checks_performed,
        "issues_found": issues,
        "compliant": len(issues) == 0,
    }

    return json.dumps(result, indent=2)


def amos_status() -> str:
    """Get AMOS Brain integration status.

    Returns:
        Current brain status including loaded engines, active laws, and domains
    """
    amos = get_amos_integration()
    status = amos.get_status()

    return json.dumps(
        {
            "initialized": status.get("initialized", False),
            "brain_loaded": status.get("brain_loaded", False),
            "engines_count": status.get("engines_count", 0),
            "laws_active": status.get("laws_active", []),
            "domains_covered": status.get("domains_covered", []),
            "laws_summary": amos.get_laws_summary() if amos._initialized else "Not initialized",
        },
        indent=2,
    )


def amos_route(query: str) -> str:
    """Determine which AMOS cognitive engines should handle a query.

    Args:
        query: The query to route

    Returns:
        List of engines that would handle this query
    """
    amos = get_amos_integration()

    if not amos or not amos._initialized:
        return json.dumps({"error": "AMOS brain not initialized"}, indent=2)

    from amos_brain.cognitive_stack import CognitiveStack

    stack = CognitiveStack()
    engines = stack.route_query(query)

    return json.dumps(
        {
            "query": query,
            "routed_engines": engines,
            "engine_count": len(engines),
            "coverage": "full" if len(engines) == len(stack.engines) else "targeted",
        },
        indent=2,
    )


# Tool schema definitions for registration
AMOS_TOOLS = [
    {
        "name": "amos_decide",
        "description": "Analyze a decision using AMOS Brain Rule of 2 (dual perspective) and Rule of 4 (four quadrants). Provides structured reasoning for complex decisions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "problem": {"type": "string", "description": "The decision or problem to analyze"},
                "include_rule2": {
                    "type": "boolean",
                    "description": "Whether to apply Rule of 2 (dual perspective analysis)",
                    "default": True,
                },
                "include_rule4": {
                    "type": "boolean",
                    "description": "Whether to apply Rule of 4 (four quadrant analysis)",
                    "default": True,
                },
            },
            "required": ["problem"],
        },
    },
    {
        "name": "amos_laws_check",
        "description": "Check if text complies with AMOS Global Laws L4 (structural integrity) and L5 (communication style).",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to check for law compliance"},
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
    },
    {
        "name": "amos_status",
        "description": "Get AMOS Brain integration status including loaded engines, active laws, and domain coverage.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "amos_route",
        "description": "Determine which AMOS cognitive engines should handle a query based on domain routing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to route to cognitive engines",
                }
            },
            "required": ["query"],
        },
    },
]


def register_amos_tools() -> None:
    """Register AMOS tools with clawspring if available."""
    try:
        from clawspring.tools import register_tool

        register_tool("amos_decide", amos_decide)
        register_tool("amos_laws_check", amos_laws_check)
        register_tool("amos_status", amos_status)
        register_tool("amos_route", amos_route)

        print("[AMOS] Brain tools registered successfully")
    except ImportError:
        # clawspring not available, skip registration
        pass
    except Exception as e:
        print(f"[AMOS] Failed to register tools: {e}")


# Auto-register on import
register_amos_tools()

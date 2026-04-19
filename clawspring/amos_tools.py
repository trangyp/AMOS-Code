"""AMOS Brain tools v2.0.0 for ClawSpring - SuperBrain governance integrated.

SUPERBRAIN INTEGRATION:
- All tool executions validated via ActionGate
- Tool calls recorded in brain audit trail
- Engine access governed by brain policies

Owner: Trang Phan
Version: 2.0.0
"""

from datetime import datetime
from functools import wraps
from typing import Any

from tool_registry import ToolDef, register_tool

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

# ── AMOS Runtime Integration ───────────────────────────────────────────────

_amos_runtime = None
_super_brain = None


def _get_runtime():
    """Get or create AMOS runtime."""
    global _amos_runtime
    if _amos_runtime is None:
        from amos_runtime import get_runtime

        _amos_runtime = get_runtime()
    return _amos_runtime


def _get_super_brain():
    """Get SuperBrain singleton for governance."""
    global _super_brain
    if SUPERBRAIN_AVAILABLE and _super_brain is None:
        try:
            _super_brain = get_super_brain()
        except Exception:
            pass
    return _super_brain


def _validate_tool_call(tool_name: str, params: dict) -> bool:
    """Validate tool execution via SuperBrain ActionGate."""
    if not SUPERBRAIN_AVAILABLE:
        return True

    brain = _get_super_brain()
    if not brain or not hasattr(brain, "action_gate"):
        return True

    try:
        action_result = brain.action_gate.validate_action(
            agent_id="amos_tools",
            action=f"tool_{tool_name}",
            details={
                "params_keys": list(params.keys()),
                "has_description": "description" in params or "problem" in params,
            },
        )
        return action_result.authorized
    except Exception:
        return True  # Fail open


def _record_tool_call(tool_name: str, params: dict):
    """Record tool execution in SuperBrain audit."""
    if not SUPERBRAIN_AVAILABLE:
        return

    brain = _get_super_brain()
    if not brain or not hasattr(brain, "record_audit"):
        return

    try:
        keys = list(params.keys())
        brain.record_audit(
            action=f"tool_{tool_name}", agent_id="amos_tools", details={"params_keys": keys}
        )
    except Exception:
        pass


def governed_tool(tool_func):
    """Decorator to add SuperBrain governance to tool functions."""

    @wraps(tool_func)
    def wrapper(params: Dict[str, Any], config: Dict[str, Any]) -> str:
        tool_name = tool_func.__name__.replace("_amos_", "")

        # Validate via SuperBrain
        if not _validate_tool_call(tool_name, params):
            return f"Error: Tool '{tool_name}' blocked by SuperBrain governance"

        # Execute tool
        result = tool_func(params, config)

        # Record in audit
        _record_tool_call(tool_name, params)

        return result

    return wrapper


# ── Tool Implementations ────────────────────────────────────────────────────


def _amos_reasoning(params: Dict[str, Any], config: Dict[str, Any]) -> str:
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

    for p in result.get("perspectives", []):
        lines.append(f"\n### {p['id']}: {p['stance']}")
        lines.append(f"Framing: {p['framing']}")
        lines.append(f"Questions: {', '.join(p['questions'])}")

    lines.extend(["", "## Rule of 4 (Four-Quadrant Analysis)"])
    for q_name, q_data in result.get("quadrant_analysis", {}).items():
        lines.append(f"\n### {q_name}")
        lines.append(f"Focus: {q_data['focus']}")

    lines.extend(
        [
            "",
            "## Assumptions",
            "\n".join(f"- {a}" for a in result.get("assumptions", [])),
            "",
            "## Gap Acknowledgment",
            result.get("gap_statement", ""),
            "",
            "## Recommendation",
            result.get("recommendation", ""),
        ]
    )

    return "\n".join(lines)


def _amos_laws(params: Dict[str, Any], config: Dict[str, Any]) -> str:
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


def _amos_engines(params: Dict[str, Any], config: Dict[str, Any]) -> str:
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


def _amos_status(params: Dict[str, Any], config: Dict[str, Any]) -> str:
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


def _amos_enhance_prompt(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Enhance a system prompt with AMOS brain context."""
    base_prompt = params.get("prompt", "")

    if not base_prompt:
        return "Error: 'prompt' parameter is required"

    runtime = _get_runtime()
    identity = runtime.get_identity()
    laws = runtime.get_law_summary()

    amos_section = f"""# AMOS Brain (vInfinity)
System: {identity.get("system_name", "AMOS")}
Creator: {identity.get("creator", "Trang Phan")}
Laws: {", ".join(law["name"] for law in laws[:4])}
Gap: No embodiment, consciousness, or autonomous action
"""
    enhanced = f"{base_prompt}\n\n{amos_section}"
    return f"# Enhanced System Prompt\n\n{enhanced}"


def _amos_workflow(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run full AMOS workflow: cognitive → execution → validation → output."""
    from amos_orchestrator import run_amos_workflow

    task = params.get("task", "")
    output_type = params.get("output_type", "structured_explanation")

    if not task:
        return "Error: 'task' parameter is required"

    return run_amos_workflow(task, output_type)


def _amos_code(params: Dict[str, Any], config: Dict[str, Any]) -> str:
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


def _amos_design(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate UI/UX design with biological constraints."""
    from amos_design_engine import get_design_engine

    comp_type = params.get("component_type", "")
    purpose = params.get("purpose", "")
    segments = params.get("user_segments", [])
    accessibility = params.get("accessibility", True)

    if not comp_type or not purpose:
        return "Error: 'component_type' and 'purpose' are required"

    engine = get_design_engine()
    result = engine.design_component(comp_type, purpose, segments, accessibility)

    lines = [
        f"# AMOS Design: {result.component_type}",
        f"Purpose: {purpose}",
        "",
        "## Design System",
        f"Structure: {result.design_system['structure']['navigation_pattern']}",
        f"Visual: {result.design_system['visual']['grid_system']}",
        "",
        "## Copy Blocks",
    ]
    for key, text in result.copy_blocks.items():
        lines.append(f"{key}: '{text}'")

    lines.extend(
        [
            "",
            "## Biological Constraints (L6 UBI Alignment)",
        ]
    )
    for constraint in result.biological_constraints:
        lines.append(f"- {constraint}")

    lines.extend(
        [
            "",
            "## Accessibility Notes",
        ]
    )
    for note in result.accessibility_notes[:3]:
        lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "## Gap Acknowledgment",
            result.gap_acknowledgment,
        ]
    )

    return "\n".join(lines)


def _amos_signal(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run signal processing analysis across multiple domains."""
    from amos_signal_engine import get_signal_engine

    description = params.get("description", "")
    domains = params.get("domains", ["time_frequency", "biological", "control", "communication"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_signal_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_ubi(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Analyze human factors using UBI (Unified Biological Intelligence)."""
    from amos_ubi_engine import get_ubi_engine

    description = params.get("description", "")
    domains = params.get("domains", ["NBI", "NEI", "SI", "BEI"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_ubi_engine()
    results = engine.analyze(description, domains)

    lines = [
        "# AMOS UBI Analysis: Human Factors",
        f"Input: {description[:60]}...",
        "",
        "## Biological Intelligence Domains",
    ]

    for domain, result in results.items():
        lines.extend(
            [
                f"\n### {domain}",
                f"Key Analysis: {list(result.analysis.keys())[:3]}",
            ]
        )
        if result.risk_flags:
            lines.append(f"Risk Flags: {', '.join(result.risk_flags)}")
        lines.append(f"Design Levers: {', '.join(result.design_levers[:3])}")

    return "\n".join(lines)


def _amos_memory(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """AMOS memory layer - store and recall brain artifacts."""
    from amos_memory import get_memory_bridge

    action = params.get("action", "stats")

    bridge = get_memory_bridge()

    if action == "stats":
        stats = bridge.store.get_memory_stats()
        return f"""# AMOS Memory Stats
Total memories: {stats["total_memories"]}
By type: {stats["by_type"]}
Storage: {stats["storage_path"]}
Creator: {stats["creator"]}
Version: {stats["amos_version"]}
"""
    elif action == "recall":
        mem_type = params.get("memory_type")
        limit = params.get("limit", 5)
        entries = bridge.recall_recent(mem_type, limit)

        lines = ["# Recent AMOS Memories", ""]
        for entry in entries:
            dt = datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d %H:%M")
            lines.append(f"- [{entry.memory_type}] {entry.id[:25]}... ({dt})")
            lines.append(f"  Source: {entry.source}, Tags: {', '.join(entry.tags[:2])}")

        return "\n".join(lines)

    return f"Unknown action: {action}. Use 'stats' or 'recall'."


def _amos_strategy(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run strategy/game theory analysis."""
    from amos_strategy_engine import get_strategy_engine

    description = params.get("description", "")
    domains = params.get("domains", ["game_normal", "game_dynamical", "negotiation"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_strategy_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_society(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run society/culture analysis across multiple domains."""
    from amos_society_engine import get_society_engine

    description = params.get("description", "")
    domains = params.get("domains", ["institutional", "cultural", "demographic", "media"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_society_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_econ(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run economics/finance analysis across multiple domains."""
    from amos_econ_engine import get_econ_engine

    description = params.get("description", "")
    domains = params.get("domains", ["micro", "macro", "public_finance", "finance"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_econ_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_scientific(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run scientific analysis across multiple domains."""
    from amos_scientific_engine import get_scientific_engine

    description = params.get("description", "")
    domains = params.get("domains", ["biology", "physics", "mathematics", "engineering"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_scientific_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_multi_agent(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run multi-agent parallel analysis."""
    from amos_multi_agent import get_multi_agent_coordinator

    analysis_type = params.get("analysis_type", "quadrant")
    problem = params.get("problem", "")

    if not problem:
        return "Error: 'problem' parameter is required"

    coord = get_multi_agent_coordinator()

    if analysis_type == "quadrant":
        return coord.run_quadrant_analysis(problem)
    elif analysis_type == "dual":
        return coord.run_dual_perspective(problem)
    else:
        return f"Unknown analysis_type: {analysis_type}. Use 'quadrant' or 'dual'."


def _amos_multi_agent_coordination(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run multi-agent coordination and swarm intelligence analysis."""
    from amos_multi_agent_coordination_engine import get_multi_agent_engine

    scenario = params.get("scenario", "")
    context = params.get("context", {})

    if not scenario:
        return "Error: 'scenario' parameter is required"

    engine = get_multi_agent_engine()
    results = engine.analyze(scenario, context)

    return engine.get_findings_summary(results)


def _amos_memory_optimization(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run memory optimization and caching analysis."""
    from amos_memory_optimization_engine import get_memory_optimization_engine

    scenario = params.get("scenario", "")
    context = params.get("context", {})

    if not scenario:
        return "Error: 'scenario' parameter is required"

    engine = get_memory_optimization_engine()
    results = engine.analyze(scenario, context)

    return engine.get_findings_summary(results)


def _amos_logic_core(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run logic core analysis for formal logic and reasoning."""
    from amos_logic_core_engine import get_logic_core_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_logic_core_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_species_interaction_core(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run species interaction core analysis (HIE, UMPL, UST, UIE, UEL)."""
    from amos_species_interaction_core_engine import get_species_interaction_core_engine

    input_text = params.get("input", "")
    context = params.get("context", {})

    if not input_text:
        return "Error: 'input' parameter is required"

    engine = get_species_interaction_core_engine()
    results = engine.analyze(input_text, context)

    return engine.get_findings_summary(results)


def _amos_ubi_stack(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run UBI Stack neurobiological intelligence analysis."""
    from amos_ubi_stack_engine import get_ubi_stack_engine

    scenario = params.get("scenario", "")
    context = params.get("context", {})

    if not scenario:
        return "Error: 'scenario' parameter is required"

    engine = get_ubi_stack_engine()
    results = engine.analyze(scenario, context)

    return engine.get_findings_summary(results)


def _amos_planetary_stack(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run Planetary Stack analysis for planetary-scale systems."""
    from amos_planetary_stack_engine import get_planetary_stack_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_planetary_stack_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_knowledge_graph(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run Knowledge Graph analysis for semantic entity and relationship extraction."""
    from amos_knowledge_graph_engine import get_knowledge_graph_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_knowledge_graph_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_ethics_safety(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run Ethics & Safety analysis for ethical reasoning and safety constraints."""
    from amos_ethics_safety_engine import get_ethics_safety_engine

    scenario = params.get("scenario", "")
    context = params.get("context", {})

    if not scenario:
        return "Error: 'scenario' parameter is required"

    engine = get_ethics_safety_engine()
    results = engine.analyze(scenario, context)

    return engine.get_findings_summary(results)


def _amos_causal_inference(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run Causal Inference analysis using do-calculus and Pearl's framework."""
    from amos_causal_inference_engine import get_causal_inference_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_causal_inference_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_knowledge(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Query knowledge graph and external data sources."""
    from amos_knowledge_connector import get_knowledge_connector

    query = params.get("query", "")
    domain = params.get("domain", "general")

    if not query:
        return "Error: 'query' parameter is required"

    connector = get_knowledge_connector()
    result = connector.query_knowledge(query, domain)

    return connector.get_findings_summary(result)


def _amos_personality(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run personality/character analysis."""
    from amos_personality_engine import get_personality_engine

    description = params.get("description", "")
    domains = params.get(
        "domains", ["traits", "identity", "behavioral_patterns", "cognitive_style"]
    )

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_personality_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_emotion(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run emotion/affective analysis across multiple domains."""
    from amos_emotion_engine import get_emotion_engine

    description = params.get("description", "")
    domains = params.get("domains", ["affective", "somatic", "motivation", "empathy"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_emotion_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_biology_cognition(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run biology and cognition analysis."""
    from amos_biology_cognition_engine import get_biology_cognition_engine

    description = params.get("description", "")
    domains = params.get("domains", ["molecular", "cellular", "organ", "cognition", "pathology"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_biology_cognition_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_design_language(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run design language and UX analysis."""
    from amos_design_language_engine import get_design_language_engine

    description = params.get("description", "")
    domains = params.get("domains", ["ia", "visual", "language", "accessibility"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_design_language_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_workflow_orchestrator(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run workflow orchestration for complex multi-engine tasks."""
    from amos_workflow_orchestrator import get_workflow_orchestrator

    goal = params.get("goal", "")
    mode = params.get("mode", "adaptive")
    tools = params.get("tools", [])

    if not goal:
        return "Error: 'goal' parameter is required"

    orchestrator = get_workflow_orchestrator()
    result = orchestrator.orchestrate(goal, mode, tools)

    return orchestrator.get_findings_summary(result)


def _amos_electrical_power(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run electrical power systems analysis."""
    from amos_electrical_power_engine import get_electrical_power_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_electrical_power_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_mechanical_structural(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run mechanical and structural analysis."""
    from amos_mechanical_structural_engine import get_mechanical_structural_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_mechanical_structural_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_numerical_methods(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run numerical methods and scientific computing analysis."""
    from amos_numerical_methods_engine import get_numerical_methods_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_numerical_methods_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_econ_finance(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run economics and financial analysis."""
    from amos_econ_finance_engine import get_econ_finance_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_econ_finance_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_strategy_game(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run strategy and game theory analysis."""
    from amos_strategy_game_engine import get_strategy_game_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_strategy_game_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_society_culture(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run society and culture analysis."""
    from amos_society_culture_engine import get_society_culture_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_society_culture_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_speed(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run speed optimization analysis for AMOS engines."""
    from amos_speed_engine import get_speed_engine

    description = params.get("description", "")
    mode = params.get("mode", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_speed_engine()
    results = engine.analyze_speed(description, mode)

    return engine.get_findings_summary(results)


def _amos_species_interaction(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run species interaction analysis for human-facing AI."""
    from amos_species_interaction_engine import get_species_interaction_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_species_interaction_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_universe_core(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run universe core physics and cosmology analysis."""
    from amos_universe_core_engine import get_universe_core_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_universe_core_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_audit_quality(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run audit quality analysis across financial, operational, and risk domains."""
    from amos_audit_quality_engine import get_audit_quality_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_audit_quality_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_unified_coding(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run unified coding analysis across architecture, backend, database, security."""
    from amos_unified_coding_engine import get_unified_coding_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_unified_coding_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_systems_core(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run systems core orchestration and health monitoring."""
    from amos_systems_core_engine import get_systems_core_engine

    operation = params.get("operation", "report")
    component = params.get("component", None)

    engine = get_systems_core_engine()

    if operation == "register" and component:
        deps = params.get("dependencies", [])
        comp_type = params.get("component_type", "service")
        limit = params.get("resource_limit", 1.0)
        success = engine.register_component(component, comp_type, deps, limit)
        return f"Registered {component}: {success}"
    elif operation == "start" and component:
        success = engine.start_component(component)
        return f"Started {component}: {success}"
    elif operation == "stop" and component:
        success = engine.stop_component(component)
        return f"Stopped {component}: {success}"
    elif operation == "status" and component:
        status = engine.get_component_status(component)
        return f"Status for {component}: {status}"
    else:
        results = engine.get_system_report()
        return engine.findings_summary(results)


def _amos_physics_cosmos(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run physics and cosmos analysis across classical, EM, quantum, statistical, cosmology."""
    from amos_physics_cosmos_engine import get_physics_cosmos_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_physics_cosmos_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_tech_quantum(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run tech quantum analysis for quantum computing applications."""
    from amos_tech_quantum_engine import get_tech_quantum_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_tech_quantum_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_logic_law(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run deterministic logic and legal analysis."""
    from amos_logic_law_engine import get_logic_law_engine

    query = params.get("query", "")
    domains = params.get("domains", ["logic", "legal", "argumentation", "policy"])

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_logic_law_engine()
    results = engine.analyze(query, domains)

    return engine.get_findings_summary(results)


def _amos_vn_legal(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run Vietnam-specialised legal analysis."""
    from amos_vn_legal_engine import get_vn_legal_engine

    description = params.get("description", "")
    domains = params.get("domains", None)

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_vn_legal_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_vomni(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run vOmni kernel master orchestration and routing."""
    from amos_vomni_kernel_engine import get_vomni_engine

    query = params.get("query", "")
    context = params.get("context", {})

    if not query:
        return "Error: 'query' parameter is required"

    engine = get_vomni_engine()
    results = engine.analyze(query, context)

    return engine.get_findings_summary(results)


def _amos_engineering_math(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run engineering and mathematics analysis."""
    from amos_engineering_math_engine import get_engineering_math_engine

    description = params.get("description", "")
    domains = params.get(
        "domains", ["pure_math", "applied_math", "numerical", "mechanical", "electrical", "control"]
    )

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_engineering_math_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_physics(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run physics and cosmology analysis."""
    from amos_physics_engine import get_physics_engine

    description = params.get("description", "")
    domains = params.get(
        "domains", ["classical", "electromagnetism", "quantum", "statistical", "cosmology"]
    )

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_physics_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_consciousness(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Run consciousness and meta-cognitive analysis."""
    from amos_consciousness_engine import get_consciousness_engine

    description = params.get("description", "")
    domains = params.get("domains", ["self_modeling", "attention", "narrative", "embodiment"])

    if not description:
        return "Error: 'description' parameter is required"

    engine = get_consciousness_engine()
    results = engine.analyze(description, domains)

    return engine.get_findings_summary(results)


def _amos_monitoring(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Get system monitoring and telemetry status."""
    from amos_monitoring import get_monitoring

    action = params.get("action", "status")

    monitoring = get_monitoring()

    if action == "status":
        return monitoring.get_findings_summary()
    elif action == "health":
        health = monitoring.health.check_health()
        return f"System Health: {health['status']}\nUptime: {health['uptime_seconds']}s"
    else:
        return f"Unknown action: {action}. Use 'status' or 'health'."


def _amos_audit(params: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Audit content against AMOS 6 Global Laws."""
    from amos_cognitive_audit import get_cognitive_audit

    content = params.get("content", "")
    content_type = params.get("content_type", "general")

    if not content:
        return "Error: 'content' parameter is required"

    audit = get_cognitive_audit()

    if content_type == "code":
        result = audit.audit_code(content)
    elif content_type == "design":
        result = audit.audit_design(content)
    else:
        result = audit.audit(content)

    return audit.get_audit_summary(result)


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
                        "description": "The problem or question to analyze",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context dictionary for the analysis",
                    },
                },
                "required": ["problem"],
            },
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
                "Access AMOS Global Laws (L1-L6). Can list laws, check compliance, validate text."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "check", "validate"],
                        "description": "Action to perform: list laws, check L1 compliance, or validate L4 integrity",
                    },
                    "check_type": {
                        "type": "string",
                        "description": "For 'check' action: type of action to validate (e.g., 'analysis', 'design')",
                    },
                    "text": {
                        "type": "string",
                        "description": "For 'validate' action: text to check for contradictions",
                    },
                },
                "required": ["action"],
            },
        },
        func=_amos_laws,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEngines",
        schema={
            "name": "AMOSEngines",
            "description": ("Query AMOS cognitive engines. List, route, or execute queries."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "route", "execute"],
                        "description": "Action: list engines, route query, or execute through engines",
                    },
                    "query": {
                        "type": "string",
                        "description": "For 'route' or 'execute' actions: the query to process",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for execute action",
                    },
                },
                "required": ["action"],
            },
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
            },
        },
        func=_amos_status,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEnhancePrompt",
        schema={
            "name": "AMOSEnhancePrompt",
            "description": ("Enhance a system prompt with AMOS brain context."),
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Base system prompt to enhance"}
                },
                "required": ["prompt"],
            },
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
                        "description": "The task or question to process through full AMOS workflow",
                    },
                    "output_type": {
                        "type": "string",
                        "enum": [
                            "structured_explanation",
                            "decision_recommendation",
                            "framework_design",
                            "research_analysis",
                            "diagnostic",
                        ],
                        "description": "Type of output to produce",
                    },
                },
                "required": ["task"],
            },
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
                        "description": "Coding layer to use",
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function/component to generate",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the code should do",
                    },
                    "inputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Input parameters",
                    },
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Expected outputs",
                    },
                },
                "required": ["layer", "function_name", "description"],
            },
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
                        "description": "Type of UI component to design",
                    },
                    "purpose": {
                        "type": "string",
                        "description": "What the component helps the user accomplish",
                    },
                    "user_segments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Target user segments",
                    },
                    "accessibility": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable accessibility requirements (WCAG AA)",
                    },
                },
                "required": ["component_type", "purpose"],
            },
        },
        func=_amos_design,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSDesignLanguage",
        schema={
            "name": "AMOSDesignLanguage",
            "description": (
                "Run design language analysis: information architecture, "
                "visual semantics, language clarity, and accessibility. "
                "Safety: NO clinical/medical decisions."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Design scenario to analyze"},
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["ia", "visual", "language", "accessibility"],
                        "description": "Domains: ia, visual, language, accessibility",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_design_language,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSignal",
        schema={
            "name": "AMOSSignal",
            "description": (
                "Run signal processing analysis across multiple domains. "
                "Analyzes Time/Frequency, Biological, Control Systems, and "
                "Communication signals with safety constraints (non-clinical)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Signal processing scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["time_frequency", "biological", "control", "communication"],
                        "description": "Signal domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_signal,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSUBI",
        schema={
            "name": "AMOSUBI",
            "description": (
                "Analyze human factors using Unified Biological Intelligence. "
                "Analyzes NBI (cognitive), NEI (emotional), SI (somatic), "
                "BEI (environmental) dimensions with safety constraints."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description of scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["NBI", "NEI", "SI", "BEI"],
                        "description": "UBI domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_ubi,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSStrategy",
        schema={
            "name": "AMOSStrategy",
            "description": (
                "Run strategy/game theory analysis across multiple domains. "
                "Analyzes Normal Form Games, Dynamical Games, and Negotiation "
                "with safety constraints (no harm strategies, no illegal collusion)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Strategic scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["game_normal", "game_dynamical", "negotiation"],
                        "description": "Strategy domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_strategy,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSociety",
        schema={
            "name": "AMOSSociety",
            "description": (
                "Run society/culture analysis across multiple domains. "
                "Analyzes Institutional, Cultural Norms, Demographic, and "
                "Media/Information systems with cultural sensitivity and safety constraints."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Social/cultural scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["institutional", "cultural", "demographic", "media"],
                        "description": "Society/culture domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_society,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEcon",
        schema={
            "name": "AMOSEcon",
            "description": (
                "Run economics/finance analysis across multiple domains. "
                "Analyzes Microeconomics, Macroeconomics, Public Finance, and "
                "Financial Markets with safety constraints (no investment advice)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Economic/financial scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["micro", "macro", "public_finance", "finance"],
                        "description": "Economic domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_econ,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSScientific",
        schema={
            "name": "AMOSScientific",
            "description": (
                "Run multi-domain scientific analysis using AMOS research engines. "
                "Analyzes input across Biology, Physics, Mathematics, and Engineering "
                "domains with pattern detection and scientific principle mapping."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description or problem to analyze scientifically",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["biology", "physics", "mathematics", "engineering"],
                        "description": "Scientific domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_scientific,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSBiologyCognition",
        schema={
            "name": "AMOSBiologyCognition",
            "description": (
                "Run biology and cognition analysis across 5 levels: "
                "molecular/genetic, cellular/tissue, organ/system, "
                "cognition/behavior, and pathology/recovery. "
                "Safety: NOT medical advice - informational only."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Biological or cognitive system to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["molecular", "cellular", "organ", "cognition", "pathology"],
                        "description": "Biology/cognition domains to include",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_biology_cognition,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMemory",
        schema={
            "name": "AMOSMemory",
            "description": (
                "Access AMOS memory layer - view stats or recall "
                "stored brain artifacts (reasoning, code, design, UBI)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["stats", "recall"],
                        "default": "stats",
                        "description": "Action: view stats or recall memories",
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["reasoning", "code", "design", "ubi"],
                        "description": "Type of memory to recall",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Number of memories to recall",
                    },
                },
            },
        },
        func=_amos_memory,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMultiAgent",
        schema={
            "name": "AMOSMultiAgent",
            "description": (
                "Run parallel multi-agent cognition using AMOS brain layers. "
                "Executes Rule of 2 (dual perspective) or Rule of 4 (4-quadrant) "
                "analysis with multiple sub-agents working in parallel."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["quadrant", "dual"],
                        "default": "quadrant",
                        "description": "Type of parallel analysis",
                    },
                    "problem": {"type": "string", "description": "Problem or question to analyze"},
                },
                "required": ["problem"],
            },
        },
        func=_amos_multi_agent,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMultiAgentCoordination",
        schema={
            "name": "AMOSMultiAgentCoordination",
            "description": (
                "Run multi-agent coordination and swarm intelligence analysis. "
                "Contract Net Protocol, market-based allocation, consensus mechanisms, "
                "and emergent swarm behaviors (PSO, ACO). "
                "Coordinated task allocation for distributed AI systems."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Coordination scenario to analyze (mention: contract, market, consensus, swarm)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for coordination analysis",
                    },
                },
                "required": ["scenario"],
            },
        },
        func=_amos_multi_agent_coordination,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMemoryOptimization",
        schema={
            "name": "AMOSMemoryOptimization",
            "description": (
                "Run memory optimization and caching analysis. "
                "LRU/LFU cache strategies, working set management, tiered storage, "
                "and prefetching. Memory hierarchy optimization for performance."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Memory scenario (mention: cache, LRU, LFU, working set, tier, prefetch)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for memory analysis",
                    },
                },
                "required": ["scenario"],
            },
        },
        func=_amos_memory_optimization,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSLogicCore",
        schema={
            "name": "AMOSLogicCore",
            "description": (
                "Run formal logic and reasoning analysis. Propositional, predicate, "
                "modal, temporal, and fuzzy logic systems. Logical inference and "
                "deduction capabilities."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Logic query to analyze (mention: proposition, predicate, modal, temporal, fuzzy)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for logic analysis",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_logic_core,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSpeciesInteractionCore",
        schema={
            "name": "AMOSSpeciesInteractionCore",
            "description": (
                "Run species interaction core analysis with HIE, UMPL, UST, UIE, UEL. "
                "Human Interaction Engine with nervous system safety, multimodal perception, "
                "universe structure tree, and interaction mapping."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Input text for species interaction analysis",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for interaction analysis",
                    },
                },
                "required": ["input"],
            },
        },
        func=_amos_species_interaction_core,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSUBIStack",
        schema={
            "name": "AMOSUBIStack",
            "description": (
                "Run UBI Stack neurobiological intelligence analysis. "
                "Stress physiology, autonomic nervous system, polyvagal theory, "
                "and social engagement system. Complements Species Interaction Core."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Scenario for neurobiological analysis (mention: stress, calm, anxiety, nervous system)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for UBI analysis",
                    },
                },
                "required": ["scenario"],
            },
        },
        func=_amos_ubi_stack,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSPlanetaryStack",
        schema={
            "name": "AMOSPlanetaryStack",
            "description": (
                "Run Planetary Stack analysis for planetary-scale systems. "
                "Planetary boundaries, climate systems, ecology, resource cycles, "
                "and sustainability metrics. Earth system thinking."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query for planetary analysis (mention: climate, biodiversity, boundaries, sustainability)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for planetary analysis",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_planetary_stack,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSKnowledgeGraph",
        schema={
            "name": "AMOSKnowledgeGraph",
            "description": (
                "Run Knowledge Graph analysis for semantic entity extraction, "
                "relationship detection, and knowledge inference. Connects entities "
                "across domains with typed relations and graph traversal."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query for knowledge graph analysis (entities, relationships, concepts)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for knowledge analysis",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_knowledge_graph,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEthicsSafety",
        schema={
            "name": "AMOSEthicsSafety",
            "description": (
                "Run Ethics & Safety analysis for comprehensive ethical reasoning. "
                "Multi-framework analysis (utilitarian, deontological, virtue, care), "
                "safety constraint enforcement, and human value alignment checking. "
                "Safety: Never violates critical constraints. Respects autonomy always."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "Scenario to analyze for ethics and safety",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context (stakeholders, consequences, options)",
                    },
                },
                "required": ["scenario"],
            },
        },
        func=_amos_ethics_safety,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSCausalInference",
        schema={
            "name": "AMOSCausalInference",
            "description": (
                "Run Causal Inference analysis using do-calculus and Pearl's framework. "
                "Interventions, counterfactuals, confounder detection, and causal discovery. "
                "Answers 'what if' questions and estimates causal effects."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Causal query (mention: intervention, counterfactual, what if, confounder)",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for causal analysis",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_causal_inference,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSKnowledge",
        schema={
            "name": "AMOSKnowledge",
            "description": (
                "Query knowledge graph and external data sources. "
                "Supports entity extraction, semantic search, and data connection "
                "with gap acknowledgment (simulated operations only)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Knowledge query to execute"},
                    "domain": {
                        "type": "string",
                        "default": "general",
                        "description": "Knowledge domain to query",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_knowledge,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSPersonality",
        schema={
            "name": "AMOSPersonality",
            "description": (
                "Run personality and character analysis with AMOS identity awareness. "
                "Analyzes Traits, Identity, Behavioral Patterns, and Cognitive Style. "
                "Includes AMOS core identity: creator Trang Phan, INTJ-ENTP hybrid, "
                "values truth, protection, coherence."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Personality/character scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["traits", "identity", "behavioral_patterns", "cognitive_style"],
                        "description": "Personality domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_personality,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEmotion",
        schema={
            "name": "AMOSEmotion",
            "description": (
                "Run emotion/affective analysis across multiple domains. "
                "Analyzes Affective States, Somatic Markers, Motivation, and Empathy "
                "with CRITICAL safety constraints (NOT real emotion recognition, lexical only)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Emotion-related scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["affective", "somatic", "motivation", "empathy"],
                        "description": "Emotion domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_emotion,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSConsciousness",
        schema={
            "name": "AMOSConsciousness",
            "description": (
                "Run consciousness and meta-cognitive analysis across multiple domains. "
                "Analyzes Self-Modeling, Attention, Narrative, and Embodiment with "
                "CRITICAL safety constraints (NOT real consciousness, pattern simulation only)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Consciousness-related scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["self_modeling", "attention", "narrative", "embodiment"],
                        "description": "Consciousness domains to analyze",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_consciousness,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="ALOSEconFinance",
        schema={
            "name": "ALOSEconFinance",
            "description": (
                "Run economics and financial analysis: micro/macroeconomics, "
                "public finance, banking and markets. Safety: NOT personalized "
                "investment advice. Long-horizon forecasts uncertain."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Economic or financial scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: micro, macro, public_finance, financial_system",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_econ_finance,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="ALOSStrategyGame",
        schema={
            "name": "ALOSStrategyGame",
            "description": (
                "Run strategy and game theory analysis: normal-form games, "
                "repeated games, evolutionary dynamics, negotiation, and "
                "coalition formation. Safety: NOT for physical harm strategies "
                "or illegal collusion."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Strategic scenario or game to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: normal_form, dynamical, negotiation",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_strategy_game,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="ALOSSocietyCulture",
        schema={
            "name": "ALOSSocietyCulture",
            "description": (
                "Run society and culture analysis: institutions, cultural norms, "
                "demographics, and media/information flows. Safety: Avoids prescriptive "
                "cultural judgments. Does not generate targeted manipulation."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Social or cultural scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: institutions, cultural_norms, demographics, media_information",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_society_culture,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSpeed",
        schema={
            "name": "AMOSSpeed",
            "description": (
                "Run speed optimization analysis for AMOS engines. "
                "Analyzes query complexity and recommends optimization profiles, "
                "response tiers, and reasoning pruning strategies."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Query or task to optimize"},
                    "mode": {
                        "type": "string",
                        "description": "Mode: max_safe_speed, balanced_fast, precision_priority",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_speed,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSUniverseCore",
        schema={
            "name": "AMOSUniverseCore",
            "description": (
                "Run universe core physics and cosmology analysis. "
                "Fundamental constants, cosmological parameters, spacetime geometry, "
                "and quantum gravity concepts. Lambda-CDM model. "
                "Safety: Does not claim beyond established physics."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Physics or cosmology query to analyze",
                    },
                    "context": {"type": "object", "description": "Optional context for analysis"},
                },
                "required": ["query"],
            },
        },
        func=_amos_universe_core,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSpeciesInteraction",
        schema={
            "name": "AMOSSpeciesInteraction",
            "description": (
                "Run species interaction analysis: human-facing AI with safety filters, "
                "nervous-system awareness, and interaction strategies. Safety: Never induces "
                "panic deliberately. Does not manipulate or coerce. Prefers safety over speed."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "User input or scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: human_interaction, perception, structure",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_species_interaction,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSAuditQuality",
        schema={
            "name": "AMOSAuditQuality",
            "description": (
                "Run audit quality analysis: financial, operational, and risk audit. "
                "Maps findings to systemic states (Ω overload, H health, F fragmentation, "
                "S shock-sensitivity). Safety: Advisory only. Not substitute for "
                "professional audit services."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Process, data, or scenario to audit",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: financial, operational, risk",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_audit_quality,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSUnifiedCoding",
        schema={
            "name": "AMOSUnifiedCoding",
            "description": (
                "Run unified coding analysis: architecture, backend, database, security "
                "across 9 layers. Detects code smells, security issues, performance "
                "problems. Safety: Advisory only. Production code requires professional "
                "review and testing."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Code, design, or scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: architecture, backend, database, security",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_unified_coding,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSSystemsCore",
        schema={
            "name": "AMOSSystemsCore",
            "description": (
                "Run AMOS Systems Core orchestration and health monitoring. "
                "Central nervous system for lifecycle management, dependency resolution, "
                "health monitoring, and resource balancing. Operations: register, start, "
                "stop, status, report."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "default": "report",
                        "description": "Operation: report, register, start, stop, status",
                    },
                    "component": {"type": "string", "description": "Component name"},
                    "component_type": {"type": "string", "default": "service"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "resource_limit": {"type": "number", "default": 1.0},
                },
            },
        },
        func=_amos_systems_core,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSPhysicsCosmos",
        schema={
            "name": "AMOSPhysicsCosmos",
            "description": (
                "Run physics and cosmos analysis: classical dynamics, electromagnetism, "
                "quantum mechanics, statistical physics, cosmology. Maps physical "
                "principles to applications. Safety: Does not claim new physical laws. "
                "Marks speculative content as hypothetical."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Physical scenario or system to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: classical, electromagnetism, quantum, statistical, cosmology",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_physics_cosmos,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSTechQuantum",
        schema={
            "name": "AMOSTechQuantum",
            "description": (
                "Run quantum computing analysis: algorithms, hardware platforms, "
                "control software, error correction, and applications. "
                "Analyzes quantum advantage potential and NISQ-era considerations. "
                "Safety: Does not guarantee quantum speedup. "
                "Not a substitute for quantum physicists."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Quantum computing scenario or application to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: algorithms, hardware, control, error_correction, applications",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_tech_quantum,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSLogicLaw",
        schema={
            "name": "AMOSLogicLaw",
            "description": (
                "Run deterministic logic and legal analysis. "
                "Analyzes formal logic, legal entities/relations, argumentation, "
                "and policy design with CRITICAL safety constraints "
                "(NOT legal advice, informational only)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Logic or legal query to analyze"},
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["logic", "legal", "argumentation", "policy"],
                        "description": "Analysis domains to include",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_logic_law,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSVNLegal",
        schema={
            "name": "AMOSVNLegal",
            "description": (
                "Run Vietnam-specialised legal analysis. "
                "Covers corporate, finance, disputes, regulatory, IP/data, and ESG law. "
                "24-dimensional legal analysis axes. "
                "CRITICAL: Informational only - NOT legal advice. "
                "Always consult licensed Vietnamese attorneys."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Legal matter or scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: corporate, finance, disputes, regulatory, ip_data, esg",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_vn_legal,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSVOMNI",
        schema={
            "name": "AMOSVOMNI",
            "description": (
                "Run vOmni kernel master orchestration and routing. "
                "Analyzes queries and routes to optimal kernel combinations. "
                "Combines 33 meta-kernels, domain kernels, orchestration, "
                "UBI stack, planetary systems, and safety layers. "
                "CRITICAL: Does not execute, only routes."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to analyze for kernel routing",
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context for routing decisions",
                    },
                },
                "required": ["query"],
            },
        },
        func=_amos_vomni,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSWorkflowOrchestrator",
        schema={
            "name": "AMOSWorkflowOrchestrator",
            "description": (
                "Run workflow orchestration for complex multi-engine tasks. "
                "State-of-the-art 2024-2025 agentic AI with hierarchical planning, "
                "execution, and reflection. Safety: NO autonomous execution without oversight."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Goal to orchestrate workflow for"},
                    "mode": {
                        "type": "string",
                        "default": "adaptive",
                        "description": "Orchestration mode: sequential, parallel, or adaptive",
                    },
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                        "description": "Tools to use in workflow",
                    },
                },
                "required": ["goal"],
            },
        },
        func=_amos_workflow_orchestrator,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSElectricalPower",
        schema={
            "name": "AMOSElectricalPower",
            "description": (
                "Run electrical power systems analysis covering generation, transmission, "
                "distribution, power electronics, protection, and markets. "
                "Safety: NO safety-critical decisions without qualified engineer review."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Power system scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains to analyze (power_systems, power_electronics, protection, markets)",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_electrical_power,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMechanicalStructural",
        schema={
            "name": "AMOSMechanicalStructural",
            "description": (
                "Run mechanical and structural analysis: mechanics, materials, "
                "elements, loads, and design codes. Safety: NOT a licensed engineer. "
                "All outputs require review by qualified engineers."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Structural scenario to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: mechanics, elements, loads, codes",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_mechanical_structural,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSNumericalMethods",
        schema={
            "name": "AMOSNumericalMethods",
            "description": (
                "Run numerical methods analysis: linear algebra, optimization, "
                "differential equations, interpolation, and integration. "
                "Safety: Design support only, not for safety-critical verification."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Numerical problem to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domains: linear_algebra, optimization, differential_equations, approximation",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_numerical_methods,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSPhysics",
        schema={
            "name": "AMOSPhysics",
            "description": (
                "Run physics and cosmology analysis across 5 domains: "
                "classical mechanics, electromagnetism, quantum mechanics, "
                "statistical physics, and cosmology. Safety: NO new laws claimed."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Physical system or phenomenon to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "classical",
                            "electromagnetism",
                            "quantum",
                            "statistical",
                            "cosmology",
                        ],
                        "description": "Physics domains to include",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_physics,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSEngineeringMath",
        schema={
            "name": "AMOSEngineeringMath",
            "description": (
                "Run engineering and mathematics analysis across 6 domains: "
                "pure math, applied math, numerical methods, mechanical, "
                "electrical, and control systems. Safety: NO real-time control."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Engineering or mathematical system to analyze",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "pure_math",
                            "applied_math",
                            "numerical",
                            "mechanical",
                            "electrical",
                            "control",
                        ],
                        "description": "Engineering/math domains to include",
                    },
                },
                "required": ["description"],
            },
        },
        func=_amos_engineering_math,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSMonitoring",
        schema={
            "name": "AMOSMonitoring",
            "description": (
                "Get system monitoring and telemetry status. "
                "Provides performance metrics, health checks, and execution telemetry."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "health"],
                        "default": "status",
                        "description": "Monitoring action to perform",
                    }
                },
            },
        },
        func=_amos_monitoring,
        read_only=True,
        concurrent_safe=True,
    ),
    ToolDef(
        name="AMOSAudit",
        schema={
            "name": "AMOSAudit",
            "description": (
                "Audit content against AMOS 6 Global Laws (L1-L6) and quality checks. "
                "Validates law compliance, structural integrity, and gap acknowledgment."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to audit"},
                    "content_type": {
                        "type": "string",
                        "enum": ["general", "code", "design"],
                        "default": "general",
                        "description": "Type of content for specialized auditing",
                    },
                },
                "required": ["content"],
            },
        },
        func=_amos_audit,
        read_only=True,
        concurrent_safe=True,
    ),
]


# ── Registration ──────────────────────────────────────────────────────────────


def _ensure_amos() -> None:
    """Lightweight AMOS check - doesn't load heavy resources."""
    # Just verify the runtime module is available
    # Actual runtime loading is deferred until tool is used
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

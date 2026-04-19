"""AMOS Agent Bridge
=================
Integrates AMOS Cognitive Runtime with the clawspring agent system.
Provides tools for the agent to leverage AMOS brain capabilities.
"""

from __future__ import annotations



import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the repo root to path for imports
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


from amos_cognitive_runtime import AMOSCognitiveRuntime


class AMOSAgentBridge:
    """Bridge between AMOS Cognitive Runtime and agent tools.
    Provides a clean API for agent integration.
    """

    _instance: Optional[AMOSAgentBridge] = None
    _runtime: Optional[AMOSCognitiveRuntime] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._runtime is None:
            brain_dir = REPO_ROOT / "_AMOS_BRAIN"
            self._runtime = AMOSCognitiveRuntime(brain_dir)

    @property
    def runtime(self) -> AMOSCognitiveRuntime:
        """Access the underlying AMOS runtime."""
        return self._runtime

    def think(self, question: str, mode: str = "exploratory_mapping") -> Dict[str, Any]:
        """Process a question through AMOS cognitive layers.

        Args:
            question: The question or task to analyze
            mode: Reasoning mode (exploratory_mapping, diagnostic_analysis,
                  design_and_architecture, audit_and_critique, measurement_and_scoring)

        Returns:
            Structured analysis with explanation and metadata
        """
        return self._runtime.think(question, mode)

    def analyze_task(self, task_description: str, context: dict = None) -> Dict[str, Any]:
        """Analyze a coding/design task using AMOS cognitive architecture.

        Args:
            task_description: Description of the task
            context: Additional context (files, requirements, constraints)

        Returns:
            Analysis with recommendations and structured breakdown
        """
        # Combine task with context for comprehensive analysis
        full_question = task_description
        if context:
            context_str = json.dumps(context, indent=2)
            full_question += f"\n\nContext:\n{context_str}"

        result = self._runtime.think(full_question, "diagnostic_analysis")

        # Add task-specific processing
        synthesis = result["synthesis"]

        # Extract recommendations for developers
        dev_recommendations = []
        if synthesis["problem_structure"]["domain"] == "engineering":
            dev_recommendations.append("Consider system boundaries and interfaces")
            dev_recommendations.append("Check for structural integrity constraints")

        if synthesis["problem_structure"]["domain"] == "economics":
            dev_recommendations.append("Evaluate resource allocation patterns")
            dev_recommendations.append("Consider incentive structures")

        result["developer_recommendations"] = dev_recommendations
        return result

    def design_architecture(
        self, requirements: str, constraints: List[str] = None
    ) -> Dict[str, Any]:
        """Generate architecture design using AMOS design engine principles.

        Args:
            requirements: System requirements
            constraints: List of constraints to respect

        Returns:
            Architecture design with AMOS quality checks
        """
        question = f"Design architecture for: {requirements}"
        if constraints:
            question += f"\n\nConstraints: {', '.join(constraints)}"

        result = self._runtime.think(question, "design_and_architecture")

        # Add architecture-specific validation
        synthesis = result["synthesis"]

        # Check UBI alignment for system design
        ubi_check = self._runtime.biological.apply_ubi_alignment(requirements)
        result["ubi_alignment"] = ubi_check

        # Add structural recommendations
        arch_recommendations = [
            "Ensure clear interfaces between components",
            "Design for biological constraints (attention, cognitive load)",
            "Include audit points for traceability",
        ]

        if not ubi_check["aligned"]:
            arch_recommendations.append("Review design for UBI alignment - may impact human users")

        result["architecture_recommendations"] = arch_recommendations
        return result

    def audit_decision(self, decision: str, rationale: str) -> Dict[str, Any]:
        """Audit a decision against AMOS global laws and constraints.

        Args:
            decision: The decision made
            rationale: The reasoning behind it

        Returns:
            Audit report with law compliance and recommendations
        """
        full_text = f"Decision: {decision}\n\nRationale: {rationale}"
        result = self._runtime.think(full_text, "audit_and_critique")

        # Add specific law compliance checks
        meta = self._runtime.meta_logic

        # Check Rule of 2 (dual perspective)
        rule2_check = meta.check_rule_of_2(decision, ["alternative approach", "opposing view"])

        # Check structural integrity
        integrity = meta.validate_structural_integrity(rationale)

        result["law_compliance"] = {
            "rule_of_2": rule2_check["compliant"],
            "structural_integrity": all(integrity.values()),
            "total_violations": len(meta.violations),
        }

        return result

    def get_engine_info(self, engine_name: str) -> dict:
        """Get information about a specific cognitive engine."""
        return self._runtime.get_engine_info(engine_name)

    def list_engines(self) -> List[str]:
        """List all available cognitive engines."""
        return self._runtime.list_available_engines()

    def get_status(self) -> Dict[str, Any]:
        """Get AMOS runtime status."""
        return self._runtime.get_status()


# Tool functions for integration with clawspring


def amos_think(question: str, mode: str = "exploratory_mapping") -> str:
    """Tool: Think through a question using AMOS cognitive architecture.

    Args:
        question: The question or problem to analyze
        mode: Reasoning mode (exploratory_mapping, diagnostic_analysis,
              design_and_architecture, audit_and_critique, measurement_and_scoring)

    Returns:
        Structured analysis and recommendations
    """
    bridge = AMOSAgentBridge()
    result = bridge.think(question, mode)

    output = [
        result["explanation"],
        "",
        "## Runtime State",
        f"- Engines loaded: {result['runtime_state']['loaded_engines']}",
        f"- Working memory: {result['runtime_state']['working_memory']['used']}/"
        f"{result['runtime_state']['working_memory']['capacity']}",
        f"- Law compliance: {'✓' if result['runtime_state']['law_compliance']['compliant'] else '✗'}",
    ]

    return "\n".join(output)


def amos_analyze_task(task: str, context_json: str = "{}") -> str:
    """Tool: Analyze a development task using AMOS cognitive layers.

    Args:
        task: Task description
        context_json: JSON string with context (files, requirements, etc.)

    Returns:
        Analysis with developer-focused recommendations
    """
    bridge = AMOSAgentBridge()

    try:
        context = json.loads(context_json) if context_json else {}
    except json.JSONDecodeError:
        context = {"raw_context": context_json}

    result = bridge.analyze_task(task, context)

    output = [
        result["explanation"],
        "",
        "## Developer Recommendations",
    ]

    for rec in result.get("developer_recommendations", []):
        output.append(f"- {rec}")

    output.extend(
        [
            "",
            "## Quality Check",
            f"Meta-logic compliant: {'✓' if result['synthesis']['meta_logic_compliant'] else '✗'}",
            f"Biological constraints: {'✓' if result['synthesis']['biological_constraints_met'] else '✗'}",
        ]
    )

    return "\n".join(output)


def amos_design_architecture(requirements: str, constraints: str = "") -> str:
    """Tool: Generate architecture design with AMOS principles.

    Args:
        requirements: System requirements
        constraints: Comma-separated list of constraints

    Returns:
        Architecture design with quality checks
    """
    bridge = AMOSAgentBridge()

    constraint_list = [c.strip() for c in constraints.split(",")] if constraints else []
    result = bridge.design_architecture(requirements, constraint_list)

    output = [
        result["explanation"],
        "",
        "## Architecture Recommendations",
    ]

    for rec in result.get("architecture_recommendations", []):
        output.append(f"- {rec}")

    ubi = result.get("ubi_alignment", {})
    output.extend(
        [
            "",
            "## UBI Alignment",
            f"Aligned: {'✓' if ubi.get('aligned') else '✗'}",
            f"Score: {ubi.get('ubi_score', 0):.2f}",
        ]
    )

    return "\n".join(output)


def amos_audit_decision(decision: str, rationale: str) -> str:
    """Tool: Audit a decision against AMOS global laws.

    Args:
        decision: The decision to audit
        rationale: The reasoning behind it

    Returns:
        Audit report with law compliance status
    """
    bridge = AMOSAgentBridge()
    result = bridge.audit_decision(decision, rationale)

    compliance = result.get("law_compliance", {})

    output = [
        result["explanation"],
        "",
        "## Law Compliance Check",
        f"Rule of 2 (dual perspective): {'✓' if compliance.get('rule_of_2') else '✗'}",
        f"Structural integrity: {'✓' if compliance.get('structural_integrity') else '✗'}",
        f"Total violations: {compliance.get('total_violations', 0)}",
    ]

    return "\n".join(output)


def amos_list_engines() -> str:
    """Tool: List all available AMOS cognitive engines.

    Returns:
        List of loaded engines
    """
    bridge = AMOSAgentBridge()
    engines = bridge.list_engines()

    output = ["## AMOS Cognitive Engines Loaded", ""]

    for engine in sorted(engines):
        output.append(f"- {engine}")

    output.append(f"\nTotal: {len(engines)} engines")
    return "\n".join(output)


def amos_status() -> str:
    """Tool: Get AMOS runtime status.

    Returns:
        Runtime status summary
    """
    bridge = AMOSAgentBridge()
    status = bridge.get_status()

    return json.dumps(status, indent=2)


# Export for clawspring tool integration
AMOS_TOOLS = {
    "amos_think": amos_think,
    "amos_analyze_task": amos_analyze_task,
    "amos_design_architecture": amos_design_architecture,
    "amos_audit_decision": amos_audit_decision,
    "amos_list_engines": amos_list_engines,
    "amos_status": amos_status,
}


if __name__ == "__main__":
    # Test the bridge
    print("Testing AMOS Agent Bridge...")
    print()

    # Test 1: Basic thinking
    print("=" * 60)
    print("Test 1: Basic Think")
    print("=" * 60)
    result = amos_think(
        "How do we ensure AI systems remain aligned with human values?", "exploratory_mapping"
    )
    print(result[:500] + "...\n")

    # Test 2: List engines
    print("=" * 60)
    print("Test 2: List Engines")
    print("=" * 60)
    print(amos_list_engines())

    # Test 3: Status
    print("=" * 60)
    print("Test 3: Status")
    print("=" * 60)
    print(amos_status())

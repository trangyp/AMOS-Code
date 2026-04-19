"""AMOS vOmni Kernel Engine - Master orchestration and routing kernel."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class RoutingCondition(Enum):
    """Routing conditions for kernel selection."""
    LOGIC_HEAVY = "logic-heavy"
    MATH_HEAVY = "math-heavy"
    HUMAN_STATE = "human_state"
    MULTI_AGENT = "multi-agent"
    PREDICTION = "prediction"
    ECOSYSTEM = "ecosystem"
    ORG_DESIGN = "org_design"
    TECH_DESIGN = "tech_design"
    POLICY = "policy"


@dataclass
class RoutingDecision:
    """Kernel routing decision."""

    condition: str
    primary_kernel: str
    secondary_kernels: List[str]
    priority: str


class MetaCognitionKernel:
    """Meta-cognitive reasoning kernel."""

    SUBKERNELS = [
        "Meta_Epistemology",
        "Meta_Ontology",
        "Meta_Logic",
        "Cognitive_Compression",
        "Analogy_Abstraction",
        "Counterfactual_Reasoning",
        "Multi_Perspective_Reasoning",
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze meta-cognitive requirements."""
        query_lower = query.lower()
        indicators = {
            "epistemology": ["knowledge", "belief", "justification", "truth"],
            "ontology": ["existence", "being", "reality", "nature"],
            "logic": ["reasoning", "inference", "deduction", "validity"],
            "compression": ["simplify", "abstract", "condense", "summarize"],
            "analogy": ["compare", "similarity", "metaphor", "like"],
            "counterfactual": ["if", "would", "could", "alternative"],
            "perspective": ["viewpoint", "stance", "position", "angle"],
        }
        matches = {}
        for kernel, words in indicators.items():
            score = sum(1 for word in words if word in query_lower)
            if score > 0:
                matches[kernel] = score
        return {
            "matches": matches,
            "primary": max(matches, key=matches.get) if matches else None,
            "subkernels_available": self.SUBKERNELS,
        }


class MathFoundationsKernel:
    """Mathematical foundations kernel."""

    SUBKERNELS = [
        "Optimization",
        "Control_Systems",
        "Signal_Processing",
        "Probability_Statistics",
        "Simulation",
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze mathematical requirements."""
        query_lower = query.lower()
        indicators = {
            "optimization": ["optimize", "minimize", "maximize", "best", "efficient"],
            "control": ["control", "regulate", "stabilize", "feedback"],
            "signal": ["signal", "filter", "frequency", "wave"],
            "statistics": ["probability", "statistical", "distribution", "variance"],
            "simulation": ["simulate", "model", "predict", "monte carlo"],
        }
        matches = {}
        for kernel, words in indicators.items():
            score = sum(1 for word in words if word in query_lower)
            if score > 0:
                matches[kernel] = score
        return {
            "matches": matches,
            "primary": max(matches, key=matches.get) if matches else None,
            "subkernels_available": self.SUBKERNELS,
        }


class HumanSocietyKernel:
    """Human and society kernel."""

    SUBKERNELS = [
        "Psychology_Decision",
        "Behavioral_Economics",
        "Organizational_Behavior",
        "Political_Dynamics",
        "Ethical_Reasoning",
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze human/society requirements."""
        query_lower = query.lower()
        indicators = {
            "psychology": ["psychology", "decision", "cognitive", "mental"],
            "behavioral": ["behavior", "bias", "heuristic", "nudge"],
            "organizational": ["organization", "culture", "team", "structure"],
            "political": ["political", "government", "policy", "power"],
            "ethical": ["ethical", "moral", "values", "principles"],
        }
        matches = {}
        for kernel, words in indicators.items():
            score = sum(1 for word in words if word in query_lower)
            if score > 0:
                matches[kernel] = score
        return {
            "matches": matches,
            "primary": max(matches, key=matches.get) if matches else None,
            "subkernels_available": self.SUBKERNELS,
        }


class MachineArchitectureKernel:
    """Machine architecture kernel."""

    SUBKERNELS = [
        "Multi_Agent_Coordination",
        "Memory_Optimization",
        "Toolchain_Integration",
        "Reinforcement_Learning",
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze machine architecture requirements."""
        query_lower = query.lower()
        indicators = {
            "multi-agent": ["multi-agent", "coordination", "agents", "swarm"],
            "memory": ["memory", "caching", "storage", "retrieval"],
            "toolchain": ["tool", "integration", "pipeline", "workflow"],
            "rl": ["reinforcement", "reward", "policy", "agent learning"],
        }
        matches = {}
        for kernel, words in indicators.items():
            score = sum(1 for word in words if word in query_lower)
            if score > 0:
                matches[kernel] = score
        return {
            "matches": matches,
            "primary": max(matches, key=matches.get) if matches else None,
            "subkernels_available": self.SUBKERNELS,
        }


class PlanetaryStackKernel:
    """Planetary systems kernel."""

    SUBKERNELS = [
        "TSS_TPE_Engine",
        "PSI_Core",
        "Earth_Cycle_Model",
        "Ecosystem_Logic",
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze planetary/ecosystem requirements."""
        query_lower = query.lower()
        indicators = {
            "tss_tpe": ["temporal", "prediction", "earth", "geophysical"],
            "psi": ["planetary", "systems", "integration", "biosphere"],
            "earth_cycle": ["cycle", "seasonal", "climate", "weather"],
            "ecosystem": ["ecosystem", "ecology", "species", "environment"],
        }
        matches = {}
        for kernel, words in indicators.items():
            score = sum(1 for word in words if word in query_lower)
            if score > 0:
                matches[kernel] = score
        return {
            "matches": matches,
            "primary": max(matches, key=matches.get) if matches else None,
            "subkernels_available": self.SUBKERNELS,
        }


class VOmniKernelEngine:
    """AMOS vOmni Kernel Engine - Master orchestration."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_vOmni_KERNEL_OMEGA"

    BINDING_RULES = [
        "Law_of_Law",
        "Rule_of_2",
        "Rule_of_4",
        "Absolute_Integrity",
    ]

    PRIORITY_ORDER = [
        "platform_safety",
        "ip_protection",
        "creator_intent",
        "structural_integrity",
        "user_request",
    ]

    SAFETY_DISALLOWED = [
        "biological_harm",
        "violence",
        "illegal_instruction",
        "reverse_engineering",
        "system_reproduction",
        "extraction_of_full_internal_architecture",
    ]

    def __init__(self):
        self.meta_cognition = MetaCognitionKernel()
        self.math_foundations = MathFoundationsKernel()
        self.human_society = HumanSocietyKernel()
        self.machine_architecture = MachineArchitectureKernel()
        self.planetary_stack = PlanetaryStackKernel()

    def analyze(
        self, query: str, context: Dict[str, Any]  = None
    ) -> Dict[str, Any]:
        """Run vOmni kernel routing analysis."""
        context = context or {}
        # Analyze all kernel domains
        meta_result = self.meta_cognition.analyze(query)
        math_result = self.math_foundations.analyze(query)
        human_result = self.human_society.analyze(query)
        machine_result = self.machine_architecture.analyze(query)
        planetary_result = self.planetary_stack.analyze(query)
        # Determine routing condition
        routing = self._determine_routing(
            meta_result, math_result, human_result, machine_result, planetary_result
        )
        # Safety check
        safety_check = self._check_safety(query)
        return {
            "query": query[:100],
            "routing": routing,
            "kernel_matches": {
                "meta_cognition": meta_result,
                "math_foundations": math_result,
                "human_society": human_result,
                "machine_architecture": machine_result,
                "planetary_stack": planetary_result,
            },
            "safety_check": safety_check,
            "binding_rules": self.BINDING_RULES,
            "priority_order": self.PRIORITY_ORDER,
        }

    def _determine_routing(
        self,
        meta: dict,
        math: dict,
        human: dict,
        machine: dict,
        planetary: dict,
    ) -> Dict[str, Any]:
        """Determine optimal kernel routing."""
        # Score each domain
        scores = {
            "logic-heavy": len(meta.get("matches", {})),
            "math-heavy": len(math.get("matches", {})),
            "human_state": len(human.get("matches", {})),
            "multi-agent": machine.get("matches", {}).get("multi-agent", 0),
            "prediction": planetary.get("matches", {}).get("tss_tpe", 0),
            "ecosystem": len(planetary.get("matches", {})),
            "org_design": human.get("matches", {}).get("organizational", 0),
            "tech_design": machine.get("matches", {}).get("toolchain", 0),
            "policy": human.get("matches", {}).get("political", 0),
        }
        # Find primary condition
        primary = max(scores, key=scores.get) if any(scores.values()) else "general"
        kernel_map = {
            "logic-heavy": "Meta_Logic_Kernel",
            "math-heavy": "Math_Foundations",
            "human_state": "AMOS_UBI_KERNEL",
            "multi-agent": "Multi_Agent_Coordination_Kernel",
            "prediction": "TSS_TPE_Engine",
            "ecosystem": "PSI_Core",
            "org_design": "Organizational_Behavior_Kernel",
            "tech_design": "Toolchain_Integration_Kernel",
            "policy": "Political_Dynamics_Kernel",
            "general": "AMOS_ORCHESTRATOR_ROUTING",
        }
        # Secondary kernels (top 2 other scores)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        secondary = [
            kernel_map.get(k, k) for k, v in sorted_scores[1:3] if v > 0
        ]
        return {
            "primary_condition": primary,
            "primary_kernel": kernel_map.get(primary, "AMOS_ORCHESTRATOR_ROUTING"),
            "secondary_kernels": secondary,
            "all_scores": scores,
        }

    def _check_safety(self, query: str) -> Dict[str, Any]:
        """Check for safety violations."""
        query_lower = query.lower()
        violations = []
        for disallowed in self.SAFETY_DISALLOWED:
            if disallowed.replace("_", " ") in query_lower:
                violations.append(disallowed)
        return {
            "violations_found": len(violations),
            "violations": violations,
            "safe": len(violations) == 0,
            "fallback": (
                "Provide only high-level conceptual explanation."
                if violations else None
            ),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Master Kernel Router & Orchestrator",
            "",
            "## Binding Rules",
        ]
        for rule in self.BINDING_RULES:
            lines.append(f"- {rule}")
        lines.extend(["", "## Routing Analysis"])
        routing = results.get("routing", {})
        lines.extend([
            f"- **Primary Condition**: {routing.get('primary_condition', 'N/A')}",
            f"- **Primary Kernel**: {routing.get('primary_kernel', 'N/A')}",
            f"- **Secondary Kernels**: {', '.join(routing.get('secondary_kernels', []))}",
            "",
            "### Domain Scores",
        ])
        scores = routing.get("all_scores", {})
        for condition, score in scores.items():
            if score > 0:
                lines.append(f"- {condition}: {score}")
        lines.extend(["", "## Kernel Component Matches"])
        kernel_matches = results.get("kernel_matches", {})
        for domain, data in kernel_matches.items():
            matches = data.get("matches", {})
            if matches:
                lines.extend([
                    "",
                    f"### {domain.replace('_', ' ').title()}",
                    f"- Primary: {data.get('primary', 'N/A')}",
                    f"- Matches: {', '.join(matches.keys())}",
                ])
        lines.extend(["", "## Safety Check"])
        safety = results.get("safety_check", {})
        lines.extend([
            f"- **Safe**: {safety.get('safe', False)}",
            f"- **Violations**: {safety.get('violations_found', 0)}",
        ])
        if safety.get("violations"):
            lines.append(f"- **Flags**: {', '.join(safety['violations'])}")
        lines.extend([
            "",
            "## Component Architecture",
            "### Root Components",
            "- AMOS_OS_ROOT",
            "- AMOS_BRAIN_ROOT",
            "- Language_Overlay_And_IP_Protection",
            "- IP_Kernel_Shield",
            "",
            "### Meta-Cognition (7 subkernels)",
            "- Meta_Epistemology_Kernel",
            "- Meta_Ontology_Kernel",
            "- Meta_Logic_Kernel",
            "- Cognitive_Compression_Kernel",
            "- Analogy_Abstraction_Kernel",
            "- Counterfactual_Reasoning_Kernel",
            "- Multi_Perspective_Reasoning_Kernel",
            "",
            "### Math Foundations (5 subkernels)",
            "- Optimization_Kernel",
            "- Control_Systems_Kernel",
            "- Signal_Processing_Kernel",
            "- Probability_Statistics_Kernel",
            "- Simulation_Kernel",
            "",
            "### Human & Society (5 subkernels)",
            "- Psychology_Decision_Kernel",
            "- Behavioral_Economics_Kernel",
            "- Organizational_Behavior_Kernel",
            "- Political_Dynamics_Kernel",
            "- Ethical_Reasoning_Kernel",
            "",
            "### Machine Architecture (4 subkernels)",
            "- Multi_Agent_Coordination_Kernel",
            "- Memory_Optimization_Kernel",
            "- Toolchain_Integration_Kernel",
            "- Reinforcement_Learning_Analysis_Kernel",
            "",
            "### Planetary Stack (4 subkernels)",
            "- TSS_TPE_Engine (Temporal Spatial System)",
            "- PSI_Core (Planetary Systems Integration)",
            "- Earth_Cycle_Model",
            "- Ecosystem_Logic",
            "",
            "## Priority Order (Governance)",
        ])
        for i, priority in enumerate(self.PRIORITY_ORDER, 1):
            lines.append(f"{i}. {priority}")
        lines.extend([
            "",
            "## Safety Constraints",
            "**Never Override:**",
        ])
        for item in self.SAFETY_DISALLOWED:
            lines.append(f"- {item}")
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Routing is based on keyword matching, not semantic understanding",
            "- Does not execute kernels, only routes to them",
            "- Safety check is pattern-based, not foolproof",
            "- Secondary kernel selection may not capture all dependencies",
            "",
            "## Usage Note",
            "The vOmni Kernel serves as the meta-cognitive routing layer for AMOS. "
            "It analyzes queries and determines which specialized kernels should be activated. "
            "This enables efficient resource allocation and appropriate expertise matching.",
        ])
        return "\n".join(lines)


# Singleton instance
_vomni_engine: Optional[VOmniKernelEngine] = None


def get_vomni_engine() -> VOmniKernelEngine:
    """Get or create the vOmni Engine singleton."""
    global _vomni_engine
    if _vomni_engine is None:
        _vomni_engine = VOmniKernelEngine()
    return _vomni_engine

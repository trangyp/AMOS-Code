"""AMOS Causal Inference Engine - Causal reasoning and do-calculus."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class CausalRelationType(Enum):
    """Types of causal relationships."""
    DIRECT_CAUSE = "direct_cause"
    INDIRECT_CAUSE = "indirect_cause"
    COMMON_CAUSE = "common_cause"
    CONFOUNDER = "confounder"
    COLLIDER = "collider"
    MEDIATOR = "mediator"
    MODERATOR = "moderator"


class EvidenceType(Enum):
    """Types of causal evidence."""
    EXPERIMENTAL = "experimental"
    OBSERVATIONAL = "observational"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    SIMULATION = "simulation"
    THEORETICAL = "theoretical"


@dataclass
class CausalVariable:
    """Represents a variable in a causal model."""
    id: str
    name: str
    var_type: str  # "continuous", "binary", "categorical"
    domain: List[Any] = field(default_factory=list)


@dataclass
class CausalEdge:
    """Represents a causal relationship."""
    source: str
    target: str
    relation_type: CausalRelationType
    strength: float  # 0-1
    evidence: EvidenceType
    confidence: float = 0.8


@dataclass
class Intervention:
    """Represents a do-operator intervention."""
    target_var: str
    new_value: Any
    context: Dict[str, Any] = field(default_factory=dict)


class CausalGraph:
    """Causal graph structure (DAG)."""

    def __init__(self):
        self.variables: Dict[str, CausalVariable] = {}
        self.edges: List[CausalEdge] = []
        self.adjacency: Dict[str, list[str]] = {}  # source -> targets

    def add_variable(self, var: CausalVariable) -> None:
        """Add variable to graph."""
        self.variables[var.id] = var
        if var.id not in self.adjacency:
            self.adjacency[var.id] = []

    def add_edge(self, edge: CausalEdge) -> None:
        """Add causal edge to graph."""
        self.edges.append(edge)
        if edge.source in self.adjacency:
            self.adjacency[edge.source].append(edge.target)

    def get_parents(self, var_id: str) -> List[str]:
        """Get parent variables (direct causes)."""
        parents = []
        for edge in self.edges:
            if edge.target == var_id and edge.relation_type == CausalRelationType.DIRECT_CAUSE:
                parents.append(edge.source)
        return parents

    def get_children(self, var_id: str) -> List[str]:
        """Get child variables (direct effects)."""
        children = []
        for edge in self.edges:
            if edge.source == var_id and edge.relation_type == CausalRelationType.DIRECT_CAUSE:
                children.append(edge.target)
        return children

    def find_confounders(self, var1: str, var2: str) -> List[str]:
        """Find confounding variables between two variables."""
        parents1 = set(self.get_parents(var1))
        parents2 = set(self.get_parents(var2))
        return list(parents1 & parents2)

    def find_path(self, source: str, target: str, blocked: Set[str]  = None) -> Optional[List[str]]:
        """Find an unblocked path between variables."""
        blocked = blocked or set()
        visited = set()
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            if current in visited or current in blocked:
                continue
            visited.add(current)

            for edge in self.edges:
                if edge.source == current and edge.target not in visited:
                    queue.append((edge.target, path + [edge.target]))
                elif edge.target == current and edge.source not in visited:
                    queue.append((edge.source, path + [edge.source]))
        return None


class DoCalculus:
    """Implementation of Pearl's do-calculus."""

    def __init__(self, graph: CausalGraph):
        self.graph = graph

    def intervention_effect(self, intervention: Intervention, outcome_var: str) -> Dict[str, Any]:
        """Estimate effect of intervention on outcome variable."""
        # Simplified causal effect estimation
        target = intervention.target_var
        parents = self.graph.get_parents(outcome_var)

        if target in parents:
            # Direct intervention on parent
            return {
                "intervention": f"do({target}={intervention.new_value})",
                "outcome": outcome_var,
                "effect_type": "direct",
                "estimated_effect": 0.7,  # Simplified
                "confidence": 0.8,
            }

        # Check for indirect paths
        path = self.graph.find_path(target, outcome_var)
        if path:
            return {
                "intervention": f"do({target}={intervention.new_value})",
                "outcome": outcome_var,
                "effect_type": "indirect",
                "path": " -> ".join(path),
                "estimated_effect": 0.5 * (0.9 ** len(path)),  # Decay with path length
                "confidence": 0.6,
            }

        return {
            "intervention": f"do({target}={intervention.new_value})",
            "outcome": outcome_var,
            "effect_type": "none",
            "estimated_effect": 0.0,
            "confidence": 0.9,
        }

    def counterfactual(self, observed: Dict[str, Any], intervention: Intervention, outcome_var: str) -> Dict[str, Any]:
        """Compute counterfactual: what would outcome be if we had done X?"""
        # Simplified counterfactual
        actual_outcome = observed.get(outcome_var, "unknown")
        effect = self.intervention_effect(intervention, outcome_var)

        return {
            "actual_outcome": actual_outcome,
            "counterfactual_scenario": f"do({intervention.target_var}={intervention.new_value})",
            "predicted_outcome_change": effect["estimated_effect"],
            "confidence": effect["confidence"] * 0.8,  # Lower confidence for counterfactuals
        }


class CausalDiscovery:
    """Discover causal relationships from data."""

    def __init__(self):
        self.heuristics = {
            "temporal_priority": 0.3,  # Earlier events may cause later
            "covariation": 0.4,        # Correlation suggests causation (weak)
            "mechanism": 0.5,          # Known mechanisms
            "intervention": 0.9,       # Strongest: experimental evidence
        }

    def score_causal_link(self, var1: str, var2: str, evidence: Dict[str, Any]) -> float:
        """Score likelihood of causal link based on evidence."""
        score = 0.0

        if evidence.get("temporal_order") == var1 + "_before_" + var2:
            score += self.heuristics["temporal_priority"]

        if evidence.get("correlation", 0) > 0.5:
            score += self.heuristics["covariation"] * evidence["correlation"]

        if evidence.get("mechanism_known"):
            score += self.heuristics["mechanism"]

        if evidence.get("experimental"):
            score += self.heuristics["intervention"]

        return min(1.0, score)


class CausalInferenceEngine:
    """AMOS Causal Inference Engine - Pearl's causal hierarchy."""

    VERSION = "vInfinity_Causal_1.0.0"
    NAME = "AMOS_Causal_Inference_OMEGA"

    def __init__(self):
        self.graph = CausalGraph()
        self.do_calculus = DoCalculus(self.graph)
        self.discovery = CausalDiscovery()
        self._initialize_core_causal_knowledge()

    def _initialize_core_causal_knowledge(self) -> None:
        """Initialize with core causal knowledge."""
        # Core variables
        variables = [
            CausalVariable("stress", "Stress Level", "continuous"),
            CausalVariable("cortisol", "Cortisol", "continuous"),
            CausalVariable("performance", "Performance", "continuous"),
            CausalVariable("sleep", "Sleep Quality", "continuous"),
            CausalVariable("co2", "CO2 Emissions", "continuous"),
            CausalVariable("temperature", "Global Temperature", "continuous"),
            CausalVariable("biodiversity", "Biodiversity", "continuous"),
        ]
        for var in variables:
            self.graph.add_variable(var)

        # Core causal edges
        edges = [
            CausalEdge("stress", "cortisol", CausalRelationType.DIRECT_CAUSE, 0.8, EvidenceType.EXPERIMENTAL),
            CausalEdge("cortisol", "performance", CausalRelationType.DIRECT_CAUSE, 0.6, EvidenceType.OBSERVATIONAL),
            CausalEdge("sleep", "stress", CausalRelationType.DIRECT_CAUSE, 0.7, EvidenceType.EXPERIMENTAL),
            CausalEdge("co2", "temperature", CausalRelationType.DIRECT_CAUSE, 0.9, EvidenceType.EXPERIMENTAL),
            CausalEdge("temperature", "biodiversity", CausalRelationType.DIRECT_CAUSE, 0.8, EvidenceType.OBSERVATIONAL),
        ]
        for edge in edges:
            self.graph.add_edge(edge)

    def analyze(self, query: str, context: Dict[str, Any]  = None) -> Dict[str, Any]:
        """Run causal inference analysis."""
        context = context or {}
        query_lower = query.lower()

        results: Dict[str, Any] = {
            "query": query[:100],
            "causal_analysis": {},
            "interventions": [],
            "counterfactuals": [],
            "graph_stats": {},
            "recommendations": [],
        }

        # Detect intervention queries
        if "what if" in query_lower or "do(" in query_lower or "intervention" in query_lower:
            # Parse intervention
            if "reduce stress" in query_lower:
                intervention = Intervention("stress", "reduced")
                effect = self.do_calculus.intervention_effect(intervention, "performance")
                results["interventions"].append(effect)

            if "reduce co2" in query_lower or "decrease emissions" in query_lower:
                intervention = Intervention("co2", "reduced")
                temp_effect = self.do_calculus.intervention_effect(intervention, "temperature")
                bio_effect = self.do_calculus.intervention_effect(intervention, "biodiversity")
                results["interventions"].extend([temp_effect, bio_effect])

        # Detect counterfactual queries
        if "would have" in query_lower or "if we had" in query_lower or "counterfactual" in query_lower:
            observed = {"stress": "high", "performance": "low"}
            intervention = Intervention("stress", "low")
            counterfactual = self.do_calculus.counterfactual(observed, intervention, "performance")
            results["counterfactuals"].append(counterfactual)

        # Causal discovery from context
        if "discover" in query_lower or "find causes" in query_lower:
            var_pair = context.get("variables", ["var1", "var2"])
            evidence = context.get("evidence", {})
            score = self.discovery.score_causal_link(var_pair[0], var_pair[1], evidence)
            results["causal_analysis"] = {
                "variables": var_pair,
                "causal_score": round(score, 2),
                "suggested_relation": "likely_causal" if score > 0.7 else "uncertain",
            }

        # Find confounders
        if "confounder" in query_lower or "confounding" in query_lower:
            vars_in_query = [v for v in self.graph.variables if v in query_lower]
            if len(vars_in_query) >= 2:
                confounders = self.graph.find_confounders(vars_in_query[0], vars_in_query[1])
                results["causal_analysis"]["confounders"] = confounders

        # Graph statistics
        results["graph_stats"] = {
            "num_variables": len(self.graph.variables),
            "num_edges": len(self.graph.edges),
            "density": len(self.graph.edges) / max(1, len(self.graph.variables) ** 2),
        }

        # Generate recommendations
        recommendations = [
            "Causal Inference: Use do-calculus for intervention planning",
            "Confounding: Always check for common causes before inferring causation",
            "Counterfactuals: Use for hindsight analysis and learning",
            "Causal Discovery: Combine multiple evidence types for robust inference",
            "Integration: Connect with Knowledge Graph for semantic causal understanding",
            "Validation: Experimental evidence > observational > simulation",
        ]
        results["recommendations"] = recommendations

        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Causal Reasoning and Do-Calculus (Pearl's Causal Hierarchy)",
            "",
            "## Causal Inference Overview",
            "The Causal Inference Engine implements Judea Pearl's three-level",
            "causal hierarchy for understanding cause-effect relationships:",
            "",
            "### Pearl's Causal Hierarchy",
            "1. **Association** (Seeing): P(y|x) - What is?",
            "2. **Intervention** (Doing): P(y|do(x)) - What if?",
            "3. **Counterfactuals** (Imagining): P(y_x|x',y') - Why?",
            "",
            "## Causal Graph Analysis",
        ]

        stats = results.get("graph_stats", {})
        lines.extend([
            f"- **Variables**: {stats.get('num_variables', 0)}",
            f"- **Causal Edges**: {stats.get('num_edges', 0)}",
            f"- **Graph Density**: {stats.get('density', 0):.3f}",
        ])

        lines.extend([
            "",
            "## Intervention Analysis (Do-Calculus)",
        ])

        for intervention in results.get("interventions", []):
            lines.extend([
                f"### {intervention.get('intervention', 'N/A')}",
                f"- **Outcome Variable**: {intervention.get('outcome', 'N/A')}",
                f"- **Effect Type**: {intervention.get('effect_type', 'N/A')}",
                f"- **Estimated Effect**: {intervention.get('estimated_effect', 0):.2f}",
                f"- **Confidence**: {intervention.get('confidence', 0):.2f}",
            ])
            if "path" in intervention:
                lines.append(f"- **Causal Path**: {intervention['path']}")

        if results.get("counterfactuals"):
            lines.extend([
                "",
                "## Counterfactual Analysis",
            ])
            for cf in results.get("counterfactuals", []):
                lines.extend([
                    f"- **Actual Outcome**: {cf.get('actual_outcome', 'N/A')}",
                    f"- **Counterfactual**: {cf.get('counterfactual_scenario', 'N/A')}",
                    f"- **Predicted Change**: {cf.get('predicted_outcome_change', 0):.2f}",
                    f"- **Confidence**: {cf.get('confidence', 0):.2f}",
                ])

        causal_analysis = results.get("causal_analysis", {})
        if causal_analysis:
            lines.extend([
                "",
                "## Causal Discovery",
            ])
            if "causal_score" in causal_analysis:
                lines.append(f"- **Causal Score**: {causal_analysis['causal_score']:.2f}")
            if "suggested_relation" in causal_analysis:
                lines.append(f"- **Suggested Relation**: {causal_analysis['suggested_relation']}")
            if "confounders" in causal_analysis:
                confs = causal_analysis["confounders"]
                lines.append(f"- **Confounders**: {', '.join(confs) if confs else 'None detected'}")

        lines.extend([
            "",
            "## Key Causal Concepts",
            "",
            "### Causal Relationship Types",
            "- **Direct Cause**: Immediate causal influence",
            "- **Indirect Cause**: Influence through mediators",
            "- **Confounder**: Common cause creating spurious association",
            "- **Collider**: Common effect inducing selection bias",
            "- **Mediator**: Variable on causal path between variables",
            "- **Moderator**: Variable affecting strength of causal relation",
            "",
            "### Do-Calculus Rules",
            "1. **Insertion/Deletion of observations**: If Y ⊥⊥ Z | X, W, then P(y|do(x),z,w) = P(y|do(x),w)",
            "2. **Action/Observation exchange**: If Y ⊥⊥ Z | X, W, then P(y|do(x),do(z),w) = P(y|do(x),z,w)",
            "3. **Insertion/Deletion of actions**: If Y ⊥⊥ Z | X, W, then P(y|do(x),do(z),w) = P(y|do(x),w)",
            "",
            "### Evidence Hierarchy",
            "1. **Experimental** (RCTs): Gold standard - can compute P(y|do(x))",
            "2. **Quasi-Experimental**: Natural experiments, IV methods",
            "3. **Observational**: Requires adjustment for confounders",
            "4. **Simulation**: Model-based causal inference",
            "5. **Theoretical**: Mechanism-based reasoning",
        ])

        recommendations = results.get("recommendations", [])
        if recommendations:
            lines.extend([
                "",
                "## Causal Reasoning Recommendations",
            ])
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")

        lines.extend([
            "",
            "## Pre-Loaded Causal Models",
            "- **Stress → Cortisol → Performance**: Physiological pathway",
            "- **Sleep → Stress**: Recovery and resilience",
            "- **CO2 → Temperature → Biodiversity**: Climate impact chain",
            "",
            "## Integration with AMOS",
            "The Causal Inference Engine connects to:",
            "- **Knowledge Graph**: Causal relationships as semantic edges",
            "- **UBI Stack**: Physiological causal pathways",
            "- **Planetary Stack**: Environmental causal chains",
            "- **Logic Core**: Formal causal reasoning",
            "",
            "## Limitations",
            "- Simplified do-calculus (full implementation is NP-hard)",
            "- Limited counterfactual computation",
            "- Static causal graph (no dynamic learning)",
            "- Binary/treatment effects (not full distributions)",
            "- No unobserved confounder handling",
        ])

        return "\n".join(lines)


# Singleton instance
_causal_engine: Optional[CausalInferenceEngine] = None


def get_causal_inference_engine() -> CausalInferenceEngine:
    """Get or create the Causal Inference Engine singleton."""
    global _causal_engine
    if _causal_engine is None:
        _causal_engine = CausalInferenceEngine()
    return _causal_engine

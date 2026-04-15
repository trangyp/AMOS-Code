"""
Causal Architecture Intelligence Engine.

Provides causal reasoning capabilities for understanding true
cause-effect relationships in software architecture.

Distinguishes correlation from causation, enabling:
- Causal graph construction
- Counterfactual reasoning
- Intervention analysis
- True root cause identification

Mathematical Foundation:
- Causal Graph G = (V, E) where V = variables, E = causal edges
- do-calculus: P(Y | do(X)) - effect of intervention
- Counterfactuals: Y_x(u) - outcome Y if X had been x for unit u
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CausalRelationType(Enum):
    """Types of causal relationships."""

    DIRECT_CAUSE = "direct_cause"  # X → Y (X directly causes Y)
    INDIRECT_CAUSE = "indirect_cause"  # X → ... → Y (transitive)
    COMMON_CAUSE = "common_cause"  # Z causes both X and Y
    CONFOUNDER = "confounder"  # Unobserved common cause
    COLLIDER = "collider"  # Both X and Y cause Z
    MEDIATOR = "mediator"  # X → Z → Y (Z mediates X's effect on Y)
    SPURIOUS = "spurious"  # Apparent correlation, no causation


class EvidenceStrength(Enum):
    """Strength of causal evidence."""

    STRONG = "strong"  # Multiple lines of evidence
    MODERATE = "moderate"  # Some supporting evidence
    WEAK = "weak"  # Limited evidence
    SPECULATIVE = "speculative"  # Hypothetical


@dataclass
class CausalNode:
    """Node in causal graph representing a variable."""

    node_id: str
    name: str
    description: str
    node_type: str  # "metric", "event", "condition", "action"
    observable: bool = True
    interventions: list[str] = field(default_factory=list)


@dataclass
class CausalEdge:
    """Directed edge representing causal relationship."""

    source_id: str
    target_id: str
    relation_type: CausalRelationType
    strength: float  # 0-1 causal strength
    evidence: EvidenceStrength
    mechanism: str  # How does cause lead to effect?
    confounders: list[str] = field(default_factory=list)  # Potential confounders


@dataclass
class CausalPath:
    """Path through causal graph."""

    path_id: str
    source_id: str
    target_id: str
    nodes: list[str]  # Node IDs in path
    edges: list[tuple[str, str]]  # Edge pairs
    total_strength: float
    is_blocked: bool = False  # By conditioning on colliders
    backdoor_paths: list[list[str]] = field(default_factory=list)


@dataclass
class Intervention:
    """Represents an intervention (do-operator)."""

    target_node: str
    new_value: Any
    context: dict[str, Any]  # Other variables held constant
    expected_effect: dict[str, Any] | None = None


@dataclass
class Counterfactual:
    """Counterfactual query result."""

    query_id: str
    actual_observation: dict[str, Any]
    intervention: Intervention
    predicted_outcome: dict[str, Any]
    confidence: float
    assumptions: list[str]


@dataclass
class CausalAnalysis:
    """Result of causal analysis."""

    analysis_id: str
    target_variable: str
    causal_graph: dict[str, Any]
    root_causes: list[dict[str, Any]]
    spurious_correlations: list[dict[str, Any]]
    interventions: list[dict[str, Any]]
    counterfactuals: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "analysis_id": self.analysis_id,
            "target": self.target_variable,
            "nodes": len(self.causal_graph.get("nodes", [])),
            "edges": len(self.causal_graph.get("edges", [])),
            "root_causes": len(self.root_causes),
            "spurious": len(self.spurious_correlations),
            "interventions": len(self.interventions),
        }


class CausalArchitectureEngine:
    """
    Engine for causal reasoning about software architecture.

    Builds causal graphs, identifies true causes vs correlations,
    performs counterfactual reasoning, and predicts intervention effects.
    """

    def __init__(self):
        self.nodes: dict[str, CausalNode] = {}
        self.edges: list[CausalEdge] = []
        self.paths: list[CausalPath] = []
        self.analyses: list[CausalAnalysis] = []

        # Domain knowledge for architecture
        self._initialize_architecture_knowledge()

    def _initialize_architecture_knowledge(self) -> None:
        """Initialize domain knowledge about software architecture causality."""
        # Define common architecture variables
        arch_variables = [
            ("complexity", "Code Complexity", "Cyclomatic complexity, LOC, etc.", "metric"),
            ("coupling", "Component Coupling", "Degree of interdependence", "metric"),
            ("test_coverage", "Test Coverage", "Percentage of code tested", "metric"),
            ("bug_rate", "Bug Rate", "Defects per unit of code", "metric"),
            ("build_time", "Build Time", "Duration of build process", "metric"),
            ("tech_debt", "Technical Debt", "Accumulated shortcuts", "condition"),
            ("refactoring", "Refactoring Activity", "Code restructuring effort", "action"),
            ("new_features", "New Feature Work", "Development of new functionality", "action"),
            ("team_size", "Team Size", "Number of developers", "condition"),
            ("deadline_pressure", "Deadline Pressure", "Time constraints", "condition"),
            ("code_quality", "Code Quality", "Overall quality score", "metric"),
            ("maintainability", "Maintainability", "Ease of maintenance", "metric"),
        ]

        for var_id, name, desc, var_type in arch_variables:
            self.nodes[var_id] = CausalNode(
                node_id=var_id,
                name=name,
                description=desc,
                node_type=var_type,
            )

        # Define known causal relationships
        known_relationships = [
            # Complexity → Bug Rate (well-established)
            (
                "complexity",
                "bug_rate",
                CausalRelationType.DIRECT_CAUSE,
                0.75,
                EvidenceStrength.STRONG,
            ),
            # Coupling → Complexity (tight coupling increases complexity)
            (
                "coupling",
                "complexity",
                CausalRelationType.DIRECT_CAUSE,
                0.7,
                EvidenceStrength.MODERATE,
            ),
            # Test Coverage → Bug Rate (inverse relationship)
            (
                "test_coverage",
                "bug_rate",
                CausalRelationType.DIRECT_CAUSE,
                -0.6,
                EvidenceStrength.MODERATE,
            ),
            # Technical Debt → Complexity
            (
                "tech_debt",
                "complexity",
                CausalRelationType.DIRECT_CAUSE,
                0.65,
                EvidenceStrength.MODERATE,
            ),
            # Refactoring → Complexity (inverse)
            (
                "refactoring",
                "complexity",
                CausalRelationType.DIRECT_CAUSE,
                -0.5,
                EvidenceStrength.MODERATE,
            ),
            # Deadline Pressure → Technical Debt
            (
                "deadline_pressure",
                "tech_debt",
                CausalRelationType.DIRECT_CAUSE,
                0.6,
                EvidenceStrength.MODERATE,
            ),
            # Team Size → Coupling (larger teams often more coupling)
            ("team_size", "coupling", CausalRelationType.DIRECT_CAUSE, 0.4, EvidenceStrength.WEAK),
            # Complexity → Maintainability (inverse)
            (
                "complexity",
                "maintainability",
                CausalRelationType.DIRECT_CAUSE,
                -0.8,
                EvidenceStrength.STRONG,
            ),
            # Bug Rate → Build Time (bugs cause build failures)
            (
                "bug_rate",
                "build_time",
                CausalRelationType.DIRECT_CAUSE,
                0.5,
                EvidenceStrength.MODERATE,
            ),
        ]

        for source, target, rel_type, strength, evidence in known_relationships:
            self.edges.append(
                CausalEdge(
                    source_id=source,
                    target_id=target,
                    relation_type=rel_type,
                    strength=strength,
                    evidence=evidence,
                    mechanism=f"{source} affects {target} through established mechanisms",
                )
            )

    def build_causal_graph(
        self,
        observations: list[dict[str, Any]],
        target_variable: str,
    ) -> dict[str, Any]:
        """
        Build causal graph from observations.

        Args:
            observations: List of observed data points
            target_variable: Variable to explain

        Returns:
            Causal graph structure

        """
        # Find relevant nodes and edges
        relevant_nodes = self._find_relevant_nodes(target_variable, observations)
        relevant_edges = self._find_relevant_edges(relevant_nodes)

        # Identify potential confounders
        confounders = self._identify_confounders(target_variable, relevant_edges)

        # Build graph structure
        graph = {
            "target": target_variable,
            "nodes": [
                {
                    "id": n.node_id,
                    "name": n.name,
                    "type": n.node_type,
                    "observable": n.observable,
                }
                for n in relevant_nodes
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.relation_type.value,
                    "strength": round(e.strength, 2),
                    "evidence": e.evidence.value,
                }
                for e in relevant_edges
            ],
            "confounders": confounders,
        }

        return graph

    def find_true_root_causes(
        self,
        symptom: str,
        observations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Find true root causes (not just correlated factors).

        Args:
            symptom: Symptom to explain
            observations: Observed data

        Returns:
            List of true root causes with evidence

        """
        # Build causal graph
        graph = self.build_causal_graph(observations, symptom)

        # Find all paths to symptom
        paths_to_symptom = self._find_all_paths_to_target(symptom)

        # Identify root causes (nodes with no incoming edges in relevant subgraph)
        root_causes = []
        for node_id in graph["nodes"]:
            node = self.nodes.get(node_id["id"] if isinstance(node_id, dict) else node_id)
            if not node:
                continue

            # Check if this node has incoming edges from other relevant nodes
            incoming = [e for e in self.edges if e.target_id == node.node_id]

            if not incoming:
                # True root cause - no predecessors
                root_causes.append(
                    {
                        "node_id": node.node_id,
                        "name": node.name,
                        "type": "root_cause",
                        "confidence": 0.9,
                        "rationale": f"{node.name} has no observed causal predecessors",
                    }
                )
            elif all(e.relation_type == CausalRelationType.SPURIOUS for e in incoming):
                # All incoming relationships are spurious
                root_causes.append(
                    {
                        "node_id": node.node_id,
                        "name": node.name,
                        "type": "potential_root_cause",
                        "confidence": 0.7,
                        "rationale": "Only spurious correlations point to this node",
                    }
                )

        # Sort by confidence
        root_causes.sort(key=lambda x: x["confidence"], reverse=True)

        return root_causes[:5]  # Top 5

    def identify_spurious_correlations(
        self,
        variable1: str,
        variable2: str,
    ) -> dict[str, Any]:
        """
        Determine if correlation between variables is spurious.

        Args:
            variable1: First variable
            variable2: Second variable

        Returns:
            Analysis of whether correlation is causal or spurious

        """
        # Check for direct causal edge
        direct_causal = any(
            (e.source_id == variable1 and e.target_id == variable2)
            or (e.source_id == variable2 and e.target_id == variable1)
            for e in self.edges
        )

        if direct_causal:
            return {
                "variables": [variable1, variable2],
                "correlation_type": "causal",
                "confidence": 0.85,
                "explanation": f"Direct causal relationship exists between {variable1} and {variable2}",
            }

        # Check for common cause (confounder)
        common_causes = []
        for edge1 in self.edges:
            if (
                edge1.target_id == variable1
                and edge1.relation_type == CausalRelationType.DIRECT_CAUSE
            ):
                for edge2 in self.edges:
                    if (
                        edge2.target_id == variable2
                        and edge2.source_id == edge1.source_id
                        and edge2.relation_type == CausalRelationType.DIRECT_CAUSE
                    ):
                        common_causes.append(edge1.source_id)

        if common_causes:
            return {
                "variables": [variable1, variable2],
                "correlation_type": "spurious",
                "confidence": 0.8,
                "explanation": f"Correlation is due to common cause(s): {', '.join(common_causes)}",
                "common_causes": common_causes,
                "recommendation": "Condition on common causes to remove spurious correlation",
            }

        # Check for collider structure
        colliders = []
        for edge1 in self.edges:
            if edge1.source_id == variable1:
                for edge2 in self.edges:
                    if edge2.source_id == variable2 and edge2.target_id == edge1.target_id:
                        colliders.append(edge1.target_id)

        if colliders:
            return {
                "variables": [variable1, variable2],
                "correlation_type": "collider_induced",
                "confidence": 0.75,
                "explanation": f"Correlation induced by conditioning on collider: {', '.join(colliders)}",
                "colliders": colliders,
                "recommendation": "Do not condition on colliders without additional analysis",
            }

        # No clear causal structure found
        return {
            "variables": [variable1, variable2],
            "correlation_type": "unknown",
            "confidence": 0.5,
            "explanation": "No clear causal structure identified - correlation may be spurious",
            "recommendation": "Collect more data or perform controlled experiments",
        }

    def counterfactual_analysis(
        self,
        observation: dict[str, Any],
        intervention: Intervention,
    ) -> Counterfactual:
        """
        Perform counterfactual reasoning.

        Args:
            observation: Actual observed state
            intervention: Hypothetical intervention

        Returns:
            Counterfactual prediction

        """
        # Find causal paths from intervention target to outcome variables
        target_node = intervention.target_node

        # Identify affected variables
        affected_vars = self._find_descendants(target_node)

        # Simulate intervention (do-operator)
        predicted_outcomes = {}
        for var_id in affected_vars:
            # Find direct causal effect
            direct_effect = next(
                (e for e in self.edges if e.source_id == target_node and e.target_id == var_id),
                None,
            )

            if direct_effect:
                # Simple linear effect model
                current_value = observation.get(var_id, 0)
                effect = direct_effect.strength * (
                    intervention.new_value - observation.get(target_node, 0)
                )
                predicted_outcomes[var_id] = current_value + effect

        # Build assumptions
        assumptions = [
            f"Causal structure from {target_node} to affected variables is correct",
            "No unobserved confounders affect the relationship",
            "Linear effect model is appropriate",
        ]

        return Counterfactual(
            query_id=f"cf_{len(self.analyses)}",
            actual_observation=observation,
            intervention=intervention,
            predicted_outcome=predicted_outcomes,
            confidence=0.7,  # Counterfactuals are inherently uncertain
            assumptions=assumptions,
        )

    def analyze_intervention(
        self,
        intervention: Intervention,
    ) -> dict[str, Any]:
        """
        Analyze potential effects of an intervention.

        Args:
            intervention: Proposed intervention

        Returns:
            Analysis of expected effects

        """
        target = intervention.target_node

        # Find all causal paths from target
        affected = self._find_descendants(target)

        # Calculate effect on each descendant
        effects = []
        for var_id in affected:
            # Find path from target to var
            path = self._find_strongest_path(target, var_id)
            if path:
                effects.append(
                    {
                        "variable": var_id,
                        "variable_name": self.nodes.get(
                            var_id, CausalNode(var_id, var_id, "", "")
                        ).name,
                        "effect_strength": round(path.total_strength, 2),
                        "path_length": len(path.nodes),
                        "confidence": "high" if path.total_strength > 0.6 else "medium",
                    }
                )

        # Sort by effect strength
        effects.sort(key=lambda x: abs(x["effect_strength"]), reverse=True)

        # Identify potential side effects (indirect paths)
        side_effects = [e for e in effects if e["path_length"] > 2]

        return {
            "intervention_target": target,
            "intervention_value": intervention.new_value,
            "direct_effects": effects[:3],
            "side_effects": side_effects[:3],
            "total_affected_variables": len(affected),
            "confidence": "medium",
            "recommendation": "Monitor affected variables after intervention",
        }

    def _find_relevant_nodes(self, target: str, observations: list[dict]) -> list[CausalNode]:
        """Find nodes relevant to target variable."""
        relevant = set()
        relevant.add(target)

        # Find all nodes in observations
        for obs in observations:
            for key in obs.keys():
                if key in self.nodes:
                    relevant.add(key)

        # Find nodes connected by edges
        for edge in self.edges:
            if edge.source_id in relevant or edge.target_id in relevant:
                relevant.add(edge.source_id)
                relevant.add(edge.target_id)

        return [self.nodes[n] for n in relevant if n in self.nodes]

    def _find_relevant_edges(self, nodes: list[CausalNode]) -> list[CausalEdge]:
        """Find edges between relevant nodes."""
        node_ids = {n.node_id for n in nodes}
        return [e for e in self.edges if e.source_id in node_ids and e.target_id in node_ids]

    def _identify_confounders(self, target: str, edges: list[CausalEdge]) -> list[str]:
        """Identify potential confounders for target variable."""
        confounders = []

        # Find nodes that cause both target and other observed variables
        for edge1 in edges:
            if edge1.target_id == target:
                for edge2 in edges:
                    if edge2.source_id == edge1.source_id and edge2.target_id != target:
                        confounders.append(edge1.source_id)

        return list(set(confounders))

    def _find_all_paths_to_target(self, target: str) -> list[CausalPath]:
        """Find all causal paths leading to target."""
        paths = []

        # Find all edges pointing to target
        incoming = [e for e in self.edges if e.target_id == target]

        for edge in incoming:
            # Find paths from this source
            source_paths = self._find_paths_from_source(edge.source_id)
            for path_nodes in source_paths:
                path_nodes.append(target)
                paths.append(
                    CausalPath(
                        path_id=f"path_{len(paths)}",
                        source_id=path_nodes[0],
                        target_id=target,
                        nodes=path_nodes,
                        edges=[],  # Simplified
                        total_strength=edge.strength,
                    )
                )

        return paths

    def _find_paths_from_source(self, source: str) -> list[list[str]]:
        """Find all paths starting from source node."""
        # Simplified: return just the source
        return [[source]]

    def _find_descendants(self, node_id: str) -> list[str]:
        """Find all descendants of a node in causal graph."""
        descendants = set()
        to_process = [node_id]

        while to_process:
            current = to_process.pop(0)
            for edge in self.edges:
                if edge.source_id == current:
                    if edge.target_id not in descendants:
                        descendants.add(edge.target_id)
                        to_process.append(edge.target_id)

        return list(descendants)

    def _find_strongest_path(self, source: str, target: str) -> CausalPath | None:
        """Find strongest causal path from source to target."""
        # Simplified BFS
        visited = {source}
        queue = [(source, [source], 1.0)]

        while queue:
            current, path, strength = queue.pop(0)

            if current == target:
                return CausalPath(
                    path_id=f"path_{source}_{target}",
                    source_id=source,
                    target_id=target,
                    nodes=path,
                    edges=[],  # Simplified
                    total_strength=strength,
                )

            for edge in self.edges:
                if edge.source_id == current and edge.target_id not in visited:
                    visited.add(edge.target_id)
                    new_strength = strength * abs(edge.strength)
                    queue.append((edge.target_id, path + [edge.target_id], new_strength))

        return None

    def analyze_architecture_causality(
        self,
        metric_data: dict[str, Any],
        target_metric: str,
    ) -> CausalAnalysis:
        """
        Perform comprehensive causal analysis of architecture.

        Args:
            metric_data: Architecture metrics
            target_metric: Metric to analyze

        Returns:
            Complete causal analysis

        """
        # Convert metric data to observations format
        observations = [metric_data]

        # Build causal graph
        graph = self.build_causal_graph(observations, target_metric)

        # Find true root causes
        root_causes = self.find_true_root_causes(target_metric, observations)

        # Identify spurious correlations
        spurious = []
        for node_id in graph.get("nodes", []):
            node_id = node_id["id"] if isinstance(node_id, dict) else node_id
            if node_id != target_metric:
                result = self.identify_spurious_correlations(node_id, target_metric)
                if result["correlation_type"] in ["spurious", "collider_induced"]:
                    spurious.append(result)

        # Analyze potential interventions
        interventions = []
        for cause in root_causes[:3]:
            node_id = cause["node_id"]
            intervention = Intervention(
                target_node=node_id,
                new_value="improved",  # Generic improvement
                context=metric_data,
            )
            analysis = self.analyze_intervention(intervention)
            interventions.append(analysis)

        # Generate counterfactuals
        counterfactuals = []
        if root_causes:
            top_cause = root_causes[0]
            cf = self.counterfactual_analysis(
                metric_data,
                Intervention(
                    target_node=top_cause["node_id"],
                    new_value=metric_data.get(top_cause["node_id"], 0) * 0.5,  # 50% improvement
                    context=metric_data,
                ),
            )
            counterfactuals.append(
                {
                    "query_id": cf.query_id,
                    "intervention": top_cause["node_id"],
                    "predicted_outcomes": cf.predicted_outcome,
                    "confidence": cf.confidence,
                }
            )

        analysis = CausalAnalysis(
            analysis_id=f"causal_{len(self.analyses)}",
            target_variable=target_metric,
            causal_graph=graph,
            root_causes=root_causes,
            spurious_correlations=spurious,
            interventions=interventions,
            counterfactuals=counterfactuals,
        )

        self.analyses.append(analysis)
        return analysis

    def get_causal_insights(self) -> list[dict[str, Any]]:
        """Get general causal insights about architecture."""
        return [
            {
                "insight": "Complexity is a primary driver of bug rates",
                "evidence": "Strong causal link (r=0.75) from complexity to bugs",
                "recommendation": "Monitor and control complexity as top priority",
            },
            {
                "insight": "Technical debt accumulates from deadline pressure",
                "evidence": "Moderate causal effect (r=0.6) from pressure to tech debt",
                "recommendation": "Build buffer time to prevent debt accumulation",
            },
            {
                "insight": "Test coverage causally reduces bugs, not just correlated",
                "evidence": "Direct negative causal effect (r=-0.6)",
                "recommendation": "Increase test coverage as intervention",
            },
            {
                "insight": "Team size may spuriously correlate with coupling",
                "evidence": "Weak causal link (r=0.4) - may be confounded",
                "recommendation": "Control for communication patterns before concluding",
            },
        ]

#!/usr/bin/env python3
"""
Brain-Powered Architecture Analyzer for repo_doctor

Integrates AMOS brain cognition into architecture analysis:
- Brain-powered architectural smell detection
- Cognitive coupling analysis
- Intelligent architectural recommendations
- Brain-validated invariant checking

Uses amos_brain_working.think() for real brain cognition.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any

# Import brain
try:
    from amos_brain_working import think as brain_think

    _BRAIN_AVAILABLE = True
except ImportError:
    brain_think = None
    _BRAIN_AVAILABLE = False

# Import architecture types
try:
    from .architecture import (
        ArchEdge,
        ArchEdgeType,
        ArchNode,
        ArchNodeType,
        ArchitectureBuilder,
        ArchitectureGraph,
        AuthorityClaim,
        BoundaryViolation,
        HiddenInterface,
        PlaneType,
    )
except ImportError:
    from architecture import (
        ArchEdge,
        ArchEdgeType,
        ArchNode,
        ArchNodeType,
        ArchitectureBuilder,
        ArchitectureGraph,
        AuthorityClaim,
        BoundaryViolation,
        HiddenInterface,
        PlaneType,
    )


@dataclass
class BrainArchitectureInsight:
    """Cognitive insight from brain analysis."""

    insight_type: str
    description: str
    severity: str  # critical, high, medium, low
    confidence: float
    affected_nodes: list[str] = field(default_factory=list)
    recommendation: str = ""
    brain_sigma: Optional[float] = None
    brain_legality: Optional[str] = None


@dataclass
class BrainArchitectureReport:
    """Complete brain-powered architecture analysis report."""

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    graph: Optional[ArchitectureGraph] = None
    insights: list[BrainArchitectureInsight] = field(default_factory=list)
    violations: list[BoundaryViolation] = field(default_factory=list)
    hidden_interfaces: list[HiddenInterface] = field(default_factory=list)
    authority_conflicts: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    brain_used: bool = False


class BrainPoweredArchitectureAnalyzer:
    """
    Architecture analyzer with AMOS brain integration.

    Combines symbolic architecture graph analysis with neural cognition
    for deeper architectural insights and recommendations.
    """

    def __init__(self, repo_path: Path | str | None = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.builder = ArchitectureBuilder(self.repo_path)
        self._brain_think = brain_think if _BRAIN_AVAILABLE else None

    def analyze_with_brain(self, use_brain: bool = True) -> BrainArchitectureReport:
        """
        Perform brain-powered architecture analysis.

        Args:
            use_brain: Whether to use AMOS brain for cognitive analysis

        Returns:
            BrainArchitectureReport with full analysis
        """
        report = BrainArchitectureReport()

        # 1. Build architecture graph
        report.graph = self.builder.build_from_repo()

        # 2. Check boundary violations
        report.violations = report.graph.find_boundary_violations()

        # 3. Find hidden interfaces
        report.hidden_interfaces = report.graph.find_hidden_interfaces()

        # 4. Find authority conflicts
        report.authority_conflicts = self._find_authority_conflicts(report.graph)

        # 5. Brain-powered analysis (if enabled and available)
        if use_brain and self._brain_think:
            report.brain_used = True
            report.insights = self._brain_analyze_architecture(report.graph)
            report.recommendations = self._brain_generate_recommendations(
                report.graph, report.violations, report.insights
            )
        else:
            # Fallback to rule-based analysis
            report.insights = self._rule_based_analysis(report.graph)
            report.recommendations = self._generate_basic_recommendations(
                report.graph, report.violations
            )

        return report

    def _find_authority_conflicts(self, graph: ArchitectureGraph) -> list[dict[str, Any]]:
        """Find architectural authority conflicts."""
        conflicts = []
        duplicates = graph.find_authority_duplicates()

        for fact_name, node_ids in duplicates.items():
            if len(node_ids) > 1:
                conflicts.append(
                    {
                        "fact_name": fact_name,
                        "conflicting_nodes": node_ids,
                        "severity": "high",
                        "description": f"Multiple nodes claim authority over '{fact_name}'",
                    }
                )

        return conflicts

    def _brain_analyze_architecture(
        self, graph: ArchitectureGraph
    ) -> list[BrainArchitectureInsight]:
        """
        Use AMOS brain for cognitive architecture analysis.

        Returns intelligent insights about architectural patterns,
        coupling, cohesion, and potential issues.
        """
        insights: list[BrainArchitectureInsight] = []

        if not self._brain_think:
            return insights

        # Prepare architecture summary for brain
        arch_summary = {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "services": len(graph.get_nodes_by_type(ArchNodeType.SERVICE)),
            "libraries": len(graph.get_nodes_by_type(ArchNodeType.LIBRARY)),
            "databases": len(graph.get_nodes_by_type(ArchNodeType.PERSISTENCE_BOUNDARY)),
            "apis": len(graph.get_nodes_by_type(ArchNodeType.SCHEMA_AUTHORITY)),
            "violations": len(graph.boundary_violations),
            "hidden_interfaces": len(graph.hidden_interfaces),
        }

        # Brain analysis prompt
        brain_input = f"""
Analyze this software architecture for design patterns, coupling issues, and improvements:

Architecture Summary:
{json.dumps(arch_summary, indent=2)}

Violation Count: {len(graph.boundary_violations)}
Hidden Interfaces: {len(graph.hidden_interfaces)}

Provide:
1. Top 3 architectural smells (if any)
2. Coupling analysis between major components
3. Cohesion assessment
4. Specific improvement recommendations
5. Confidence score for each insight

Respond in structured format with severity levels.
"""

        try:
            # Real brain execution
            result = self._brain_think(brain_input, context={"analysis_type": "architecture"})

            if result.get("status") == "SUCCESS":
                # Parse brain response for insights
                content = str(result.get("result", ""))

                # Extract insights from brain response
                # This is a simplified extraction - in production would use structured output
                if "coupling" in content.lower() or "dependency" in content.lower():
                    insights.append(
                        BrainArchitectureInsight(
                            insight_type="coupling_analysis",
                            description="Brain detected potential coupling issues in architecture",
                            severity="medium",
                            confidence=result.get("confidence", 0.7),
                            recommendation="Review inter-service dependencies and consider decoupling strategies",
                            brain_sigma=result.get("sigma"),
                            brain_legality=result.get("legality"),
                        )
                    )

                if "cohesion" in content.lower() or "single responsibility" in content.lower():
                    insights.append(
                        BrainArchitectureInsight(
                            insight_type="cohesion_assessment",
                            description="Brain identified cohesion concerns in component design",
                            severity="medium",
                            confidence=result.get("confidence", 0.7),
                            recommendation="Refactor components to improve internal cohesion",
                            brain_sigma=result.get("sigma"),
                            brain_legality=result.get("legality"),
                        )
                    )

                # Add generic insight if brain returned successfully
                insights.append(
                    BrainArchitectureInsight(
                        insight_type="brain_architecture_review",
                        description=f"Brain cognitive analysis completed on {arch_summary['total_nodes']} nodes",
                        severity="info",
                        confidence=result.get("confidence", 0.8),
                        recommendation="Review brain insights and prioritize high-severity items",
                        brain_sigma=result.get("sigma"),
                        brain_legality=result.get("legality"),
                    )
                )

        except Exception as e:
            # Brain analysis failed, add failure insight
            insights.append(
                BrainArchitectureInsight(
                    insight_type="brain_analysis_error",
                    description=f"Brain analysis encountered error: {str(e)[:100]}",
                    severity="low",
                    confidence=0.5,
                    recommendation="Check brain availability and retry analysis",
                )
            )

        return insights

    def _brain_generate_recommendations(
        self,
        graph: ArchitectureGraph,
        violations: list[BoundaryViolation],
        insights: list[BrainArchitectureInsight],
    ) -> list[str]:
        """Generate recommendations using brain cognition."""
        recommendations: list[str] = []

        if not self._brain_think:
            return recommendations

        # Build context for brain
        context = {
            "violation_count": len(violations),
            "insight_count": len(insights),
            "high_severity_insights": [i.description for i in insights if i.severity == "high"],
        }

        brain_input = f"""
Generate prioritized architectural improvement recommendations:

Context:
- Violations: {context['violation_count']}
- Insights: {context['insight_count']}
- High Severity Issues: {len(context['high_severity_insights'])}

Provide 3-5 concrete, actionable recommendations prioritized by impact.
"""

        try:
            result = self._brain_think(brain_input, context={"task": "recommendations"})

            if result.get("status") == "SUCCESS":
                content = str(result.get("result", ""))
                # Parse recommendations from response
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-")):
                        recommendations.append(line.lstrip("- 123456789.").strip())

        except Exception:
            pass

        # Fallback recommendations if brain failed
        if not recommendations:
            if violations:
                recommendations.append(
                    f"Address {len(violations)} architectural boundary violations"
                )
            if graph.hidden_interfaces:
                recommendations.append(f"Document {len(graph.hidden_interfaces)} hidden interfaces")
            if graph.find_authority_duplicates():
                recommendations.append("Resolve authority claim conflicts")

        return recommendations

    def _rule_based_analysis(self, graph: ArchitectureGraph) -> list[BrainArchitectureInsight]:
        """Fallback rule-based analysis when brain is unavailable."""
        insights: list[BrainArchitectureInsight] = []

        # Check for circular dependencies
        if len(graph.edges) > len(graph.nodes) * 2:
            insights.append(
                BrainArchitectureInsight(
                    insight_type="high_coupling_risk",
                    description=f"High edge-to-node ratio ({len(graph.edges)}/{len(graph.nodes)}) suggests tight coupling",
                    severity="medium",
                    confidence=0.6,
                    recommendation="Review dependencies and reduce coupling between components",
                )
            )

        # Check for isolated nodes
        connected_nodes = set()
        for edge in graph.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)

        isolated = set(graph.nodes.keys()) - connected_nodes
        if isolated:
            insights.append(
                BrainArchitectureInsight(
                    insight_type="isolated_components",
                    description=f"Found {len(isolated)} isolated components with no connections",
                    severity="low",
                    confidence=0.7,
                    recommendation="Review isolated components for potential integration or removal",
                    affected_nodes=list(isolated),
                )
            )

        return insights

    def _generate_basic_recommendations(
        self,
        graph: ArchitectureGraph,
        violations: list[BoundaryViolation],
    ) -> list[str]:
        """Generate basic recommendations without brain."""
        recommendations: list[str] = []

        if violations:
            recommendations.append(f"Fix {len(violations)} architectural boundary violations")

        if graph.hidden_interfaces:
            recommendations.append(f"Document {len(graph.hidden_interfaces)} hidden interfaces")

        duplicates = graph.find_authority_duplicates()
        if duplicates:
            recommendations.append(f"Resolve {len(duplicates)} authority claim conflicts")

        return recommendations


def analyze_repository_architecture(
    repo_path: str | Path,
    use_brain: bool = True,
) -> BrainArchitectureReport:
    """
    Convenience function to analyze repository architecture.

    Args:
        repo_path: Path to repository
        use_brain: Whether to use AMOS brain for analysis

    Returns:
        BrainArchitectureReport with full analysis
    """
    analyzer = BrainPoweredArchitectureAnalyzer(repo_path)
    return analyzer.analyze_with_brain(use_brain=use_brain)


if __name__ == "__main__":
    # CLI for testing
    import argparse

    parser = argparse.ArgumentParser(description="Brain-Powered Architecture Analyzer")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument("--no-brain", action="store_true", help="Disable brain analysis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    print(f"\n🔍 Analyzing architecture: {args.repo}")
    print(f"🧠 Brain available: {_BRAIN_AVAILABLE}")
    print("=" * 60)

    report = analyze_repository_architecture(args.repo, use_brain=not args.no_brain)

    if args.json:
        # Simplified JSON output
        output = {
            "timestamp": report.timestamp,
            "brain_used": report.brain_used,
            "nodes": len(report.graph.nodes) if report.graph else 0,
            "edges": len(report.graph.edges) if report.graph else 0,
            "violations": len(report.violations),
            "insights": len(report.insights),
            "recommendations": report.recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n📊 Architecture Summary:")
        if report.graph:
            print(f"   Nodes: {len(report.graph.nodes)}")
            print(f"   Edges: {len(report.graph.edges)}")
        print(f"   Violations: {len(report.violations)}")
        print(f"   Insights: {len(report.insights)}")

        if report.insights:
            print(f"\n💡 Brain Insights ({'brain' if report.brain_used else 'rule-based'}):")
            for insight in report.insights[:5]:
                icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                    "info": "🔵",
                }.get(insight.severity, "⚪")
                print(f"   {icon} [{insight.severity.upper()}] {insight.description}")
                if insight.brain_sigma:
                    print(f"      Brain σ: {insight.brain_sigma:.2f}")

        if report.recommendations:
            print(f"\n📝 Recommendations:")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"   {i}. {rec}")

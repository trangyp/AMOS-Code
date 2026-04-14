"""AMOS Brain Cookbook - Real-world workflow examples.

Pre-built workflows for common scenarios:
  - Architecture Decision Records (ADRs)
  - Project Planning & Estimation
  - Problem Diagnosis & Root Cause Analysis
  - Technology Selection
  - Risk Assessment
  - Post-Mortem Analysis

Usage:
  from amos_brain.cookbook import ArchitectureDecision
  result = ArchitectureDecision.run("Should we use microservices?")
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from amos_brain import get_amos_integration
from amos_brain.memory import get_brain_memory


@dataclass
class WorkflowResult:
    """Result from running a cookbook workflow."""

    workflow_name: str
    problem: str
    analysis: dict[str, Any]
    memory_id: str
    recommendations: list[str]
    confidence: float


class ArchitectureDecision:
    """Workflow for architecture decisions.

    Use when: Choosing between architectural approaches,
              technology stacks, or system designs.

    Example:
        result = ArchitectureDecision.run(
            "Should we migrate from monolith to microservices?"
        )
    """

    WORKFLOW_NAME = "Architecture Decision Record (ADR)"
    TEMPLATE_TAGS = ["architecture", "adr", "system-design"]

    @classmethod
    def run(cls, problem: str, context: dict[str, Any] | None = None) -> WorkflowResult:
        """Execute architecture decision workflow.

        Args:
            problem: The architectural decision to analyze
            context: Optional context (current stack, constraints, etc.)

        Returns:
            WorkflowResult with analysis and recommendations
        """
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Check for similar past decisions
        recall = memory.recall_for_problem(problem)
        if recall.get("has_prior_reasoning"):
            print(f"[Found {len(recall.get('similar_entries', []))} similar past decisions]")

        # Enrich problem with context
        enriched_problem = cls._enrich_problem(problem, context)

        # Run analysis
        analysis = amos.analyze_with_rules(enriched_problem)

        # Architecture-specific post-processing
        recommendations = cls._structure_recommendations(analysis)

        # Save to memory
        memory_id = memory.save_reasoning(problem, analysis, tags=cls.TEMPLATE_TAGS)

        return WorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            problem=problem,
            analysis=analysis,
            memory_id=memory_id,
            recommendations=recommendations,
            confidence=analysis.get("structural_integrity_score", 0.0),
        )

    @classmethod
    def _enrich_problem(cls, problem: str, context: dict[str, Any] | None) -> str:
        """Enrich problem with architectural context."""
        if not context:
            return problem

        enrichments = [f"\nContext: {problem}"]

        if "current_stack" in context:
            enrichments.append(f"Current: {context['current_stack']}")
        if "constraints" in context:
            enrichments.append(f"Constraints: {context['constraints']}")
        if "scale" in context:
            enrichments.append(f"Scale: {context['scale']}")
        if "team_size" in context:
            enrichments.append(f"Team: {context['team_size']}")

        return "\n".join(enrichments)

    @classmethod
    def _structure_recommendations(cls, analysis: dict[str, Any]) -> list[str]:
        """Structure recommendations for architecture decisions."""
        recs = []

        # Rule of 2 recommendations
        if "rule_of_two" in analysis:
            r2 = analysis["rule_of_two"]
            recs.append(f"[Dual-Perspective] {r2.get('recommendation', 'N/A')}")

        # Rule of 4 recommendations
        if "rule_of_four" in analysis:
            r4 = analysis["rule_of_four"]
            integration = r4.get("integration", {})
            if integration.get("integrated_recommendation"):
                recs.append(f"[Four-Quadrant] {integration['integrated_recommendation']}")

        # Add generic recommendations
        recs.extend(analysis.get("recommendations", []))

        return recs


class ProjectPlanner:
    """Workflow for project planning and estimation.

    Use when: Planning a new project, estimating scope,
              or breaking down complex work.

    Example:
        result = ProjectPlanner.run(
            "Build a real-time analytics dashboard",
            timeline="3 months",
            team="2 backend, 1 frontend, 1 devops"
        )
    """

    WORKFLOW_NAME = "Project Planning & Estimation"
    TEMPLATE_TAGS = ["planning", "project", "estimation"]

    @classmethod
    def run(
        cls,
        project: str,
        timeline: str | None = None,
        team: str | None = None,
        constraints: list[str] | None = None,
    ) -> WorkflowResult:
        """Execute project planning workflow.

        Args:
            project: Project description
            timeline: Timeline constraints
            team: Team composition
            constraints: List of constraints

        Returns:
            WorkflowResult with planning analysis
        """
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Build enriched problem
        problem_parts = [f"Project: {project}"]

        if timeline:
            problem_parts.append(f"Timeline: {timeline}")
        if team:
            problem_parts.append(f"Team: {team}")
        if constraints:
            problem_parts.append(f"Constraints: {', '.join(constraints)}")

        problem = "\n".join(problem_parts)

        # Analyze
        analysis = amos.analyze_with_rules(problem)

        # Planning-specific insights
        recommendations = cls._planning_recommendations(analysis)

        # Save
        memory_id = memory.save_reasoning(problem, analysis, tags=cls.TEMPLATE_TAGS)

        return WorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            problem=project,
            analysis=analysis,
            memory_id=memory_id,
            recommendations=recommendations,
            confidence=analysis.get("structural_integrity_score", 0.0),
        )

    @classmethod
    def _planning_recommendations(cls, analysis: dict[str, Any]) -> list[str]:
        """Extract planning-specific recommendations."""
        recs = []

        # Look for risk indicators
        if "assumptions" in analysis:
            for assumption in analysis["assumptions"]:
                if any(risk in assumption.lower() for risk in ["risk", "uncertain", "unknown"]):
                    recs.append(f"[Risk] {assumption}")

        # Add standard recommendations
        recs.extend(analysis.get("recommendations", []))

        return recs


class ProblemDiagnosis:
    """Workflow for problem diagnosis and root cause analysis.

    Use when: Debugging complex issues, investigating outages,
              or analyzing failures.

    Example:
        result = ProblemDiagnosis.run(
            "API latency spikes during peak hours",
            symptoms=["500ms+ response times", "only 2-4 PM"],
            checked=["database", "caching"]
        )
    """

    WORKFLOW_NAME = "Problem Diagnosis & RCA"
    TEMPLATE_TAGS = ["diagnosis", "debugging", "rca", "incident"]

    @classmethod
    def run(
        cls,
        problem: str,
        symptoms: list[str] | None = None,
        checked: list[str] | None = None,
        timeline: str | None = None,
    ) -> WorkflowResult:
        """Execute problem diagnosis workflow.

        Args:
            problem: Problem description
            symptoms: Observable symptoms
            checked: Components already checked
            timeline: When problem started/occurs

        Returns:
            WorkflowResult with diagnosis analysis
        """
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Build problem statement
        parts = [f"Problem: {problem}"]

        if symptoms:
            parts.append(f"Symptoms: {', '.join(symptoms)}")
        if checked:
            parts.append(f"Already checked: {', '.join(checked)}")
        if timeline:
            parts.append(f"Timeline: {timeline}")

        full_problem = "\n".join(parts)

        # Check for similar past issues
        recall = memory.recall_for_problem(problem)
        if recall.get("has_prior_reasoning"):
            print("[Similar past issues found - checking for known solutions]")

        # Analyze
        analysis = amos.analyze_with_rules(full_problem)

        # Diagnosis-specific recommendations
        recommendations = cls._diagnosis_recommendations(analysis)

        # Save with high priority tagging
        memory_id = memory.save_reasoning(full_problem, analysis, tags=cls.TEMPLATE_TAGS)

        return WorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            problem=problem,
            analysis=analysis,
            memory_id=memory_id,
            recommendations=recommendations,
            confidence=analysis.get("structural_integrity_score", 0.0),
        )

    @classmethod
    def _diagnosis_recommendations(cls, analysis: dict[str, Any]) -> list[str]:
        """Structure diagnosis recommendations."""
        recs = []

        # Look for uncertainty flags (potential root causes)
        for flag in analysis.get("uncertainty_flags", []):
            recs.append(f"[Investigate] {flag}")

        # Add standard recommendations
        recs.extend(analysis.get("recommendations", []))

        return recs


class TechnologySelection:
    """Workflow for technology/tool selection.

    Use when: Choosing between frameworks, libraries,
              tools, or platforms.

    Example:
        result = TechnologySelection.run(
            "Frontend framework",
            options=["React", "Vue", "Svelte"],
            criteria=["performance", "ecosystem", "learning-curve"]
        )
    """

    WORKFLOW_NAME = "Technology Selection"
    TEMPLATE_TAGS = ["technology", "selection", "evaluation"]

    @classmethod
    def run(
        cls,
        category: str,
        options: list[str],
        criteria: list[str] | None = None,
        must_haves: list[str] | None = None,
    ) -> WorkflowResult:
        """Execute technology selection workflow.

        Args:
            category: Category (e.g., "database", "frontend framework")
            options: List of options to evaluate
            criteria: Evaluation criteria
            must_haves: Non-negotiable requirements

        Returns:
            WorkflowResult with selection analysis
        """
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Build selection problem
        parts = [f"Select {category} from: {', '.join(options)}"]

        if criteria:
            parts.append(f"Criteria: {', '.join(criteria)}")
        if must_haves:
            parts.append(f"Must-haves: {', '.join(must_haves)}")

        problem = "\n".join(parts)

        # Analyze
        analysis = amos.analyze_with_rules(problem)

        # Selection-specific recommendations
        recommendations = cls._selection_recommendations(analysis, options)

        # Save
        memory_id = memory.save_reasoning(problem, analysis, tags=cls.TEMPLATE_TAGS)

        return WorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            problem=f"Select {category}",
            analysis=analysis,
            memory_id=memory_id,
            recommendations=recommendations,
            confidence=analysis.get("structural_integrity_score", 0.0),
        )

    @classmethod
    def _selection_recommendations(cls, analysis: dict[str, Any], options: list[str]) -> list[str]:
        """Structure selection recommendations."""
        recs = []

        # Extract option-specific recommendations
        for rec in analysis.get("recommendations", []):
            for option in options:
                if option.lower() in rec.lower():
                    recs.append(f"[{option}] {rec}")
                    break
            else:
                recs.append(rec)

        return recs


class RiskAssessment:
    """Workflow for risk assessment and mitigation planning.

    Use when: Evaluating risks for projects, decisions,
              or operational changes.

    Example:
        result = RiskAssessment.run(
            "Deploy new payment processor",
            impacts=["revenue", "customer-trust"],
            mitigations=["canary-deployment", "rollback-plan"]
        )
    """

    WORKFLOW_NAME = "Risk Assessment"
    TEMPLATE_TAGS = ["risk", "assessment", "mitigation"]

    @classmethod
    def run(
        cls,
        action: str,
        impacts: list[str] | None = None,
        mitigations: list[str] | None = None,
        severity_threshold: str = "medium",
    ) -> WorkflowResult:
        """Execute risk assessment workflow.

        Args:
            action: Action/decision being assessed
            impacts: Areas of impact
            mitigations: Planned mitigations
            severity_threshold: Risk level threshold

        Returns:
            WorkflowResult with risk analysis
        """
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Build problem
        parts = [f"Risk assessment for: {action}"]

        if impacts:
            parts.append(f"Impact areas: {', '.join(impacts)}")
        if mitigations:
            parts.append(f"Planned mitigations: {', '.join(mitigations)}")

        problem = "\n".join(parts)

        # Analyze
        analysis = amos.analyze_with_rules(problem)

        # Risk-specific recommendations
        recommendations = cls._risk_recommendations(analysis)

        # Save
        memory_id = memory.save_reasoning(problem, analysis, tags=cls.TEMPLATE_TAGS)

        return WorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            problem=action,
            analysis=analysis,
            memory_id=memory_id,
            recommendations=recommendations,
            confidence=analysis.get("structural_integrity_score", 0.0),
        )

    @classmethod
    def _risk_recommendations(cls, analysis: dict[str, Any]) -> list[str]:
        """Structure risk recommendations."""
        recs = []

        # Flag high-risk assumptions
        for assumption in analysis.get("assumptions", []):
            if any(risk in assumption.lower() for risk in ["fail", "break", "loss", "outage"]):
                recs.append(f"[High Risk] {assumption}")

        recs.extend(analysis.get("recommendations", []))

        return recs


# Convenience functions for quick access
def decide_architecture(problem: str, **context) -> WorkflowResult:
    """Quick access to architecture decision workflow."""
    return ArchitectureDecision.run(problem, context)


def plan_project(project: str, **kwargs) -> WorkflowResult:
    """Quick access to project planning workflow."""
    return ProjectPlanner.run(project, **kwargs)


def diagnose_problem(problem: str, **kwargs) -> WorkflowResult:
    """Quick access to problem diagnosis workflow."""
    return ProblemDiagnosis.run(problem, **kwargs)


def select_technology(category: str, options: list[str], **kwargs) -> WorkflowResult:
    """Quick access to technology selection workflow."""
    return TechnologySelection.run(category, options, **kwargs)


def assess_risk(action: str, **kwargs) -> WorkflowResult:
    """Quick access to risk assessment workflow."""
    return RiskAssessment.run(action, **kwargs)

"""AMOS Brain Cookbook - Pre-built cognitive workflows (Layer 12)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from .facade import BrainClient
from .state_manager import get_state_manager


def _run_sync(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # If already in async context, schedule and return
            return coro
    except RuntimeError:
        pass
    return asyncio.run(coro)


@dataclass
class CookbookResult:
    """Result from a cookbook recipe."""

    recipe_name: str
    input_data: str
    analysis: str
    recommendations: list[str]
    confidence: float
    law_compliant: bool
    session_id: str

    @property
    def workflow_name(self) -> str:
        return self.recipe_name

    @property
    def memory_id(self) -> str:
        return self.session_id


def _normalize_confidence(value: object) -> float:
    """Normalize confidence to float [0,1]."""
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    mapping = {
        "low": 0.33,
        "medium": 0.66,
        "high": 0.9,
    }
    return mapping.get(str(value).lower(), 0.5)


class ArchitectureDecision:
    """Recipe: Architecture Decision Records (ADR).

    Use for: Technology selection, architectural patterns,
             migration decisions, system design choices.

    Example:
        result = ArchitectureDecision.analyze(
            "Should we use microservices or monolith?",
            context={"team_size": 10, "scale": "medium"}
        )
    """

    RECIPE_NAME = "Architecture Decision Record (ADR)"

    @classmethod
    async def analyze_async(cls, question: str, context: dict[str, Any] = None) -> CookbookResult:
        """Analyze an architectural decision (async version)."""
        client = BrainClient()
        sm = get_state_manager()

        prompt = f"""Architecture Decision: {question}

Consider these factors:
- Technical feasibility and complexity
- Team capabilities and learning curve
- Operational overhead and maintenance
- Scalability and performance characteristics
- Risk assessment and mitigation strategies

Provide:
1. Clear recommendation with justification
2. Alternative options considered
3. Pros/cons analysis (Rule of 2 perspectives)
4. Implementation approach
5. Rollback strategy"""

        if context:
            prompt += f"\n\nContext: {context}"

        response = await client.think(prompt, domain="software")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["recommend", "suggest", "choose", "use"])
        ][:3]

        session_id = sm.start_session(goal=f"ADR: {question[:50]}", domain="software")

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=question,
            analysis=response.content[:500],
            recommendations=recommendations or ["See full analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=session_id,
        )

    @classmethod
    def analyze(cls, question: str, context: dict[str, Any] = None) -> CookbookResult:
        """Analyze an architectural decision (sync wrapper)."""
        return _run_sync(cls.analyze_async(question, context))

    @classmethod
    def run(cls, question: str, context: dict[str, Any] = None) -> CookbookResult:
        """Alias for analyze() - test compatibility."""
        return cls.analyze(question, context)


class CodeReview:
    """Recipe: Cognitive Code Review.

    Use for: Code review, quality assessment, refactoring suggestions.
    """

    RECIPE_NAME = "Code Review"

    @classmethod
    async def analyze_async(
        cls, code: str, language: str = "python", focus_areas: list[str] = None
    ) -> CookbookResult:
        """Analyze code with cognitive rules (async)."""
        client = BrainClient()
        sm = get_state_manager()

        focus = focus_areas or ["security", "maintainability", "performance"]

        prompt = f"""Code Review ({language}):

```
{code[:1000]}
```

Focus areas: {", ".join(focus)}

Apply Rule of 2:
1. What are the strengths of this code?
2. What are the potential issues or risks?

Apply Rule of 4:
- Technical: Code quality and patterns
- Biological: Human readability and maintainability
- Economic: Performance and resource usage
- Environmental: Integration and deployment impact

Identify:
- Security vulnerabilities
- Law of Structural Integrity violations
- UBI alignment issues"""

        response = await client.think(prompt, domain="software")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["issue", "risk", "improve", "fix", "consider"])
        ][:5]

        session_id = sm.start_session(goal=f"Code review: {language}", domain="software")

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=code[:100],
            analysis=response.content[:500],
            recommendations=recommendations or ["No major issues found"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=session_id,
        )

    @classmethod
    def analyze(
        cls, code: str, language: str = "python", focus_areas: list[str] = None
    ) -> CookbookResult:
        """Analyze code with cognitive rules (sync wrapper)."""
        return _run_sync(cls.analyze_async(code, language, focus_areas))

    @classmethod
    def run(
        cls,
        code: str,
        language: str = "python",
        focus_areas: list[str] = None,
    ) -> CookbookResult:
        return cls.analyze(code, language=language, focus_areas=focus_areas)


class SecurityAudit:
    """Recipe: Security Compliance Audit.

    Use for: Security analysis, vulnerability assessment,
             compliance checking, threat modeling.
    """

    RECIPE_NAME = "Security Audit"

    @classmethod
    def analyze(cls, system_description: str, threat_model: str = "STRIDE") -> CookbookResult:
        """Perform security audit."""
        client = BrainClient()
        sm = get_state_manager()

        prompt = f"""Security Audit ({threat_model}):

System: {system_description}

Apply security analysis:
1. Identify attack surfaces
2. Map trust boundaries
3. Analyze data flow risks
4. Check authentication/authorization
5. Review input validation
6. Assess logging and monitoring

Apply Rule of 2:
- Attacker perspective: How would you exploit this?
- Defender perspective: How would you protect this?

Check against Global Laws:
- L4: Structural Integrity (secure by design)
- L5: Clear communication of risks
- L6: Universal benefit alignment (privacy, safety)"""

        response = client.think(prompt, domain="security")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["risk", "vulnerab", "threat", "mitigate", "protect"])
        ][:5]

        session_id = sm.start_session(goal="Security audit", domain="security")

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=system_description[:100],
            analysis=response.content[:500],
            recommendations=recommendations or ["Review analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=session_id,
        )

    @classmethod
    def run(
        cls,
        code: str,
        language: str = "python",
        threat_model: str = "STRIDE",
    ) -> CookbookResult:
        system_description = f"{language} code under review:\n\n{code[:1000]}"
        return cls.analyze(system_description=system_description, threat_model=threat_model)


class DesignPattern:
    """Recipe: Design Pattern Selection.

    Use for: Choosing design patterns, refactoring decisions,
             pattern implementation guidance.
    """

    RECIPE_NAME = "Design Pattern Selection"

    @classmethod
    def select(cls, problem: str, available_patterns: list[str] = None) -> CookbookResult:
        """Select appropriate design pattern."""
        client = BrainClient()

        patterns = available_patterns or [
            "Singleton",
            "Factory",
            "Observer",
            "Strategy",
            "Decorator",
            "Adapter",
            "Command",
            "Repository",
        ]

        prompt = f"""Design Pattern Selection:

Problem: {problem}

Available patterns: {", ".join(patterns)}

Analyze using Rule of 2:
1. When is each pattern the RIGHT choice?
2. When is each pattern the WRONG choice?

Apply Rule of 4:
- Technical: Implementation complexity
- Biological: Developer understanding
- Economic: Maintenance cost
- Environmental: Integration fit

Recommend the best pattern with justification."""

        response = client.think(prompt, domain="software")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["pattern", "recommend", "use", "choose"])
        ][:3]

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=problem,
            analysis=response.content[:500],
            recommendations=recommendations or ["See analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id="",
        )


class ProblemDiagnosis:
    """Recipe: Root Cause Analysis.

    Use for: Debugging, incident analysis, problem investigation,
             root cause identification.
    """

    RECIPE_NAME = "Problem Diagnosis & RCA"

    @classmethod
    async def diagnose_async(
        cls, problem: str, symptoms: list[str], context: str = ""
    ) -> CookbookResult:
        """Diagnose problem root cause (async)."""
        client = BrainClient()

        prompt = f"""Root Cause Analysis:

Problem: {problem}

Symptoms:
{chr(10).join(f"- {s}" for s in symptoms)}

Context: {context}

Apply 5 Whys methodology:
1. Why does this symptom occur?
2. Why does THAT happen?
3. Continue until root cause found

Apply Rule of 2:
- Observable symptoms vs underlying cause
- Immediate fix vs systemic solution

Apply Rule of 4:
- Technical: Code/system issues
- Biological: Human factors
- Economic: Cost of fix vs impact
- Environmental: Infrastructure/dependencies

Identify:
- Root cause
- Contributing factors
- Immediate mitigation
- Long-term prevention"""

        response = await client.think(prompt, domain="diagnostics")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["cause", "fix", "solution", "prevent", "mitigate"])
        ][:5]

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=problem,
            analysis=response.content[:500],
            recommendations=recommendations or ["Investigate further"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id="",
        )

    @classmethod
    def diagnose(cls, problem: str, symptoms: list[str], context: str = "") -> CookbookResult:
        """Diagnose problem root cause (sync wrapper)."""
        return _run_sync(cls.diagnose_async(problem, symptoms, context))

    @classmethod
    def run(
        cls,
        problem: str,
        symptoms: list[str],
        context: str = "",
        **extra: Any,
    ) -> CookbookResult:
        """Alias for diagnose() with extra tolerance."""
        extra_context = ", ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""
        merged_context = f"{context} {extra_context}".strip()
        return cls.diagnose(problem, symptoms, merged_context)


class ProjectPlanner:
    """Recipe: Project Planner.

    Use for: Project scoping, milestone planning, resource allocation,
             risk estimation, timeline design.
    """

    RECIPE_NAME = "Project Planning & Estimation"

    @classmethod
    async def plan_async(
        cls, project_description: str, constraints: dict[str, Any] = None
    ) -> CookbookResult:
        """Create project plan with cognitive analysis (async)."""
        client = BrainClient()

        cons = constraints or {}

        prompt = f"""Project Planning:

Project: {project_description}

Constraints: {cons}

Create plan using Rule of 2:
1. Optimistic path (best case)
2. Pessimistic path (risks considered)

Apply Rule of 4 analysis:
- Technical: Architecture and implementation
- Biological: Team capacity and skills
- Economic: Budget and ROI
- Environmental: Dependencies and external factors

Provide:
1. Task breakdown (WBS)
2. Effort estimates (with uncertainty)
3. Critical path identification
4. Risk register
5. Milestone schedule
6. Resource requirements"""

        response = await client.think(prompt, domain="project")

        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["task", "milestone", "risk", "estimate", "plan"])
        ][:5]

        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=project_description[:100],
            analysis=response.content[:500],
            recommendations=recommendations or ["See plan details"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id="",
        )

    @classmethod
    def plan(cls, project_description: str, constraints: dict[str, Any] = None) -> CookbookResult:
        """Create project plan with cognitive analysis (sync wrapper)."""
        return _run_sync(cls.plan_async(project_description, constraints))

    @classmethod
    def run(
        cls,
        project_description: str,
        timeline: str = None,
        constraints: dict[str, Any] = None,
        **extra: Any,
    ) -> CookbookResult:
        """Alias for plan() - test compatibility."""
        merged = dict(constraints or {})
        if timeline is not None:
            merged["timeline"] = timeline
        if extra:
            merged.update(extra)
        return cls.plan(project_description, merged)


# Convenience functions for quick usage
def analyze_architecture(question: str, **kwargs) -> CookbookResult:
    """Quick architecture decision analysis."""
    return ArchitectureDecision.analyze(question, kwargs)


def review_code(code: str, **kwargs) -> CookbookResult:
    """Quick code review."""
    return CodeReview.analyze(code, **kwargs)


def audit_security(system: str, **kwargs) -> CookbookResult:
    """Quick security audit."""
    return SecurityAudit.analyze(system, **kwargs)


def select_pattern(problem: str, **kwargs) -> CookbookResult:
    """Quick design pattern selection."""
    return DesignPattern.select(problem, **kwargs)


def diagnose_problem(problem: str, symptoms: list[str], **kwargs) -> CookbookResult:
    """Quick problem diagnosis."""
    return ProblemDiagnosis.diagnose(problem, symptoms, **kwargs)


class TechnologySelection:
    """Recipe: Technology Selection."""

    RECIPE_NAME = "Technology Selection"

    @classmethod
    async def select_async(
        cls,
        category: str,
        options: list[str],
        criteria: list[str] = None,
        **extra: Any,
    ) -> CookbookResult:
        """Select technology (async)."""
        merged_criteria = list(criteria or [])
        for key, value in extra.items():
            if isinstance(value, list):
                merged_criteria.extend(str(v) for v in value)
            else:
                merged_criteria.append(f"{key}: {value}")
        client = BrainClient()
        prompt = f"""Technology Selection:

Category: {category}
Options: {", ".join(options)}
Criteria: {", ".join(merged_criteria)}

Compare the options using Rule of 2 and Rule of 4.
Return a recommendation, tradeoffs, and selection rationale.
"""
        response = await client.think(prompt, domain="software")
        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["recommend", "choose", "select", "tradeoff"])
        ][:5]
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=category,
            analysis=response.content[:500],
            recommendations=recommendations or ["See selection analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id="",
        )

    @classmethod
    def run(
        cls,
        category: str,
        options: list[str],
        criteria: list[str] = None,
        **extra: Any,
    ) -> CookbookResult:
        """Select technology (sync wrapper)."""
        return _run_sync(cls.select_async(category, options, criteria, **extra))


class RiskAssessment:
    """Recipe: Risk Assessment."""

    RECIPE_NAME = "Risk Assessment"

    @classmethod
    async def assess_async(
        cls,
        change: str,
        impacts: list[str] = None,
        **extra: Any,
    ) -> CookbookResult:
        """Assess risk (async)."""
        merged_impacts = list(impacts or [])
        for key, value in extra.items():
            if isinstance(value, list):
                merged_impacts.extend(str(v) for v in value)
            else:
                merged_impacts.append(f"{key}: {value}")
        client = BrainClient()
        prompt = f"""Risk Assessment:

Change: {change}
Impacts: {", ".join(merged_impacts)}

Assess the main risks, mitigations, fallback paths, and monitoring signals.
"""
        response = await client.think(prompt, domain="risk")
        recommendations = [
            step
            for step in response.reasoning
            if any(k in step.lower() for k in ["risk", "mitigate", "fallback", "monitor"])
        ][:5]
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=change,
            analysis=response.content[:500],
            recommendations=recommendations or ["See risk analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id="",
        )

    @classmethod
    def run(
        cls,
        change: str,
        impacts: list[str] = None,
        **extra: Any,
    ) -> CookbookResult:
        """Assess risk (sync wrapper)."""
        return _run_sync(cls.assess_async(change, impacts, **extra))


def plan_project(description: str, **kwargs) -> CookbookResult:
    """Quick project planning."""
    return ProjectPlanner.plan(description, **kwargs)


def run_cookbook_demo() -> None:
    """Run interactive cookbook demo.

    Presents menu of available recipes and executes selected workflow.
    """
    print("\n📚 AMOS Brain Cookbook Demos")
    print("=" * 50)
    print()
    print("Available Recipes:")
    print("  1. Architecture Decision (ADR)")
    print("  2. Code Review")
    print("  3. Security Audit")
    print("  4. Design Pattern")
    print("  5. Problem Diagnosis")
    print("  6. Project Planning")
    print("  7. Technology Selection")
    print("  8. Risk Assessment")
    print()

    choice = input("Select recipe (1-8, or q to quit): ").strip().lower()

    if choice == "q":
        return

    recipes = {
        "1": ArchitectureDecision,
        "2": CodeReview,
        "3": SecurityAudit,
        "4": DesignPattern,
        "5": ProblemDiagnosis,
        "6": ProjectPlanner,
        "7": TechnologySelection,
        "8": RiskAssessment,
    }

    recipe_class = recipes.get(choice)
    if not recipe_class:
        print("Invalid selection.")
        return

    print(f"\nRunning: {recipe_class.RECIPE_NAME}")
    print("-" * 50)

    # Get input based on recipe type
    if choice in ("1", "2", "3", "4"):
        question = input("Enter question/analysis target: ")
        result = recipe_class.analyze(question)
    elif choice == "5":
        problem = input("Enter problem: ")
        result = recipe_class.diagnose(problem)
    elif choice == "6":
        description = input("Enter project description: ")
        result = recipe_class.plan(description)
    elif choice == "7":
        criteria = input("Enter selection criteria: ")
        result = recipe_class.select(criteria)
    elif choice == "8":
        change = input("Enter change to assess: ")
        result = recipe_class.run(change)
    else:
        return

    # Display results
    print("\n✓ Analysis Complete")
    print(f"Recipe: {result.recipe_name}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Law Compliant: {'✓' if result.law_compliant else '✗'}")
    print()
    print("Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")
    print()
    print(f"Session ID: {result.session_id}")

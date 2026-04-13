"""AMOS Brain Cookbook - Pre-built cognitive workflows (Layer 12)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .facade import BrainClient, think, decide
from .state_manager import get_state_manager


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
    """
    Recipe: Architecture Decision Records (ADR).
    
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
    def analyze(
        cls,
        question: str,
        context: dict[str, Any] | None = None
    ) -> CookbookResult:
        """Analyze an architectural decision."""
        client = BrainClient()
        sm = get_state_manager()
        
        # Build enriched prompt
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
        
        # Process through brain
        response = client.think(prompt, domain="software")
        
        # Extract recommendations from reasoning
        recommendations = [
            step for step in response.reasoning
            if any(k in step.lower() for k in ["recommend", "suggest", "choose", "use"])
        ][:3]
        
        # Create session for audit
        session_id = sm.start_session(goal=f"ADR: {question[:50]}", domain="software")
        
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=question,
            analysis=response.content[:500],
            recommendations=recommendations or ["See full analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=session_id
        )

    @classmethod
    def run(cls, question: str, context: dict[str, Any] | None = None) -> CookbookResult:
        """Alias for analyze() - test compatibility."""
        return cls.analyze(question, context)


class CodeReview:
    """
    Recipe: Cognitive Code Review.
    
    Use for: Reviewing code changes with law compliance,
             security analysis, best practice validation.
    
    Example:
        result = CodeReview.analyze(code="def transfer_money...")
    """
    
    RECIPE_NAME = "Cognitive Code Review"
    
    @classmethod
    def analyze(
        cls,
        code: str,
        language: str = "python",
        focus_areas: list[str] | None = None
    ) -> CookbookResult:
        """Analyze code with cognitive rules."""
        client = BrainClient()
        sm = get_state_manager()
        
        focus = focus_areas or ["security", "maintainability", "performance"]
        
        prompt = f"""Code Review ({language}):

```
{code[:1000]}
```

Focus areas: {', '.join(focus)}

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
        
        response = client.think(prompt, domain="software")
        
        recommendations = [
            step for step in response.reasoning
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
            session_id=session_id
        )


class SecurityAudit:
    """
    Recipe: Security Compliance Audit.
    
    Use for: Security analysis, vulnerability assessment,
             compliance checking, threat modeling.
    """
    
    RECIPE_NAME = "Security Audit"
    
    @classmethod
    def analyze(
        cls,
        system_description: str,
        threat_model: str = "STRIDE"
    ) -> CookbookResult:
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
            step for step in response.reasoning
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
            session_id=session_id
        )


class DesignPattern:
    """
    Recipe: Design Pattern Selection.
    
    Use for: Choosing design patterns, refactoring decisions,
             pattern implementation guidance.
    """
    
    RECIPE_NAME = "Design Pattern Selection"
    
    @classmethod
    def select(
        cls,
        problem: str,
        available_patterns: list[str] | None = None
    ) -> CookbookResult:
        """Select appropriate design pattern."""
        client = BrainClient()
        
        patterns = available_patterns or [
            "Singleton", "Factory", "Observer", "Strategy",
            "Decorator", "Adapter", "Command", "Repository"
        ]
        
        prompt = f"""Design Pattern Selection:

Problem: {problem}

Available patterns: {', '.join(patterns)}

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
            step for step in response.reasoning
            if any(k in step.lower() for k in ["pattern", "recommend", "use", "choose"])
        ][:3]
        
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=problem,
            analysis=response.content[:500],
            recommendations=recommendations or ["See analysis"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=""
        )


class ProblemDiagnosis:
    """
    Recipe: Root Cause Analysis.
    
    Use for: Debugging, incident analysis, problem investigation,
             root cause identification.
    """
    
    RECIPE_NAME = "Root Cause Analysis"
    
    @classmethod
    def diagnose(
        cls,
        problem: str,
        symptoms: list[str],
        context: str = ""
    ) -> CookbookResult:
        """Diagnose problem root cause."""
        client = BrainClient()
        
        prompt = f"""Root Cause Analysis:

Problem: {problem}

Symptoms:
{chr(10).join(f'- {s}' for s in symptoms)}

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
        
        response = client.think(prompt, domain="diagnostics")
        
        recommendations = [
            step for step in response.reasoning
            if any(k in step.lower() for k in ["cause", "fix", "solution", "prevent", "mitigate"])
        ][:5]
        
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=problem,
            analysis=response.content[:500],
            recommendations=recommendations or ["Investigate further"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=""
        )

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
    """
    Recipe: Project Planning & Estimation.
    
    Use for: Task breakdown, effort estimation, milestone planning,
             risk assessment for projects.
    """
    
    RECIPE_NAME = "Project Planner"
    
    @classmethod
    def plan(
        cls,
        project_description: str,
        constraints: dict[str, Any] | None = None
    ) -> CookbookResult:
        """Create project plan with cognitive analysis."""
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
        
        response = client.think(prompt, domain="project")
        
        recommendations = [
            step for step in response.reasoning
            if any(k in step.lower() for k in ["task", "milestone", "risk", "estimate", "plan"])
        ][:5]
        
        return CookbookResult(
            recipe_name=cls.RECIPE_NAME,
            input_data=project_description[:100],
            analysis=response.content[:500],
            recommendations=recommendations or ["See plan details"],
            confidence=_normalize_confidence(response.confidence),
            law_compliant=response.law_compliant,
            session_id=""
        )

    @classmethod
    def run(
        cls,
        project_description: str,
        timeline: str | None = None,
        constraints: dict[str, Any] | None = None,
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
    def run(
        cls,
        category: str,
        options: list[str],
        criteria: list[str] | None = None,
        **extra: Any,
    ) -> CookbookResult:
        merged_criteria = list(criteria or [])
        for key, value in extra.items():
            if isinstance(value, list):
                merged_criteria.extend(str(v) for v in value)
            else:
                merged_criteria.append(f"{key}: {value}")
        client = BrainClient()
        prompt = f"""Technology Selection:

Category: {category}
Options: {', '.join(options)}
Criteria: {', '.join(merged_criteria)}

Compare the options using Rule of 2 and Rule of 4.
Return a recommendation, tradeoffs, and selection rationale.
"""
        response = client.think(prompt, domain="software")
        recommendations = [
            step for step in response.reasoning
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


class RiskAssessment:
    """Recipe: Risk Assessment."""
    RECIPE_NAME = "Risk Assessment"

    @classmethod
    def run(
        cls,
        change: str,
        impacts: list[str] | None = None,
        **extra: Any,
    ) -> CookbookResult:
        merged_impacts = list(impacts or [])
        for key, value in extra.items():
            if isinstance(value, list):
                merged_impacts.extend(str(v) for v in value)
            else:
                merged_impacts.append(f"{key}: {value}")
        client = BrainClient()
        prompt = f"""Risk Assessment:

Change: {change}
Impacts: {', '.join(merged_impacts)}

Assess the main risks, mitigations, fallback paths, and monitoring signals.
"""
        response = client.think(prompt, domain="risk")
        recommendations = [
            step for step in response.reasoning
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


def plan_project(description: str, **kwargs) -> CookbookResult:
    """Quick project planning."""
    return ProjectPlanner.plan(description, **kwargs)

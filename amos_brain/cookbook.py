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
    confidence: str
    law_compliant: bool
    session_id: str


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
    
    RECIPE_NAME = "Architecture Decision Record"
    
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
            confidence=response.confidence,
            law_compliant=response.law_compliant,
            session_id=session_id
        )


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
            confidence=response.confidence,
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
            confidence=response.confidence,
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
            confidence=response.confidence,
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
            confidence=response.confidence,
            law_compliant=response.law_compliant,
            session_id=""
        )


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
            confidence=response.confidence,
            law_compliant=response.law_compliant,
            session_id=""
        )


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


def plan_project(description: str, **kwargs) -> CookbookResult:
    """Quick project planning."""
    return ProjectPlanner.plan(description, **kwargs)

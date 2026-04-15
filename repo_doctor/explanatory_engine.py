"""
Explanatory Intelligence Engine.

Generates human-understandable explanations for architecture decisions,
reasoning traces, and evidence presentation.

Provides:
- Decision explanation generation
- Reasoning trace visualization
- Evidence presentation
- Confidence explanation
- Action justification

Mathematical Foundation:
- Explanation: E: Decision → Natural Language
- Reasoning Trace: T: Decision → [Step]
- Evidence: V: Claim → [Supporting Facts]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExplanationType(Enum):
    """Types of explanations."""

    DECISION = "decision"  # Why was this decision made?
    REASONING = "reasoning"  # What was the reasoning path?
    EVIDENCE = "evidence"  # What evidence supports this?
    CONFIDENCE = "confidence"  # Why this confidence level?
    ACTION = "action"  # Why take this action?
    COMPARISON = "comparison"  # Compare alternatives


class EvidenceStrength(Enum):
    """Strength of evidence."""

    STRONG = "strong"  # Direct, unambiguous evidence
    MODERATE = "moderate"  # Significant supporting evidence
    WEAK = "weak"  # Limited or indirect evidence
    CONFLICTING = "conflicting"  # Evidence contradicts claim
    INSUFFICIENT = "insufficient"  # Not enough evidence


@dataclass
class Evidence:
    """Piece of evidence supporting a claim."""

    claim: str
    fact: str
    strength: EvidenceStrength
    source: str  # Where this evidence came from
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningStep:
    """Single step in reasoning chain."""

    step_number: int
    description: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    rule_applied: str  # What rule/logic was applied
    confidence_delta: float  # How confidence changed


@dataclass
class ReasoningTrace:
    """Complete reasoning trace for a decision."""

    trace_id: str
    decision_type: str
    start_state: dict[str, Any]
    final_state: dict[str, Any]
    steps: list[ReasoningStep] = field(default_factory=list)
    total_confidence: float = 0.0

    def add_step(self, step: ReasoningStep) -> None:
        """Add a reasoning step."""
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "decision_type": self.decision_type,
            "step_count": len(self.steps),
            "total_confidence": round(self.total_confidence, 3),
            "steps": [
                {
                    "step": s.step_number,
                    "description": s.description,
                    "rule": s.rule_applied,
                    "confidence_delta": round(s.confidence_delta, 3),
                }
                for s in self.steps
            ],
        }


@dataclass
class Explanation:
    """Generated explanation."""

    explanation_id: str
    explanation_type: ExplanationType
    target: str  # What is being explained
    natural_language: str  # Human-readable explanation
    technical_details: dict[str, Any] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "explanation_id": self.explanation_id,
            "type": self.explanation_type.value,
            "target": self.target,
            "explanation": self.natural_language,
            "confidence": round(self.confidence, 3),
            "evidence_count": len(self.evidence),
            "technical": self.technical_details,
        }


class ExplanatoryEngine:
    """
    Engine for generating explanations of architecture decisions.

    Transforms technical decisions into human-understandable explanations
    with supporting evidence and reasoning traces.
    """

    def __init__(self):
        self.explanations: list[Explanation] = []
        self.traces: list[ReasoningTrace] = []

    def explain_decision(
        self,
        decision: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> Explanation:
        """
        Generate natural language explanation for a decision.

        Args:
            decision: The decision to explain
            context: Additional context

        Returns:
            Human-readable explanation

        """
        decision_type = decision.get("type", "unknown")
        confidence = decision.get("confidence", 0.5)

        # Generate explanation based on decision type
        if decision_type == "governance":
            nl = self._explain_governance_decision(decision, context)
        elif decision_type == "prediction":
            nl = self._explain_prediction(decision, context)
        elif decision_type == "repair":
            nl = self._explain_repair(decision, context)
        elif decision_type == "pathology":
            nl = self._explain_pathology(decision, context)
        else:
            nl = self._explain_generic(decision, context)

        # Gather evidence
        evidence = self._gather_evidence(decision, context)

        explanation = Explanation(
            explanation_id=f"exp_{len(self.explanations)}",
            explanation_type=ExplanationType.DECISION,
            target=decision.get("id", "unknown"),
            natural_language=nl,
            technical_details={"decision": decision, "context": context},
            evidence=evidence,
            confidence=confidence,
        )

        self.explanations.append(explanation)
        return explanation

    def explain_confidence(
        self,
        score: float,
        factors: dict[str, Any],
    ) -> Explanation:
        """
        Explain why confidence is at a particular level.

        Args:
            score: Confidence score (0-1)
            factors: Factors contributing to confidence

        Returns:
            Confidence explanation

        """
        if score >= 0.9:
            level = "very high"
            reason = "Strong evidence with clear patterns"
        elif score >= 0.75:
            level = "high"
            reason = "Good evidence with minor uncertainties"
        elif score >= 0.6:
            level = "moderate"
            reason = "Some evidence but with gaps"
        elif score >= 0.4:
            level = "low"
            reason = "Limited evidence or conflicting signals"
        else:
            level = "very low"
            reason = "Insufficient evidence or high uncertainty"

        # Build factor explanation
        factor_texts = []
        for factor, value in factors.items():
            if isinstance(value, float):
                factor_texts.append(f"{factor}: {value:.2f}")
            else:
                factor_texts.append(f"{factor}: {value}")

        natural_language = f"""
Confidence is {level} ({score:.1%}) because: {reason}.

Key factors:
{chr(10).join(f"  - {ft}" for ft in factor_texts[:5])}

Recommendation: {"Proceed with action" if score >= 0.75 else "Review before action" if score >= 0.5 else "Gather more evidence"}
""".strip()

        explanation = Explanation(
            explanation_id=f"exp_conf_{len(self.explanations)}",
            explanation_type=ExplanationType.CONFIDENCE,
            target=f"confidence_{score:.2f}",
            natural_language=natural_language,
            technical_details={"score": score, "factors": factors},
            confidence=score,
        )

        self.explanations.append(explanation)
        return explanation

    def trace_reasoning(
        self,
        start_state: dict[str, Any],
        decision: dict[str, Any],
        steps_data: list[dict[str, Any]] | None = None,
    ) -> ReasoningTrace:
        """
        Generate reasoning trace from start to decision.

        Args:
            start_state: Initial state
            decision: Final decision
            steps_data: Intermediate reasoning steps

        Returns:
            Complete reasoning trace

        """
        trace_id = f"trace_{len(self.traces)}"

        trace = ReasoningTrace(
            trace_id=trace_id,
            decision_type=decision.get("type", "unknown"),
            start_state=start_state,
            final_state=decision,
            total_confidence=decision.get("confidence", 0.0),
        )

        # Build steps from data or infer
        if steps_data:
            for i, step_data in enumerate(steps_data):
                step = ReasoningStep(
                    step_number=i,
                    description=step_data.get("description", f"Step {i}"),
                    input_data=step_data.get("input", {}),
                    output_data=step_data.get("output", {}),
                    rule_applied=step_data.get("rule", "inference"),
                    confidence_delta=step_data.get("confidence_delta", 0.0),
                )
                trace.add_step(step)
        else:
            # Infer basic steps
            trace.add_step(
                ReasoningStep(
                    step_number=0,
                    description="Initial observation",
                    input_data=start_state,
                    output_data={"observed": True},
                    rule_applied="observation",
                    confidence_delta=0.1,
                )
            )
            trace.add_step(
                ReasoningStep(
                    step_number=1,
                    description="Pattern recognition",
                    input_data={"observed": True},
                    output_data={"pattern_match": decision.get("pattern", "unknown")},
                    rule_applied="pattern_matching",
                    confidence_delta=0.3,
                )
            )
            trace.add_step(
                ReasoningStep(
                    step_number=2,
                    description="Decision formation",
                    input_data={"pattern_match": True},
                    output_data=decision,
                    rule_applied="decision_rule",
                    confidence_delta=decision.get("confidence", 0.0) - 0.4,
                )
            )

        self.traces.append(trace)
        return trace

    def justify_action(
        self,
        action: str,
        expected_outcome: str,
        risks: list[str],
        benefits: list[str],
    ) -> Explanation:
        """
        Generate justification for taking an action.

        Args:
            action: The action to justify
            expected_outcome: What we expect to happen
            risks: Potential risks
            benefits: Expected benefits

        Returns:
            Action justification

        """
        benefit_text = "\n".join(f"  ✓ {b}" for b in benefits[:3])
        risk_text = "\n".join(f"  ⚠ {r}" for r in risks[:3])

        natural_language = f"""
Recommended Action: {action}

Expected Outcome:
  {expected_outcome}

Benefits:
{benefit_text}

Risks:
{risk_text}

Overall Assessment:
This action is recommended because the benefits outweigh the risks,
and the expected outcome aligns with architectural goals.
""".strip()

        explanation = Explanation(
            explanation_id=f"exp_act_{len(self.explanations)}",
            explanation_type=ExplanationType.ACTION,
            target=action,
            natural_language=natural_language,
            technical_details={
                "action": action,
                "outcome": expected_outcome,
                "risks": risks,
                "benefits": benefits,
            },
            confidence=0.8 if len(benefits) > len(risks) else 0.6,
        )

        self.explanations.append(explanation)
        return explanation

    def compare_alternatives(
        self,
        alternatives: list[dict[str, Any]],
        criteria: list[str],
    ) -> Explanation:
        """
        Compare multiple alternatives and explain the choice.

        Args:
            alternatives: List of alternative options
            criteria: Comparison criteria

        Returns:
            Comparison explanation

        """
        if not alternatives:
            return Explanation(
                explanation_id=f"exp_comp_{len(self.explanations)}",
                explanation_type=ExplanationType.COMPARISON,
                target="alternatives",
                natural_language="No alternatives to compare.",
                confidence=0.0,
            )

        # Find best alternative
        best = max(alternatives, key=lambda a: a.get("score", 0))

        comparison_text = f"""
Alternative Analysis ({len(alternatives)} options):

Selected: {best.get("name", "Option A")}
Score: {best.get("score", 0):.2f}

Comparison:
""".strip()

        for alt in alternatives:
            marker = "→" if alt == best else " "
            score = alt.get("score", 0)
            name = alt.get("name", "Unknown")
            comparison_text += f"\n  {marker} {name}: {score:.2f}"

        comparison_text += f"\n\nSelection based on: {', '.join(criteria[:3])}"

        explanation = Explanation(
            explanation_id=f"exp_comp_{len(self.explanations)}",
            explanation_type=ExplanationType.COMPARISON,
            target="alternative_selection",
            natural_language=comparison_text,
            technical_details={
                "alternatives": alternatives,
                "criteria": criteria,
                "selected": best,
            },
            confidence=best.get("score", 0.5),
        )

        self.explanations.append(explanation)
        return explanation

    def _explain_governance_decision(
        self, decision: dict[str, Any], context: dict[str, Any] | None
    ) -> str:
        """Explain a governance decision."""
        action = decision.get("action", "unknown")
        confidence = decision.get("confidence", 0.5)
        autonomy_level = decision.get("autonomy_level", "assisted")

        return f"""
Governance Decision: {action.upper()}

This decision was made at autonomy level '{autonomy_level}' with {confidence:.1%} confidence.

The system evaluated multiple factors including:
- Confidence threshold requirements
- Safety constraints
- Historical success rates
- Risk assessment

Based on this evaluation, the system decided to {action}.
""".strip()

    def _explain_prediction(self, decision: dict[str, Any], context: dict[str, Any] | None) -> str:
        """Explain a prediction."""
        pattern = decision.get("pattern", "unknown")
        confidence = decision.get("confidence", 0.5)
        severity = decision.get("severity", "medium")

        return f"""
Prediction: {pattern}

The system detected pattern '{pattern}' with {confidence:.1%} confidence.
Severity level: {severity.upper()}

This prediction is based on:
- Historical pattern recognition
- Trend analysis
- Correlation with known failure modes

Recommended action: Review the affected components and consider preventive measures.
""".strip()

    def _explain_repair(self, decision: dict[str, Any], context: dict[str, Any] | None) -> str:
        """Explain a repair decision."""
        pathology = decision.get("pathology_type", "unknown")
        suggestion = decision.get("suggestion", "No specific suggestion")
        is_safe = decision.get("is_safe_auto_fix", False)

        safety_text = "safe to auto-apply" if is_safe else "requires manual review"

        return f"""
Repair Recommendation: {pathology}

Suggested Fix: {suggestion}

Safety Assessment: This fix is {safety_text}.

The system identified this repair based on:
- Pattern matching against known pathologies
- Safety analysis of the proposed fix
- Risk assessment of the affected code

Apply this fix to resolve the {pathology} issue.
""".strip()

    def _explain_pathology(self, decision: dict[str, Any], context: dict[str, Any] | None) -> str:
        """Explain a pathology detection."""
        pathology = decision.get("pathology", "unknown")
        location = decision.get("location", "unknown location")
        severity = decision.get("severity", "medium")

        return f"""
Pathology Detected: {pathology}

Location: {location}
Severity: {severity.upper()}

The system detected this issue through:
- Static code analysis
- Invariant violation detection
- Semantic integrity checks

This pathology indicates a potential architectural issue that should be addressed.
""".strip()

    def _explain_generic(self, decision: dict[str, Any], context: dict[str, Any] | None) -> str:
        """Generic explanation for unknown decision types."""
        return f"""
Decision: {decision.get("id", "unknown")}

Type: {decision.get("type", "unknown")}
Confidence: {decision.get("confidence", 0):.1%}

This decision was made based on available evidence and system rules.
""".strip()

    def _gather_evidence(
        self, decision: dict[str, Any], context: dict[str, Any] | None
    ) -> list[Evidence]:
        """Gather evidence supporting a decision."""
        evidence = []

        # Add confidence as evidence
        confidence = decision.get("confidence", 0.5)
        if confidence > 0.8:
            strength = EvidenceStrength.STRONG
        elif confidence > 0.6:
            strength = EvidenceStrength.MODERATE
        else:
            strength = EvidenceStrength.WEAK

        evidence.append(
            Evidence(
                claim="decision_confidence",
                fact=f"Confidence score: {confidence:.2f}",
                strength=strength,
                source="decision_data",
                details={"score": confidence},
            )
        )

        # Add pattern evidence if present
        if "pattern" in decision:
            evidence.append(
                Evidence(
                    claim="pattern_match",
                    fact=f"Matched pattern: {decision['pattern']}",
                    strength=EvidenceStrength.MODERATE,
                    source="pattern_recognition",
                    details={"pattern": decision["pattern"]},
                )
            )

        # Add context evidence if present
        if context:
            evidence.append(
                Evidence(
                    claim="context_available",
                    fact=f"Context with {len(context)} fields",
                    strength=EvidenceStrength.MODERATE,
                    source="context_data",
                    details={"fields": list(context.keys())[:5]},
                )
            )

        return evidence

    def get_explanation_history(self) -> list[dict[str, Any]]:
        """Get history of all explanations."""
        return [e.to_dict() for e in self.explanations]

    def get_traces(self) -> list[dict[str, Any]]:
        """Get all reasoning traces."""
        return [t.to_dict() for t in self.traces]

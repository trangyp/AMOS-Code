"""
Meta-Cognitive Reflection Engine.

Enables the system to reflect on its own decision-making,
learn from experience, and continuously improve.

Provides:
- Decision pattern analysis
- Failure pattern detection and avoidance
- Performance-based parameter adaptation
- Self-improvement playbook generation
- Meta-cognitive reflection

Mathematical Foundation:
- Reflection: M_{t+1} = Reflect(M_t, Error_t, Outcome_t)
- Adaptation: θ_{t+1} = θ_t + η · ∇Performance
- Learning: Experience → Insights → Improved Decisions
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from enum import Enum
from pathlib import Path
from typing import Any


class ReflectionType(Enum):
    """Types of meta-cognitive reflection."""

    DECISION_PATTERN = "decision_pattern"  # Analyze decision patterns
    FAILURE_LEARNING = "failure_learning"  # Learn from failures
    PERFORMANCE = "performance"  # Reflect on performance
    PARAMETER_ADAPTATION = "parameter_adaptation"  # Adapt parameters
    PLAYBOOK_GENERATION = "playbook_generation"  # Generate improvement guide


class InsightSeverity(Enum):
    """Severity of meta-cognitive insights."""

    CRITICAL = "critical"  # Major issue requiring immediate action
    HIGH = "high"  # Significant improvement opportunity
    MEDIUM = "medium"  # Moderate improvement potential
    LOW = "low"  # Minor refinement possible
    INFO = "info"  # Informational observation


@dataclass
class DecisionRecord:
    """Record of a decision for pattern analysis."""

    decision_id: str
    timestamp: str
    decision_type: str
    context: dict[str, Any]
    outcome: dict[str, Any]
    confidence: float
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FailurePattern:
    """Detected failure pattern."""

    pattern_id: str
    failure_type: str
    signature: str
    occurrences: int
    contexts: list[dict[str, Any]]
    first_seen: str
    last_seen: str
    severity: InsightSeverity


@dataclass
class MetaInsight:
    """Insight from meta-cognitive reflection."""

    insight_id: str
    reflection_type: ReflectionType
    severity: InsightSeverity
    insight: str
    evidence: list[str]
    recommendation: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "insight_id": self.insight_id,
            "type": self.reflection_type.value,
            "severity": self.severity.value,
            "insight": self.insight,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp,
        }


@dataclass
class AdaptedParameter:
    """Parameter that has been adapted."""

    name: str
    initial_value: float
    current_value: float
    update_count: int
    last_update: str
    update_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "initial": round(self.initial_value, 3),
            "current": round(self.current_value, 3),
            "updates": self.update_count,
            "change": round(self.current_value - self.initial_value, 3),
            "change_percent": round(
                ((self.current_value - self.initial_value) / (self.initial_value + 0.001)) * 100,
                1,
            ),
        }


@dataclass
class ReflectionResult:
    """Result of meta-cognitive reflection."""

    reflection_id: str
    timestamp: str
    insights: list[MetaInsight]
    adapted_parameters: list[AdaptedParameter]
    failure_patterns_detected: int
    learning_applied: bool
    playbook_generated: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "reflection_id": self.reflection_id,
            "timestamp": self.timestamp,
            "insights": [i.to_dict() for i in self.insights],
            "adapted_parameters": [p.to_dict() for p in self.adapted_parameters],
            "failure_patterns": self.failure_patterns_detected,
            "learning_applied": self.learning_applied,
            "playbook_generated": self.playbook_generated,
        }


class MetaCognitiveReflectionEngine:
    """
    Engine for meta-cognitive reflection and self-improvement.

    Enables the system to:
    - Reflect on its own decisions
    - Learn from failures
    - Adapt parameters based on performance
    - Generate self-improvement playbooks
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path)
        self.decision_history: list[DecisionRecord] = []
        self.failure_patterns: dict[str, FailurePattern] = {}
        self.parameters: dict[str, AdaptedParameter] = {}
        self.insights: list[MetaInsight] = []
        self.reflections: list[ReflectionResult] = []

        # Default parameters for adaptation
        self._initialize_parameters()

    def _initialize_parameters(self) -> None:
        """Initialize default adaptive parameters."""
        default_params = {
            "confidence_threshold": 0.75,
            "risk_tolerance": 0.3,
            "exploration_rate": 0.2,
            "branch_count": 3.0,
            "attention_noise": 0.1,
            "learning_rate": 0.1,
        }

        for name, value in default_params.items():
            self.parameters[name] = AdaptedParameter(
                name=name,
                initial_value=value,
                current_value=value,
                update_count=0,
                last_update=datetime.now(timezone.utc).isoformat(),
            )

    def record_decision(
        self,
        decision_type: str,
        context: dict[str, Any],
        outcome: dict[str, Any],
        confidence: float,
        success: bool,
    ) -> DecisionRecord:
        """
        Record a decision for future reflection.

        Args:
            decision_type: Type of decision made
            context: Decision context
            outcome: Actual outcome
            confidence: Confidence at decision time
            success: Whether decision led to success

        Returns:
            Recorded decision

        """
        record = DecisionRecord(
            decision_id=f"dec_{len(self.decision_history)}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision_type=decision_type,
            context=context,
            outcome=outcome,
            confidence=confidence,
            success=success,
        )

        self.decision_history.append(record)

        # Keep history manageable
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)

        return record

    def record_failure(
        self,
        failure_type: str,
        context: dict[str, Any],
        action_taken: str,
        consequence: str,
    ) -> FailurePattern:
        """
        Record a failure for pattern detection.

        Args:
            failure_type: Type of failure
            context: Failure context
            action_taken: What action led to failure
            consequence: Result of failure

        Returns:
            Detected pattern if it's a repeat

        """
        # Generate signature
        signature = self._extract_signature(failure_type, context)

        now = datetime.now(timezone.utc).isoformat()

        if signature in self.failure_patterns:
            pattern = self.failure_patterns[signature]
            pattern.occurrences += 1
            pattern.contexts.append(context)
            pattern.last_seen = now

            # Update severity based on frequency
            if pattern.occurrences >= 5:
                pattern.severity = InsightSeverity.CRITICAL
            elif pattern.occurrences >= 3:
                pattern.severity = InsightSeverity.HIGH
        else:
            self.failure_patterns[signature] = FailurePattern(
                pattern_id=f"fp_{len(self.failure_patterns)}",
                failure_type=failure_type,
                signature=signature,
                occurrences=1,
                contexts=[context],
                first_seen=now,
                last_seen=now,
                severity=InsightSeverity.MEDIUM,
            )

        return self.failure_patterns.get(signature)

    def _extract_signature(self, failure_type: str, context: dict[str, Any]) -> str:
        """Extract failure signature from context."""
        keys = sorted(context.keys())[:3]
        values = [str(context[k])[:20] for k in keys if k in context]
        return f"{failure_type}:{':'.join(values)}"

    def should_avoid(self, context: dict[str, Any], action: str) -> Tuple[bool, str]:
        """
        Check if an action should be avoided based on past failures.

        Args:
            context: Current context
            action: Proposed action

        Returns:
            (should_avoid, reason)

        """
        test_sig = self._extract_signature("any", context)

        for pattern in self.failure_patterns.values():
            if pattern.occurrences >= 2 and self._signatures_similar(test_sig, pattern.signature):
                return (
                    True,
                    f"Similar context led to {pattern.occurrences} previous {pattern.failure_type} failures",
                )

        return False, ""

    def _signatures_similar(self, sig1: str, sig2: str) -> bool:
        """Check if two signatures are similar."""
        parts1 = set(sig1.split(":"))
        parts2 = set(sig2.split(":"))
        overlap = len(parts1 & parts2)
        return overlap >= 2

    def adapt_parameter(self, name: str, performance_delta: float) -> AdaptedParameter:
        """
        Adapt a parameter based on performance feedback.

        Args:
            name: Parameter name
            performance_delta: Performance change (positive = improvement)

        Returns:
            Updated parameter

        """
        if name not in self.parameters:
            return None

        param = self.parameters[name]
        learning_rate = self.parameters.get(
            "learning_rate", AdaptedParameter("lr", 0.1, 0.1, 0, "")
        ).current_value

        # Compute gradient direction
        gradient = 1.0 if performance_delta > 0 else -1.0

        # Apply update: θ_{t+1} = θ_t + η · gradient
        update = learning_rate * gradient
        param.current_value += update

        # Keep within bounds [0, 1]
        param.current_value = max(0.0, min(1.0, param.current_value))

        param.update_count += 1
        param.last_update = datetime.now(timezone.utc).isoformat()
        param.update_history.append(
            {
                "timestamp": param.last_update,
                "delta": performance_delta,
                "update": update,
                "new_value": param.current_value,
            }
        )

        return param

    def reflect(self) -> ReflectionResult:
        """
        Perform comprehensive meta-cognitive reflection.

        Analyzes decision history, detects patterns,
        generates insights, and adapts parameters.

        Returns:
            Reflection result with insights and adaptations

        """
        reflection_id = f"refl_{len(self.reflections)}"
        timestamp = datetime.now(timezone.utc).isoformat()

        insights: list[MetaInsight] = []
        adapted_params: list[AdaptedParameter] = []

        # 1. Analyze decision patterns
        decision_insights = self._analyze_decision_patterns()
        insights.extend(decision_insights)

        # 2. Detect failure patterns
        failure_count = len([p for p in self.failure_patterns.values() if p.occurrences >= 2])

        # 3. Analyze performance trends
        performance_insights = self._analyze_performance()
        insights.extend(performance_insights)

        # 4. Adapt parameters based on recent performance
        if self.decision_history:
            recent_decisions = self.decision_history[-10:]
            success_rate = sum(1 for d in recent_decisions if d.success) / len(recent_decisions)

            # Adapt confidence threshold
            if success_rate < 0.6:
                param = self.adapt_parameter("confidence_threshold", -0.2)
                if param:
                    adapted_params.append(param)
                    insights.append(
                        MetaInsight(
                            insight_id=f"ins_{len(insights)}",
                            reflection_type=ReflectionType.PARAMETER_ADAPTATION,
                            severity=InsightSeverity.HIGH,
                            insight=f"Low success rate ({success_rate:.1%}) - raising confidence threshold",
                            evidence=[
                                f"Recent success rate: {success_rate:.1%}",
                                f"Threshold adapted to {param.current_value:.2f}",
                            ],
                            recommendation="Continue monitoring success rate",
                            confidence=0.85,
                        )
                    )
            elif success_rate > 0.9:
                param = self.adapt_parameter("confidence_threshold", 0.1)
                if param:
                    adapted_params.append(param)
                    insights.append(
                        MetaInsight(
                            insight_id=f"ins_{len(insights)}",
                            reflection_type=ReflectionType.PARAMETER_ADAPTATION,
                            severity=InsightSeverity.LOW,
                            insight=f"High success rate ({success_rate:.1%}) - can be slightly more aggressive",
                            evidence=[f"Recent success rate: {success_rate:.1%}"],
                            recommendation="Consider increasing automation level",
                            confidence=0.8,
                        )
                    )

        # 5. Generate playbook
        playbook_generated = self._generate_playbook(insights)

        result = ReflectionResult(
            reflection_id=reflection_id,
            timestamp=timestamp,
            insights=insights,
            adapted_parameters=adapted_params,
            failure_patterns_detected=failure_count,
            learning_applied=len(adapted_params) > 0 or len(insights) > 0,
            playbook_generated=playbook_generated,
        )

        self.reflections.append(result)
        return result

    def _analyze_decision_patterns(self) -> list[MetaInsight]:
        """Analyze patterns in decision history."""
        insights = []

        if len(self.decision_history) < 5:
            return insights

        # Analyze decision type distribution
        type_counts: dict[str, int] = defaultdict(int)
        for decision in self.decision_history:
            type_counts[decision.decision_type] += 1

        # Find dominant type
        dominant_type = max(type_counts.keys(), key=lambda k: type_counts[k])
        dominant_ratio = type_counts[dominant_type] / len(self.decision_history)

        if dominant_ratio > 0.7:
            insights.append(
                MetaInsight(
                    insight_id=f"ins_{len(insights)}",
                    reflection_type=ReflectionType.DECISION_PATTERN,
                    severity=InsightSeverity.MEDIUM,
                    insight=f"Heavy reliance on '{dominant_type}' decisions ({dominant_ratio:.0%})",
                    evidence=[
                        f"{type_counts[dominant_type]} out of {len(self.decision_history)} decisions"
                    ],
                    recommendation="Consider diversifying decision strategies",
                    confidence=0.75,
                )
            )

        # Analyze confidence vs success correlation
        high_conf_success = [d.success for d in self.decision_history if d.confidence >= 0.8]
        if high_conf_success:
            high_conf_rate = sum(high_conf_success) / len(high_conf_success)
            if high_conf_rate < 0.7:
                insights.append(
                    MetaInsight(
                        insight_id=f"ins_{len(insights)}",
                        reflection_type=ReflectionType.DECISION_PATTERN,
                        severity=InsightSeverity.HIGH,
                        insight="High confidence decisions have low success rate - confidence calibration needed",
                        evidence=[
                            f"High confidence success rate: {high_conf_rate:.1%}",
                            f"Expected: >80%, Actual: {high_conf_rate:.1%}",
                        ],
                        recommendation="Recalibrate confidence estimation",
                        confidence=0.9,
                    )
                )

        return insights

    def _analyze_performance(self) -> list[MetaInsight]:
        """Analyze performance trends."""
        insights = []

        if len(self.decision_history) < 10:
            return insights

        # Compare first half vs second half
        mid = len(self.decision_history) // 2
        first_half = self.decision_history[:mid]
        second_half = self.decision_history[mid:]

        first_success = sum(1 for d in first_half if d.success) / len(first_half)
        second_success = sum(1 for d in second_half if d.success) / len(second_half)

        improvement = second_success - first_success

        if improvement > 0.2:
            insights.append(
                MetaInsight(
                    insight_id=f"ins_{len(insights)}",
                    reflection_type=ReflectionType.PERFORMANCE,
                    severity=InsightSeverity.LOW,
                    insight=f"Significant performance improvement (+{improvement:.0%})",
                    evidence=[
                        f"First half success: {first_success:.1%}",
                        f"Second half success: {second_success:.1%}",
                    ],
                    recommendation="Current approach is working - maintain",
                    confidence=0.85,
                )
            )
        elif improvement < -0.1:
            insights.append(
                MetaInsight(
                    insight_id=f"ins_{len(insights)}",
                    reflection_type=ReflectionType.PERFORMANCE,
                    severity=InsightSeverity.HIGH,
                    insight=f"Performance degradation detected ({improvement:.0%})",
                    evidence=[
                        f"First half success: {first_success:.1%}",
                        f"Second half success: {second_success:.1%}",
                    ],
                    recommendation="Investigate causes and adjust strategy",
                    confidence=0.9,
                )
            )

        return insights

    def _generate_playbook(self, insights: list[MetaInsight]) -> bool:
        """Generate self-improvement playbook."""
        if not insights:
            return False

        playbook_path = self.repo_path / "META_COGNITIVE_PLAYBOOK.md"

        content = f"""# Meta-Cognitive Self-Improvement Playbook

Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
Based on: {len(self.decision_history)} decisions, {len(self.failure_patterns)} failure patterns

## Current Status

- Total Decisions: {len(self.decision_history)}
- Failure Patterns: {len(self.failure_patterns)}
- Meta-Insights: {len(insights)}
- Reflections: {len(self.reflections)}

## Key Insights

"""

        for insight in insights:
            content += f"""### {insight.insight_id}: {insight.reflection_type.value.replace("_", " ").title()}

**Severity:** {insight.severity.value.upper()}
**Confidence:** {insight.confidence:.0%}

**Insight:** {insight.insight}

**Evidence:**
"""
            for evidence in insight.evidence:
                content += f"- {evidence}\n"

            content += f"""
**Recommendation:** {insight.recommendation}

---

"""

        # Add parameter adaptations
        content += """## Adapted Parameters

| Parameter | Initial | Current | Change |
|-----------|---------|---------|--------|
"""
        for param in self.parameters.values():
            if param.update_count > 0:
                change = param.current_value - param.initial_value
                content += f"| {param.name} | {param.initial_value:.3f} | {param.current_value:.3f} | {change:+.3f} |\n"

        content += """
## Failure Patterns to Avoid

"""
        for pattern in sorted(
            self.failure_patterns.values(), key=lambda p: p.occurrences, reverse=True
        )[:5]:
            content += f"""### {pattern.pattern_id}: {pattern.failure_type}

- **Occurrences:** {pattern.occurrences}
- **Severity:** {pattern.severity.value}
- **First seen:** {pattern.first_seen}
- **Last seen:** {pattern.last_seen}
- **Signature:** `{pattern.signature}`

**Avoid this pattern by:**
- Checking for similar contexts
- Using alternative approaches
- Increasing validation

---

"""

        content += """## Improvement Strategies

1. **Regular Reflection** - Reflect after every 10 decisions
2. **Pattern Avoidance** - Check failure patterns before decisions
3. **Confidence Calibration** - Adjust confidence based on outcomes
4. **Parameter Adaptation** - Let the system tune itself
5. **Documentation** - Record decisions for pattern analysis

---

*Generated by Meta-Cognitive Reflection Engine*
"""

        try:
            playbook_path.write_text(content)
            return True
        except Exception:
            return False

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive meta-cognitive status."""
        if not self.decision_history:
            return {
                "status": "no_data",
                "message": "No decisions recorded yet",
            }

        recent = self.decision_history[-10:]
        success_rate = sum(1 for d in recent if d.success) / len(recent)

        return {
            "status": "active",
            "total_decisions": len(self.decision_history),
            "recent_success_rate": round(success_rate, 3),
            "failure_patterns": len(self.failure_patterns),
            "repeating_patterns": len(
                [p for p in self.failure_patterns.values() if p.occurrences >= 2]
            ),
            "adapted_parameters": len([p for p in self.parameters.values() if p.update_count > 0]),
            "total_reflections": len(self.reflections),
            "current_parameters": {
                name: round(p.current_value, 3) for name, p in self.parameters.items()
            },
        }

    def get_improvement_suggestions(self) -> list[str]:
        """Get improvement suggestions."""
        suggestions = []

        # Check for repeating failure patterns
        repeating = [p for p in self.failure_patterns.values() if p.occurrences >= 3]
        if repeating:
            top = repeating[0]
            suggestions.append(
                f"Address repeating failure pattern: {top.failure_type} ({top.occurrences} times)"
            )

        # Check confidence calibration
        if self.decision_history:
            high_conf = [d for d in self.decision_history if d.confidence >= 0.8]
            if high_conf:
                high_conf_success = sum(1 for d in high_conf if d.success) / len(high_conf)
                if high_conf_success < 0.7:
                    suggestions.append(
                        "Recalibrate confidence - high confidence doesn't match success rate"
                    )

        # Check parameter drift
        for param in self.parameters.values():
            if abs(param.current_value - param.initial_value) > 0.3:
                suggestions.append(f"Parameter '{param.name}' has drifted significantly - review")

        return suggestions

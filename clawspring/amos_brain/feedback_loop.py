"""AMOS Cognitive Feedback Loop - Learn from audit history."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .cognitive_audit import get_audit_trail


@dataclass
class RoutingInsight:
    """Insight derived from historical routing decisions."""

    pattern: str
    recommended_engines: List[str]
    avg_consensus_score: float
    violation_rate: float
    confidence: float


class CognitiveFeedbackLoop:
    """Analyzes audit history to improve routing decisions."""

    def __init__(self):
        self.audit = get_audit_trail()
        self._insights_cache: List[RoutingInsight] = []
        self._domain_preferences: Dict[str, list[str]] = {}

    def analyze_patterns(self) -> List[RoutingInsight]:
        """Analyze audit history for routing patterns."""
        stats = self.audit.get_statistics()
        if stats["total_entries"] < 3:
            return []  # Not enough data

        insights = []
        domains = stats.get("domains", {})

        for domain, count in domains.items():
            if count < 2:
                continue

            entries = self.audit.get_by_domain(domain)
            if not entries:
                continue

            # Find most successful engines for this domain
            engine_success = {}
            for entry in entries:
                for engine in entry.engines_selected:
                    if engine not in engine_success:
                        engine_success[engine] = {"uses": 0, "consensus": []}
                    engine_success[engine]["uses"] += 1
                    if entry.consensus_score:
                        engine_success[engine]["consensus"].append(entry.consensus_score)

            # Calculate success metrics
            best_engines = []
            for engine, data in engine_success.items():
                avg_consensus = (
                    sum(data["consensus"]) / len(data["consensus"]) if data["consensus"] else 0.5
                )
                if avg_consensus > 0.6:
                    best_engines.append((engine, avg_consensus, data["uses"]))

            best_engines.sort(key=lambda x: x[1], reverse=True)

            if best_engines:
                # Calculate violation rate for this domain
                violations = sum(1 for e in entries if e.violations_found)
                violation_rate = violations / len(entries)

                insight = RoutingInsight(
                    pattern=domain,
                    recommended_engines=[e[0] for e in best_engines[:3]],
                    avg_consensus_score=sum(e[1] for e in best_engines) / len(best_engines),
                    violation_rate=violation_rate,
                    confidence=min(len(entries) / 10, 0.95),  # Cap at 0.95
                )
                insights.append(insight)
                self._domain_preferences[domain] = insight.recommended_engines

        self._insights_cache = insights
        return insights

    def get_engine_recommendations(self, domain: str, base_engines: List[str]) -> List[str]:
        """Get engine recommendations based on historical success."""
        # Refresh insights if needed
        if self._insights_cache is None:
            self.analyze_patterns()

        # Check if we have domain-specific insights
        if domain in self._domain_preferences:
            historical = self._domain_preferences[domain]
            # Merge historical best with base recommendations
            merged = historical[:2] + [e for e in base_engines if e not in historical][:2]
            return merged[:4]  # Max 4 engines

        return base_engines

    def estimate_consensus_quality(self, domain: str, engines: List[str]) -> Tuple[float, str]:
        """Estimate expected consensus quality based on history."""
        entries = self.audit.get_by_domain(domain)
        if not entries:
            return 0.5, "No historical data"

        # Find similar engine combinations
        matching = []
        for entry in entries:
            overlap = set(entry.engines_selected) & set(engines)
            if len(overlap) >= min(len(engines), 2):
                if entry.consensus_score:
                    matching.append(entry.consensus_score)

        if matching:
            avg = sum(matching) / len(matching)
            return avg, f"Based on {len(matching)} similar decisions"

        return 0.5, "No matching engine combinations"

    def get_similar_task_advice(self, task: str) -> Dict[str, Any]:
        """Get advice from similar historical tasks."""
        similar = self.audit.find_similar(task, threshold=0.5)
        if not similar:
            return None

        best = similar[0]
        advice = {
            "similar_task_preview": best.task_preview,
            "previously_used_engines": best.engines_selected,
            "previous_consensus": best.consensus_score,
            "previous_violations": best.violations_found,
            "recommendation": best.final_recommendation,
        }

        # Add warning if previous had violations
        if best.violations_found:
            advice["warning"] = "Similar task had law violations - review carefully"

        return advice

    def generate_feedback_report(self) -> str:
        """Generate feedback analysis report."""
        stats = self.audit.get_statistics()
        insights = self.analyze_patterns()

        lines = [
            "# AMOS Cognitive Feedback Report",
            "",
            f"Based on {stats.get('total_entries', 0)} historical decisions",
            "",
            "## Derived Insights",
        ]

        if not insights:
            lines.append("*Insufficient data for insights (need 3+ decisions per domain)*")
        else:
            for insight in insights:
                lines.extend(
                    [
                        f"\n### Domain: {insight.pattern}",
                        f"- Confidence: {insight.confidence:.0%}",
                        f"- Recommended engines: {', '.join(insight.recommended_engines)}",
                        f"- Avg consensus score: {insight.avg_consensus_score:.0%}",
                        f"- Violation rate: {insight.violation_rate:.1%}",
                    ]
                )

        lines.extend(
            [
                "",
                "## Recommendations",
            ]
        )

        if insights:
            lines.append("Use historical engine preferences for domain-specific routing")
        else:
            lines.append("Continue collecting decisions to build routing insights")

        return "\n".join(lines)


# Singleton instance
_feedback_loop: Optional[CognitiveFeedbackLoop] = None


def get_feedback_loop() -> CognitiveFeedbackLoop:
    """Get or create the singleton feedback loop."""
    global _feedback_loop
    if _feedback_loop is None:
        _feedback_loop = CognitiveFeedbackLoop()
    return _feedback_loop


def get_enhanced_engines(domain: str, base_engines: List[str]) -> List[str]:
    """Convenience function to get history-enhanced engine list."""
    loop = get_feedback_loop()
    return loop.get_engine_recommendations(domain, base_engines)


def get_task_advice(task: str) -> Dict[str, Any]:
    """Convenience function to get advice for a task."""
    loop = get_feedback_loop()
    return loop.get_similar_task_advice(task)


if __name__ == "__main__":
    # Test feedback loop
    print("=" * 60)
    print("AMOS Cognitive Feedback Loop - Test")
    print("=" * 60)

    loop = get_feedback_loop()

    # First, ensure we have some audit data
    from .cognitive_audit import record_cognitive_decision

    # Add sample entries if needed
    audit = get_audit_trail()
    stats = audit.get_statistics()

    if stats["total_entries"] < 5:
        print("\nAdding sample audit entries...")
        for i in range(5):
            record_cognitive_decision(
                task=f"Sample security task {i}",
                domain="security",
                risk_level="high",
                engines=["AMOS_Strategy_Game_Engine", "AMOS_Deterministic_Logic_And_Law_Engine"],
                consensus_score=0.8 + (i * 0.02),
                laws=["RULE_OF_2"],
                violations=[],
                exec_time_ms=15.0,
                recommendation="Proceed with strategy engine",
            )

    print("\n" + loop.generate_feedback_report())

    # Test engine enhancement
    print("\n## Engine Enhancement Test")
    base = ["AMOS_Engineering_And_Mathematics_Engine"]
    enhanced = get_enhanced_engines("security", base)
    print(f"Base: {base}")
    print(f"Enhanced: {enhanced}")

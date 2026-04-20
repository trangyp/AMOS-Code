"""AMOS Brain Dashboard - Analytics and reporting for reasoning patterns."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
UTC = timezone.utc

# Python 3.9 compatibility - UTC is only in 3.11+
from typing import Any, Optional

from amos_brain import get_amos_integration
from amos_brain.memory import BrainMemory, get_brain_memory


def _coerce_confidence(value: object) -> float:
    """Coerce confidence value to float 0-1 range."""
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    mapping = {"low": 0.33, "medium": 0.66, "high": 0.9}
    return mapping.get(str(value).lower(), 0.0)


class BrainDashboard:
    """Generates analytics and reports on brain reasoning patterns.

    Provides:
    - Decision trend analysis
    - Law compliance tracking (L2, L3)
    - Domain usage patterns
    - Confidence score trends
    - Reasoning pattern insights
    """

    def __init__(self, memory: Optional[BrainMemory] = None):
        self.memory = memory or get_brain_memory()
        self._amos = None

    @property
    def amos(self):
        """Lazy-load AMOS integration to prevent blocking during init."""
        if self._amos is None:
            self._amos = get_amos_integration()
        return self._amos

    def generate_report(self, days: int = 30, include_charts: bool = True) -> dict[str, Any]:
        """Generate comprehensive reasoning analytics report.

        Args:
            days: Number of days to analyze
            include_charts: Whether to include ASCII chart data

        Returns:
            Report dictionary with all analytics
        """
        # Get all history
        history = self.memory.get_reasoning_history(limit=1000)

        # Filter by date if needed
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent = []
        for h in history:
            ts = h.get("timestamp")
            if not ts:
                continue
            try:
                if datetime.fromisoformat(ts) > cutoff:
                    recent.append(h)
            except ValueError:
                continue

        return {
            "period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": self._generate_summary(recent),
            "compliance_trends": self._analyze_compliance(recent),
            "confidence_trends": self._analyze_confidence(recent),
            "domain_patterns": self._analyze_domains(recent),
            "decision_velocity": self._analyze_velocity(recent),
            "charts": self._generate_charts(recent) if include_charts else None,
            "insights": self._generate_insights(recent),
        }

    def _generate_summary(self, history: list[dict]) -> dict[str, Any]:
        """Generate summary statistics."""
        total = len(history)
        if total == 0:
            return {"total_decisions": 0, "message": "No reasoning data available"}

        with_rule2 = sum(1 for h in history if h.get("rule_of_two_applied"))
        with_rule4 = sum(1 for h in history if h.get("rule_of_four_applied"))
        avg_confidence = (
            sum(
                _coerce_confidence(h.get("confidence_score", h.get("confidence", 0)))
                for h in history
            )
            / total
        )

        # Find most common tags
        tag_counts: dict[str, int] = defaultdict(int)
        for h in history:
            for tag in h.get("tags", []):
                tag_counts[tag] += 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_decisions": total,
            "with_rule_of_2": with_rule2,
            "with_rule_of_4": with_rule4,
            "l2_compliance_rate": with_rule2 / total,
            "l3_compliance_rate": with_rule4 / total,
            "average_confidence": avg_confidence,
            "top_tags": top_tags,
        }

    def _analyze_compliance(self, history: list[dict]) -> dict[str, Any]:
        """Analyze law compliance trends."""
        if not history:
            return {"trend": "insufficient_data"}

        # Group by time buckets (weekly)
        weekly: dict[str, dict] = defaultdict(lambda: {"total": 0, "r2": 0, "r4": 0})

        for h in history:
            ts = h.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                except ValueError:
                    continue
                iso_year, iso_week, _ = dt.isocalendar()
                week = f"{iso_year}-W{iso_week:02d}"
                weekly[week]["total"] += 1
                if h.get("rule_of_two_applied"):
                    weekly[week]["r2"] += 1
                if h.get("rule_of_four_applied"):
                    weekly[week]["r4"] += 1

        # Calculate trends
        sorted_weeks = sorted(weekly.keys())
        l2_trend = []
        l3_trend = []

        for week in sorted_weeks:
            data = weekly[week]
            l2_trend.append(
                {
                    "period": week,
                    "rate": data["r2"] / data["total"] if data["total"] > 0 else 0,
                    "count": data["total"],
                }
            )
            l3_trend.append(
                {
                    "period": week,
                    "rate": data["r4"] / data["total"] if data["total"] > 0 else 0,
                    "count": data["total"],
                }
            )

        # Determine trend direction
        if len(sorted_weeks) >= 2:
            recent_l2 = l2_trend[-1]["rate"] if l2_trend else 0
            older_l2 = l2_trend[0]["rate"] if l2_trend else 0
            l2_direction = (
                "improving"
                if recent_l2 > older_l2
                else "declining"
                if recent_l2 < older_l2
                else "stable"
            )

            recent_l3 = l3_trend[-1]["rate"] if l3_trend else 0
            older_l3 = l3_trend[0]["rate"] if l3_trend else 0
            l3_direction = (
                "improving"
                if recent_l3 > older_l3
                else "declining"
                if recent_l3 < older_l3
                else "stable"
            )
        else:
            l2_direction = "insufficient_data"
            l3_direction = "insufficient_data"

        return {
            "l2_trend": l2_direction,
            "l2_weekly": l2_trend,
            "l3_trend": l3_direction,
            "l3_weekly": l3_trend,
            "overall_l2": sum(h.get("rule_of_two_applied", 0) for h in history) / len(history)
            if history
            else 0,
            "overall_l3": sum(h.get("rule_of_four_applied", 0) for h in history) / len(history)
            if history
            else 0,
        }

    def _analyze_confidence(self, history: list[dict]) -> dict[str, Any]:
        """Analyze confidence score trends."""
        if not history:
            return {"trend": "insufficient_data"}

        scores = [
            _coerce_confidence(h.get("confidence_score", h.get("confidence", 0))) for h in history
        ]
        sorted_scores = sorted(scores)

        n = len(sorted_scores)
        mean = sum(scores) / n
        median = (
            sorted_scores[n // 2]
            if n % 2 == 1
            else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        )

        if n < 2:
            return {
                "trend": "insufficient_data",
                "mean": mean,
                "median": median,
                "min": min(scores),
                "max": max(scores),
                "first_half_avg": mean,
                "second_half_avg": mean,
            }

        # Trend: compare first half vs second half
        mid = n // 2
        first_half = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half = sum(scores[mid:]) / (n - mid) if (n - mid) > 0 else 0

        if second_half > first_half * 1.1:
            trend = "improving"
        elif second_half < first_half * 0.9:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "mean": mean,
            "median": median,
            "min": min(scores),
            "max": max(scores),
            "first_half_avg": first_half,
            "second_half_avg": second_half,
        }

    def _analyze_domains(self, history: list[dict]) -> dict[str, Any]:
        """Analyze which cognitive domains are most used."""
        # This would require tracking domain usage per reasoning
        # For now, analyze by tag patterns
        tag_domains: dict[str, int] = defaultdict(int)

        domain_keywords = {
            "architecture": ["tech_engineering", "design_language"],
            "strategy": ["strategy_game", "meta_logic"],
            "people": ["bio_neuro", "mind_behavior", "society_culture"],
            "finance": ["econ_finance"],
            "legal": ["org_law_policy"],
            "science": ["physics_cosmos", "bio_neuro"],
        }

        for h in history:
            for tag in h.get("tags", []):
                for domain, keywords in domain_keywords.items():
                    if any(kw in tag.lower() for kw in keywords):
                        tag_domains[domain] += 1

        sorted_domains = sorted(tag_domains.items(), key=lambda x: x[1], reverse=True)

        return {
            "domain_usage": sorted_domains,
            "primary_domain": sorted_domains[0][0] if sorted_domains else "unknown",
            "domain_diversity": len(tag_domains),
        }

    def _analyze_velocity(self, history: list[dict]) -> dict[str, Any]:
        """Analyze decision velocity (decisions per time period)."""
        if not history:
            return {"velocity": 0}

        # Group by day
        daily: dict[str, int] = defaultdict(int)
        for h in history:
            ts = h.get("timestamp", "")
            if ts:
                day = ts[:10]  # YYYY-MM-DD
                daily[day] += 1

        if not daily:
            return {"velocity": 0}

        sorted_days = sorted(daily.keys())
        total_days = (
            (datetime.fromisoformat(sorted_days[-1]) - datetime.fromisoformat(sorted_days[0])).days
            + 1
            if len(sorted_days) >= 2
            else 1
        )

        return {
            "total_decisions": len(history),
            "active_days": len(daily),
            "avg_per_day": len(history) / total_days if total_days > 0 else 0,
            "max_per_day": max(daily.values()),
            "peak_day": max(daily.items(), key=lambda x: x[1])[0] if daily else None,
        }

    def _generate_charts(self, history: list[dict]) -> dict[str, Any]:
        """Generate ASCII chart data for visualization."""
        if not history:
            return None

        # Confidence histogram (10 buckets)
        buckets = [0] * 10
        for h in history:
            score = _coerce_confidence(h.get("confidence_score", h.get("confidence", 0)))
            bucket = min(int(score * 10), 9)
            buckets[bucket] += 1

        # Generate ASCII bars
        max_count = max(buckets) if buckets else 1
        bars = []
        for i, count in enumerate(buckets):
            label = f"{i * 10}-{(i + 1) * 10}%"
            bar_len = int((count / max_count) * 40) if max_count > 0 else 0
            bar = "█" * bar_len
            bars.append(f"{label:8} | {bar} ({count})")

        return {
            "confidence_distribution": bars,
            "confidence_buckets": buckets,
        }

    def _generate_insights(self, history: list[dict]) -> list[str]:
        """Generate insights from the data."""
        insights = []

        if not history:
            insights.append(
                "No reasoning data available yet. Start using /decide to build history."
            )
            return insights

        # Compliance insights
        total = len(history)
        r2_rate = sum(h.get("rule_of_two_applied", 0) for h in history) / total
        r4_rate = sum(h.get("rule_of_four_applied", 0) for h in history) / total

        if r2_rate < 0.5:
            insights.append(
                f"⚠️ L2 (Rule of 2) compliance is {r2_rate:.0%} - consider using dual perspective analysis more often"
            )
        elif r2_rate > 0.9:
            insights.append(
                f"✓ Excellent L2 compliance at {r2_rate:.0%} - consistent dual perspective usage"
            )

        if r4_rate < 0.5:
            insights.append(
                f"⚠️ L3 (Rule of 4) compliance is {r4_rate:.0%} - four quadrant analysis underutilized"
            )
        elif r4_rate > 0.9:
            insights.append(
                f"✓ Strong L3 compliance at {r4_rate:.0%} - comprehensive quadrant coverage"
            )

        # Confidence insights
        scores = [
            _coerce_confidence(h.get("confidence_score", h.get("confidence", 0))) for h in history
        ]
        avg_conf = sum(scores) / len(scores)
        if avg_conf < 0.5:
            insights.append(
                f"📉 Average confidence is {avg_conf:.0%} - decisions may need more information"
            )
        elif avg_conf > 0.8:
            insights.append(f"📈 High average confidence at {avg_conf:.0%} - good data quality")

        # Velocity insights
        if total > 10:
            insights.append(
                f"📊 {total} decisions analyzed - sufficient data for pattern recognition"
            )

        # Domain insights
        tag_counts: dict[str, int] = defaultdict(int)
        for h in history:
            for tag in h.get("tags", []):
                tag_counts[tag] += 1

        if tag_counts:
            top_tag = max(tag_counts.items(), key=lambda x: x[1])
            insights.append(
                f"🏷️ Most frequent tag: '{top_tag[0]}' ({top_tag[1]} uses) - primary decision domain"
            )

        return insights


def print_report(report: dict[str, Any]) -> None:
    """Print formatted report to console."""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║           AMOS BRAIN REASONING DASHBOARD                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Summary
    summary = report.get("summary", {})
    print("📊 SUMMARY")
    print(f"   Period: {report.get('period_days', 30)} days")
    print(f"   Total Decisions: {summary.get('total_decisions', 0)}")
    print(f"   L2 (Rule of 2) Compliance: {summary.get('l2_compliance_rate', 0):.0%}")
    print(f"   L3 (Rule of 4) Compliance: {summary.get('l3_compliance_rate', 0):.0%}")
    print(f"   Average Confidence: {summary.get('average_confidence', 0):.0%}")
    print()

    # Compliance trends
    compliance = report.get("compliance_trends", {})
    print("📈 COMPLIANCE TRENDS")
    print(f"   L2 Trend: {compliance.get('l2_trend', 'N/A')}")
    print(f"   L3 Trend: {compliance.get('l3_trend', 'N/A')}")
    print()

    # Confidence trends
    confidence = report.get("confidence_trends", {})
    print("🎯 CONFIDENCE ANALYSIS")
    print(f"   Trend: {confidence.get('trend', 'N/A')}")
    print(f"   Mean: {confidence.get('mean', 0):.0%}")
    print(f"   Median: {confidence.get('median', 0):.0%}")
    print()

    # Velocity
    velocity = report.get("decision_velocity", {})
    print("⚡ DECISION VELOCITY")
    print(f"   Total: {velocity.get('total_decisions', 0)}")
    print(f"   Active Days: {velocity.get('active_days', 0)}")
    print(f"   Avg/Day: {velocity.get('avg_per_day', 0):.1f}")
    print()

    # Insights
    insights = report.get("insights", [])
    if insights:
        print("💡 INSIGHTS")
        for insight in insights:
            print(f"   {insight}")
        print()

    # Charts
    charts = report.get("charts")
    if charts:
        print("📊 CONFIDENCE DISTRIBUTION")
        for bar in charts.get("confidence_distribution", []):
            print(f"   {bar}")
        print()

    print(f"Report generated: {report.get('generated_at', 'unknown')[:16]}")
    print()


# Convenience functions
def generate_dashboard_report(days: int = 30) -> dict[str, Any]:
    """Generate dashboard report for given time period."""
    dashboard = BrainDashboard()
    return dashboard.generate_report(days=days)


def print_dashboard(days: int = 30) -> None:
    """Generate and print dashboard report."""
    report = generate_dashboard_report(days)
    print_report(report)

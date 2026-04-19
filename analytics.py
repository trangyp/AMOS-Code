"""Analytics and Reporting for AMOS Brain API

Provides usage analytics, trend analysis, and reporting.
"""

from datetime import datetime

from database import db
from typing import List


class Analytics:
    """Analytics engine for API usage data."""

    def __init__(self):
        self.db = db

    def get_dashboard_data(self) -> dict:
        """Get data for analytics dashboard."""
        # Get stats for different periods
        stats_24h = self.db.get_usage_stats(days=1)
        stats_7d = self.db.get_usage_stats(days=7)
        stats_30d = self.db.get_usage_stats(days=30)

        return {
            "periods": {"24h": stats_24h, "7d": stats_7d, "30d": stats_30d},
            "trends": self._calculate_trends(stats_24h, stats_7d, stats_30d),
            "generated_at": datetime.now().isoformat(),
        }

    def _calculate_trends(self, d1, d7, d30) -> dict:
        """Calculate usage trends."""
        daily_avg_7d = d7["total_requests"] / 7 if d7["total_requests"] > 0 else 0
        daily_avg_30d = d30["total_requests"] / 30 if d30["total_requests"] > 0 else 0

        trend = "increasing" if daily_avg_7d > daily_avg_30d else "decreasing"

        return {
            "daily_avg_7d": round(daily_avg_7d, 2),
            "daily_avg_30d": round(daily_avg_30d, 2),
            "trend": trend,
            "growth_rate": round((daily_avg_7d / daily_avg_30d - 1) * 100, 2)
            if daily_avg_30d > 0
            else 0,
        }

    def get_popular_queries(self, limit: int = 10) -> List[dict]:
        """Get most popular query types."""
        # Get recent query history
        queries = self.db.get_query_history(limit=1000)

        # Count by domain
        domain_counts = {}
        for q in queries:
            domain = q.get("domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Sort by count
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"domain": d, "count": c} for d, c in sorted_domains[:limit]]

    def get_performance_metrics(self) -> dict:
        """Get API performance metrics."""
        stats = self.db.get_usage_stats(days=7)

        return {
            "avg_response_time_ms": stats["avg_response_time_ms"],
            "success_rate": stats["success_rate_percent"],
            "total_requests": stats["total_requests"],
            "availability_percent": stats["success_rate_percent"],
            "grade": self._calculate_grade(stats["success_rate_percent"]),
        }

    def _calculate_grade(self, success_rate: float) -> str:
        """Calculate letter grade based on success rate."""
        if success_rate >= 99.9:
            return "A+"
        elif success_rate >= 99:
            return "A"
        elif success_rate >= 95:
            return "B"
        elif success_rate >= 90:
            return "C"
        else:
            return "D"

    def generate_report(self, days: int = 7) -> str:
        """Generate text report for specified period."""
        stats = self.db.get_usage_stats(days)

        report = f"""
AMOS Brain API - Usage Report
=============================
Period: Last {days} days
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Summary
-------
Total Requests: {stats["total_requests"]:,}
Success Rate: {stats["success_rate_percent"]:.2f}%
Avg Response Time: {stats["avg_response_time_ms"]:.2f}ms

Performance Grade: {self._calculate_grade(stats["success_rate_percent"])}

Top Query Domains
-----------------
"""

        popular = self.get_popular_queries(5)
        for i, p in enumerate(popular, 1):
            report += f"{i}. {p['domain']}: {p['count']} queries\n"

        return report


# Global analytics instance
analytics = Analytics()

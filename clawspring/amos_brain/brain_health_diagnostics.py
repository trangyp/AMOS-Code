from typing import Any, Dict, List, Optional

"""Brain-Powered Health Diagnostics

Intelligent health analysis and remediation using brain reasoning.
Based on research: Cognitive system monitoring with predictive healing.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

from amos_brain.integrated_brain_api import get_brain_api


@dataclass
class HealthDiagnostic:
    """Health diagnostic result from brain analysis."""

    component: str
    status: str  # healthy, degraded, critical
    diagnosis: str
    root_cause: str
    recommended_action: str
    urgency: str  # low, medium, high, immediate
    confidence: float
    estimated_recovery_time: str
    timestamp: str


class BrainHealthDiagnostics:
    """
    Brain-powered health diagnostics and remediation.

    Uses integrated brain to:
    - Analyze health check failures with reasoning
    - Identify root causes
    - Recommend remediation steps
    - Predict recovery times
    - Prioritize fixes by urgency
    """

    def __init__(
        self,
        health_check_fn: Optional[Callable] = None,
        remediation_fn: Optional[Callable] = None,
    ):
        self.brain = get_brain_api()
        self.health_check_fn = health_check_fn
        self.remediation_fn = remediation_fn
        self._diagnostic_history: List[HealthDiagnostic] = []
        self._component_history: Dict[str, list[dict[str, Any]]] = {}

    async def diagnose_component(
        self,
        component: str,
        health_data: Dict[str, Any],
    ) -> HealthDiagnostic:
        """
        Diagnose a component's health using brain reasoning.

        Args:
            component: Component name
            health_data: Health check data (status, metrics, errors)

        Returns:
            HealthDiagnostic with brain-generated analysis
        """
        # Build context for brain
        context = {
            "component": component,
            "health_data": health_data,
            "history": self._component_history.get(component, [])[-5:],
        }

        # Determine status
        status = health_data.get("status", "unknown")
        if status == "healthy":
            urgency = "low"
        elif status == "degraded":
            urgency = "medium"
        else:
            urgency = "high"

        # Use brain for diagnosis
        query = f"""Diagnose health issue for component '{component}':
Status: {status}
Metrics: {health_data.get("metrics", {})}
Errors: {health_data.get("errors", [])}

What is the likely root cause and recommended fix?"""

        result = await self.brain.process(query, mode="react", context=context)

        # Parse diagnosis
        diagnosis = result.response[:400]
        root_cause = self._extract_root_cause(result.response)
        recommended_action = self._extract_recommendation(result.response)

        # Estimate recovery
        recovery_time = self._estimate_recovery(component, status, result.response)

        diagnostic = HealthDiagnostic(
            component=component,
            status=status,
            diagnosis=diagnosis,
            root_cause=root_cause,
            recommended_action=recommended_action,
            urgency=urgency,
            confidence=result.confidence,
            estimated_recovery_time=recovery_time,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Store history
        self._diagnostic_history.append(diagnostic)
        if component not in self._component_history:
            self._component_history[component] = []
        self._component_history[component].append(
            {
                "timestamp": diagnostic.timestamp,
                "status": status,
                "diagnosis": diagnosis,
            }
        )

        return diagnostic

    async def analyze_system_health(
        self,
        all_health_data: Dict[str, dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze overall system health with brain reasoning.

        Args:
            all_health_data: Dict of component -> health data

        Returns:
            System-wide health analysis
        """
        # Count statuses
        healthy = sum(1 for d in all_health_data.values() if d.get("status") == "healthy")
        degraded = sum(1 for d in all_health_data.values() if d.get("status") == "degraded")
        critical = sum(
            1 for d in all_health_data.values() if d.get("status") not in ("healthy", "degraded")
        )

        context = {
            "total_components": len(all_health_data),
            "healthy": healthy,
            "degraded": degraded,
            "critical": critical,
            "component_statuses": {k: v.get("status") for k, v in all_health_data.items()},
        }

        query = f"""Analyze system health:
Total components: {len(all_health_data)}
Healthy: {healthy}
Degraded: {degraded}
Critical: {critical}

What is the overall system status and top priority actions?"""

        result = await self.brain.process(query, mode="reflect", context=context)

        # Prioritize components
        priorities = self._prioritize_components(all_health_data)

        return {
            "overall_status": "critical"
            if critical > 0
            else "degraded"
            if degraded > 0
            else "healthy",
            "system_analysis": result.response[:500],
            "component_count": len(all_health_data),
            "healthy_count": healthy,
            "degraded_count": degraded,
            "critical_count": critical,
            "prioritized_components": priorities,
            "confidence": result.confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def suggest_remediation(
        self,
        diagnostic: HealthDiagnostic,
    ) -> Dict[str, Any]:
        """
        Suggest specific remediation steps.

        Args:
            diagnostic: Health diagnostic to remediate

        Returns:
            Remediation plan
        """
        query = f"""Suggest remediation for:
Component: {diagnostic.component}
Issue: {diagnostic.diagnosis}
Root cause: {diagnostic.root_cause}
Urgency: {diagnostic.urgency}

Provide step-by-step remediation instructions."""

        result = await self.brain.process(
            query,
            mode="react",
            context={
                "component": diagnostic.component,
                "diagnosis": diagnostic.diagnosis,
            },
        )

        # Parse steps
        steps = self._parse_steps(result.response)

        return {
            "component": diagnostic.component,
            "steps": steps,
            "automated": len(steps) <= 3,  # Simple fixes can be automated
            "confidence": result.confidence,
            "estimated_time": diagnostic.estimated_recovery_time,
            "raw_analysis": result.response,
        }

    def _extract_root_cause(self, response: str) -> Optional[str]:
        """Extract root cause from brain response."""
        # Look for root cause indicators
        indicators = ["root cause:", "cause:", "due to", "because", "reason:"]
        lines = response.lower().split("\n")

        for line in lines:
            for indicator in indicators:
                if indicator in line:
                    # Return the sentence containing the indicator
                    start = line.find(indicator)
                    return line[start : start + 200].strip()

        return None

    def _extract_recommendation(self, response: str) -> str:
        """Extract recommendation from brain response."""
        # Look for recommendation indicators
        indicators = ["recommend", "should", "action:", "fix:", "step:", "try"]
        lines = response.split("\n")

        for line in lines:
            line_lower = line.lower()
            for indicator in indicators:
                if indicator in line_lower and len(line) > 20:
                    return line.strip()[:200]

        return "Review system logs and restart component"

    def _estimate_recovery(
        self,
        component: str,
        status: str,
        response: str,
    ) -> Optional[str]:
        """Estimate recovery time based on brain analysis."""
        # Look for time indicators
        if "immediate" in response.lower() or "now" in response.lower():
            return "< 1 minute"
        elif "minute" in response.lower():
            return "1-5 minutes"
        elif "hour" in response.lower():
            return "1-4 hours"
        elif "day" in response.lower():
            return "1-2 days"

        # Default based on status
        if status == "healthy":
            return "N/A"
        elif status == "degraded":
            return "5-15 minutes"
        else:
            return "15-60 minutes"

    def _prioritize_components(
        self,
        health_data: Dict[str, dict[str, Any]],
    ) -> List[dict[str, Any]]:
        """Prioritize components by urgency."""
        priority_order = {"critical": 0, "unhealthy": 1, "degraded": 2, "healthy": 3}

        sorted_components = sorted(
            health_data.items(),
            key=lambda x: priority_order.get(x[1].get("status"), 99),
        )

        return [
            {
                "component": name,
                "status": data.get("status"),
                "priority": i + 1,
            }
            for i, (name, data) in enumerate(sorted_components)
        ]

    def _parse_steps(self, response: str) -> List[str]:
        """Parse remediation steps from brain response."""
        lines = response.split("\n")
        steps = []

        for line in lines:
            line = line.strip()
            # Look for numbered or bulleted steps
            if line and (line[0].isdigit() or line.startswith(("-", "*"))):
                clean = line.lstrip("0123456789.-* ")
                if len(clean) > 10:
                    steps.append(clean[:200])

        return steps[:5]  # Limit to 5 steps

    def get_diagnostic_history(
        self,
        component: Optional[str] = None,
        limit: int = 50,
    ) -> List[HealthDiagnostic]:
        """Get diagnostic history."""
        diagnostics = self._diagnostic_history

        if component:
            diagnostics = [d for d in diagnostics if d.component == component]

        return diagnostics[-limit:]

    def get_common_issues(self) -> List[dict[str, Any]]:
        """Get commonly diagnosed issues."""
        from collections import Counter

        if not self._diagnostic_history:
            return []

        components = Counter(d.component for d in self._diagnostic_history)
        statuses = Counter(d.status for d in self._diagnostic_history)

        return [
            {
                "most_problematic_component": components.most_common(1)[0] if components else None,
                "status_distribution": dict(statuses),
                "total_diagnostics": len(self._diagnostic_history),
            }
        ]


# Global instance
_global_health_diagnostics: Optional[BrainHealthDiagnostics] = None


def get_brain_health_diagnostics() -> BrainHealthDiagnostics:
    """Get or create global brain health diagnostics."""
    global _global_health_diagnostics
    if _global_health_diagnostics is None:
        _global_health_diagnostics = BrainHealthDiagnostics()
    return _global_health_diagnostics


if __name__ == "__main__":

    async def test():
        diagnostics = get_brain_health_diagnostics()

        # Test component diagnosis
        health_data = {
            "status": "degraded",
            "metrics": {"cpu": 85, "memory": 92, "latency": 1200},
            "errors": ["High memory usage", "Slow response times"],
        }

        diagnostic = await diagnostics.diagnose_component("api_gateway", health_data)

        print(f"Component: {diagnostic.component}")
        print(f"Status: {diagnostic.status}")
        print(f"Urgency: {diagnostic.urgency}")
        print(f"Confidence: {diagnostic.confidence:.2f}")
        print(f"Diagnosis: {diagnostic.diagnosis[:100]}...")
        print(f"Recommended Action: {diagnostic.recommended_action[:100]}...")

        # Test system analysis
        all_health = {
            "api_gateway": {"status": "degraded"},
            "database": {"status": "healthy"},
            "cache": {"status": "healthy"},
            "llm_provider": {"status": "critical"},
        }

        analysis = await diagnostics.analyze_system_health(all_health)
        print(f"\nSystem Status: {analysis['overall_status']}")
        print(f"Analysis: {analysis['system_analysis'][:100]}...")
        print(f"Priorities: {analysis['prioritized_components'][:2]}")

    asyncio.run(test())

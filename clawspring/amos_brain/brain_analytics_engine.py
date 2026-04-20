from __future__ import annotations

from typing import Any

"""Brain-Powered Analytics Engine

Integrates brain processing with analytics for intelligent insights.
Based on research: Cognitive analytics with agent-based reasoning.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc

UTC = timezone.utc
from amos_brain.integrated_brain_api import get_brain_api


@dataclass
class AnalyticsInsight:
    """Intelligent analytics insight from brain processing."""

    metric_name: str
    insight_type: str  # trend, anomaly, prediction, recommendation
    description: str
    confidence: float
    severity: str  # low, medium, high, critical
    suggested_action: str | None
    raw_data: dict[str, Any]
    timestamp: str


class BrainAnalyticsEngine:
    """Brain-powered analytics with cognitive reasoning.

    Uses integrated brain to:
    - Detect anomalies with reasoning
    - Predict trends with reflection
    - Generate actionable recommendations
    - Explain metric changes
    """

    def __init__(self):
        self.brain = get_brain_api()
        self._insight_history: list[AnalyticsInsight] = []
        self._metric_context: dict[str, dict[str, Any]] = {}

    async def analyze_metric(
        self,
        metric_name: str,
        current_value: float,
        historical_values: list[float],
        threshold: float | None = None,
    ) -> AnalyticsInsight:
        """Analyze a metric using brain-powered reasoning.

        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            historical_values: Historical values for context
            threshold: Alert threshold if any

        Returns:
            AnalyticsInsight with brain-generated analysis

        """
        # Build context for brain
        context = {
            "metric_name": metric_name,
            "current_value": current_value,
            "historical_mean": sum(historical_values) / len(historical_values)
            if historical_values
            else 0,
            "historical_max": max(historical_values) if historical_values else current_value,
            "historical_min": min(historical_values) if historical_values else current_value,
            "threshold": threshold,
            "data_points": len(historical_values),
        }

        # Determine severity
        severity = "low"
        if threshold and current_value > threshold:
            severity = "critical" if current_value > threshold * 1.5 else "high"
        elif historical_values:
            mean = context["historical_mean"]
            if abs(current_value - mean) > mean * 0.5:
                severity = "medium"

        # Use brain for intelligent analysis
        query = f"""Analyze metric '{metric_name}':
Current: {current_value}
Threshold: {threshold}
Severity: {severity}

What does this indicate and what action should be taken?"""

        result = await self.brain.process(query, mode="auto", context=context)

        # Parse insight type from response
        insight_type = self._classify_insight(result.response, current_value, threshold)

        # Extract suggested action
        suggested_action = self._extract_action(result.response)

        insight = AnalyticsInsight(
            metric_name=metric_name,
            insight_type=insight_type,
            description=result.response[:500],
            confidence=result.confidence,
            severity=severity,
            suggested_action=suggested_action,
            raw_data={
                "current_value": current_value,
                "historical_values": historical_values[-10:],  # Last 10
                "threshold": threshold,
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._insight_history.append(insight)

        return insight

    async def predict_trend(
        self,
        metric_name: str,
        historical_values: list[float],
        forecast_horizon: int = 10,
    ) -> dict[str, Any]:
        """Predict future trend using brain reasoning.

        Args:
            metric_name: Name of the metric
            historical_values: Historical time-series data
            forecast_horizon: Number of future points to predict

        Returns:
            Prediction with confidence and reasoning

        """
        if len(historical_values) < 3:
            return {
                "predicted_values": [historical_values[-1]] * forecast_horizon
                if historical_values
                else [0] * forecast_horizon,
                "confidence": 0.0,
                "reasoning": "Insufficient data for prediction",
                "trend": "unknown",
            }

        # Calculate basic trend
        recent = historical_values[-5:] if len(historical_values) >= 5 else historical_values
        trend = "stable"
        if len(recent) >= 2:
            diff = recent[-1] - recent[0]
            if diff > 0:
                trend = "increasing"
            elif diff < 0:
                trend = "decreasing"

        # Use brain for intelligent prediction
        context = {
            "metric_name": metric_name,
            "historical_values": historical_values,
            "trend": trend,
            "forecast_horizon": forecast_horizon,
        }

        query = f"""Predict trend for '{metric_name}':
Historical data points: {len(historical_values)}
Recent trend: {trend}
Forecast horizon: {forecast_horizon}

What will the likely values be and why?"""

        result = await self.brain.process(query, mode="reflect", context=context)

        # Generate simple prediction based on trend
        last_value = historical_values[-1]
        if trend == "increasing":
            predicted = [last_value * (1 + 0.05 * i) for i in range(1, forecast_horizon + 1)]
        elif trend == "decreasing":
            predicted = [last_value * (1 - 0.05 * i) for i in range(1, forecast_horizon + 1)]
        else:
            predicted = [last_value] * forecast_horizon

        return {
            "predicted_values": predicted,
            "confidence": result.confidence,
            "reasoning": result.response[:300],
            "trend": trend,
            "components_used": result.components_used,
        }

    async def generate_recommendations(
        self,
        metrics_summary: dict[str, float],
        system_health: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate intelligent recommendations using brain.

        Args:
            metrics_summary: Key metrics and their values
            system_health: System health indicators

        Returns:
            List of prioritized recommendations

        """
        context = {
            "metrics": metrics_summary,
            "health": system_health,
        }

        query = f"""Given system metrics:
{json.dumps(metrics_summary, indent=2)}

And health status:
{json.dumps(system_health, indent=2)}

What are the top 3 recommendations to improve system performance?"""

        result = await self.brain.process(query, mode="react", context=context)

        # Parse recommendations from response
        recommendations = self._parse_recommendations(result.response)

        return [
            {
                "priority": i + 1,
                "description": rec,
                "confidence": result.confidence,
                "brain_mode": result.mode,
            }
            for i, rec in enumerate(recommendations[:3])
        ]

    def _classify_insight(
        self,
        response: str,
        current_value: float,
        threshold: float | None,
    ) -> str:
        """Classify insight type from brain response."""
        response_lower = response.lower()

        if threshold and current_value > threshold:
            return "anomaly"
        elif "predict" in response_lower or "will" in response_lower:
            return "prediction"
        elif "recommend" in response_lower or "should" in response_lower:
            return "recommendation"
        elif (
            "trend" in response_lower
            or "increasing" in response_lower
            or "decreasing" in response_lower
        ):
            return "trend"
        else:
            return "observation"

    def _extract_action(self, response: str) -> str | None:
        """Extract suggested action from brain response."""
        # Look for action keywords
        action_indicators = [
            "should",
            "recommend",
            "action:",
            "step:",
            "investigate",
            "check",
            "monitor",
        ]

        sentences = response.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in action_indicators):
                return sentence.strip()

        return None

    def _parse_recommendations(self, response: str) -> list[str]:
        """Parse recommendations from brain response."""
        lines = response.split("\n")
        recommendations = []

        for line in lines:
            line = line.strip()
            # Look for numbered items or bullet points
            if line and (line[0].isdigit() or line.startswith(("-", "*"))):
                # Clean up the line
                clean = line.lstrip("0123456789.-* ")
                if len(clean) > 10:
                    recommendations.append(clean)

        return recommendations

    def get_insight_history(
        self,
        metric_name: str | None = None,
        limit: int = 100,
    ) -> list[AnalyticsInsight]:
        """Get historical insights."""
        insights = self._insight_history

        if metric_name:
            insights = [i for i in insights if i.metric_name == metric_name]

        return insights[-limit:]


# Global instance
_global_analytics_engine: BrainAnalyticsEngine | None = None


def get_brain_analytics() -> BrainAnalyticsEngine:
    """Get or create global brain analytics engine."""
    global _global_analytics_engine
    if _global_analytics_engine is None:
        _global_analytics_engine = BrainAnalyticsEngine()
    return _global_analytics_engine


if __name__ == "__main__":

    async def test():
        engine = get_brain_analytics()

        # Test metric analysis
        insight = await engine.analyze_metric(
            "cpu_usage",
            current_value=85.5,
            historical_values=[45, 50, 55, 60, 65, 70, 75, 80],
            threshold=80.0,
        )

        print(f"Metric: {insight.metric_name}")
        print(f"Insight Type: {insight.insight_type}")
        print(f"Severity: {insight.severity}")
        print(f"Confidence: {insight.confidence:.2f}")
        print(f"Description: {insight.description[:100]}...")

        # Test trend prediction
        prediction = await engine.predict_trend(
            "memory_usage",
            historical_values=[40, 42, 45, 48, 52, 55, 58],
            forecast_horizon=5,
        )

        print(f"\nTrend: {prediction['trend']}")
        print(f"Predicted: {prediction['predicted_values']}")
        print(f"Confidence: {prediction['confidence']:.2f}")

    asyncio.run(test())

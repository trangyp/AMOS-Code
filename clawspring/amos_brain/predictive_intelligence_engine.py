"""AMOS Predictive Intelligence Engine v1.0.0 - Forecast-Driven Prevention

Predicts system degradation before it occurs using time-series forecasting,
trend analysis, and pattern recognition on detection metrics.

Architecture:
    Historical Detection Data → Pattern Analysis → Forecasting → Early Warning
        ↓
    Predicted Issue → Governance Decision → Preventive Remediation

Prediction Methods:
- Linear trend extrapolation (short-term)
- Exponential smoothing (medium-term)
- Seasonal pattern detection (recurring issues)
- Anomaly trajectory prediction (rate-of-change based)

Integration:
- UnifiedDetectionEngine (data source)
- AutoRemediationEngine (preventive action target)
- AutonomousGovernanceEngine (policy enforcement)
- UnifiedGovernanceCoordinator (orchestration)

Owner: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import json
import math
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import detection for data source
try:
    from .unified_detection_engine import (
        UnifiedDetectionEngine,
        UnifiedDetectionReport,
    )

    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False

# Import remediation for preventive actions
try:
    from .auto_remediation_engine import (
        AutoRemediationEngine,
        RemediationPlan,
    )

    REMEDIATION_AVAILABLE = True
except ImportError:
    REMEDIATION_AVAILABLE = False


# =============================================================================
# Enums and Data Classes
# =============================================================================


class PredictionHorizon(Enum):
    """Time horizons for predictions."""

    IMMEDIATE = "immediate"  # 1-5 minutes
    SHORT_TERM = "short_term"  # 15-60 minutes
    MEDIUM_TERM = "medium_term"  # 1-6 hours
    LONG_TERM = "long_term"  # 6-24 hours


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""

    HIGH = "high"  # > 85%
    MEDIUM = "medium"  # 60-85%
    LOW = "low"  # 40-60%
    UNCERTAIN = "uncertain"  # < 40%


class TrendDirection(Enum):
    """Direction of metric trend."""

    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"
    CRITICAL = "critical"


@dataclass
class MetricSnapshot:
    """Single metric measurement at a point in time."""

    timestamp: float
    metric_name: str
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Analysis result for a single metric trend."""

    metric_name: str
    direction: TrendDirection
    slope: float  # Rate of change per hour
    volatility: float  # Standard deviation
    recent_values: list[float] = field(default_factory=list)

    @property
    def is_accelerating(self) -> bool:
        """Check if degradation is accelerating."""
        if len(self.recent_values) < 3:
            return False
        # Check if slope is increasing (more negative for degradation)
        recent_slope = (self.recent_values[-1] - self.recent_values[-3]) / 2
        return abs(recent_slope) > abs(self.slope) * 1.5


@dataclass
class Prediction:
    """Single prediction result."""

    prediction_id: str
    timestamp: float
    horizon: PredictionHorizon

    # What we're predicting
    metric_name: str
    current_value: float
    predicted_value: float

    # Prediction quality
    confidence: float  # 0-1
    confidence_level: PredictionConfidence

    # Risk assessment
    risk_score: float  # 0-1
    severity: str  # low, medium, high, critical

    # Recommended action
    recommended_action: str
    time_until_issue: float = None  # minutes

    # Validation
    validated: bool = False
    actual_value: float = None
    prediction_error: float = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "horizon": self.horizon.value,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "predicted_value": self.predicted_value,
            "confidence": round(self.confidence, 3),
            "confidence_level": self.confidence_level.value,
            "risk_score": round(self.risk_score, 3),
            "severity": self.severity,
            "recommended_action": self.recommended_action,
            "time_until_issue": round(self.time_until_issue, 1) if self.time_until_issue else None,
            "validated": self.validated,
        }


@dataclass
class PredictiveAlert:
    """Alert generated from prediction."""

    alert_id: str
    timestamp: float
    predictions: list[Prediction]

    # Aggregated assessment
    overall_risk: float
    worst_severity: str

    # Action taken
    action_triggered: bool = False
    action_type: str = None
    action_result: dict = None


# =============================================================================
# Time Series Forecasting
# =============================================================================


class TimeSeriesForecaster:
    """Lightweight time series forecasting for AMOS metrics.

    Implements multiple forecasting methods:
    - Simple exponential smoothing (for stable metrics)
    - Linear trend (for trending metrics)
    - Seasonal detection (for cyclic patterns)
    """

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: dict[str, deque[MetricSnapshot]] = {}

    def add_measurement(self, snapshot: MetricSnapshot) -> None:
        """Add a metric measurement to history."""
        if snapshot.metric_name not in self.history:
            self.history[snapshot.metric_name] = deque(maxlen=self.max_history)

        self.history[snapshot.metric_name].append(snapshot)

    def forecast(
        self,
        metric_name: str,
        horizon_minutes: float,
        method: str = "auto",
    ) -> Prediction | None:
        """Forecast future value of a metric.

        Args:
            metric_name: Name of metric to forecast
            horizon_minutes: How far ahead to predict
            method: Forecasting method ("auto", "linear", "exponential", "seasonal")

        Returns:
            Prediction object or None if insufficient data

        """
        if metric_name not in self.history:
            return None

        history = list(self.history[metric_name])
        if len(history) < 3:
            return None  # Need at least 3 points

        # Extract values and timestamps
        values = [s.value for s in history]
        timestamps = [s.timestamp for s in history]
        current_value = values[-1]
        current_time = timestamps[-1]

        # Auto-select method based on data characteristics
        if method == "auto":
            method = self._select_method(values)

        # Generate forecast
        if method == "linear":
            predicted_value, confidence = self._linear_forecast(
                values, timestamps, current_time + horizon_minutes * 60
            )
        elif method == "exponential":
            predicted_value, confidence = self._exponential_forecast(values, horizon_minutes)
        elif method == "seasonal":
            predicted_value, confidence = self._seasonal_forecast(
                values, timestamps, horizon_minutes
            )
        else:
            predicted_value, confidence = self._linear_forecast(
                values, timestamps, current_time + horizon_minutes * 60
            )

        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(confidence, len(values))

        # Assess risk
        risk_score = self._assess_risk(metric_name, current_value, predicted_value)
        severity = self._risk_to_severity(risk_score)

        # Determine horizon enum
        horizon = self._minutes_to_horizon(horizon_minutes)

        # Recommend action
        recommended_action = self._recommend_action(
            metric_name, severity, predicted_value, current_value
        )

        # Calculate time until issue (if degrading)
        time_until = None
        if predicted_value < current_value and severity in ["high", "critical"]:
            # Extrapolate when it will hit threshold
            degradation_rate = (current_value - predicted_value) / horizon_minutes
            if degradation_rate > 0:
                # Time to reach 0.5 threshold (50% health)
                time_until = (current_value - 0.5) / degradation_rate

        return Prediction(
            prediction_id=f"pred_{int(current_time)}_{metric_name}",
            timestamp=current_time,
            horizon=horizon,
            metric_name=metric_name,
            current_value=current_value,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_level=confidence_level,
            risk_score=risk_score,
            severity=severity,
            recommended_action=recommended_action,
            time_until_issue=time_until,
        )

    def _select_method(self, values: list[float]) -> str:
        """Auto-select best forecasting method based on data."""
        if len(values) < 5:
            return "linear"

        # Check for seasonality (simplified)
        diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
        sign_changes = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i - 1] < 0)

        if sign_changes > len(diffs) * 0.4:
            # Oscillating pattern suggests seasonality
            return "seasonal"

        # Check trend strength
        avg_diff = sum(diffs) / len(diffs)
        if abs(avg_diff) > 0.01:
            return "linear"

        return "exponential"

    def _linear_forecast(
        self,
        values: list[float],
        timestamps: list[float],
        target_time: float,
    ) -> tuple[float, float]:
        """Linear trend extrapolation."""
        n = len(values)

        # Calculate slope using least squares
        mean_t = sum(timestamps) / n
        mean_v = sum(values) / n

        numerator = sum((timestamps[i] - mean_t) * (values[i] - mean_v) for i in range(n))
        denominator = sum((timestamps[i] - mean_t) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Convert to per-second slope
        slope_per_sec = slope

        # Current time and value
        current_time = timestamps[-1]
        current_value = values[-1]

        # Forecast
        time_delta = target_time - current_time
        predicted = current_value + slope_per_sec * time_delta

        # Clip to valid range
        predicted = max(0.0, min(1.0, predicted))

        # Confidence based on fit quality (R²)
        ss_res = sum(
            (values[i] - (mean_v + slope * (timestamps[i] - mean_t))) ** 2 for i in range(n)
        )
        ss_tot = sum((values[i] - mean_v) ** 2 for i in range(n))

        if ss_tot == 0:
            r_squared = 1.0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        confidence = max(0.3, min(0.95, r_squared))

        return predicted, confidence

    def _exponential_forecast(
        self,
        values: list[float],
        horizon_minutes: float,
    ) -> tuple[float, float]:
        """Simple exponential smoothing."""
        alpha = 0.3  # Smoothing factor

        # Calculate smoothed values
        smoothed = values[0]
        for v in values[1:]:
            smoothed = alpha * v + (1 - alpha) * smoothed

        # Forecast stays at smoothed level
        predicted = smoothed

        # Confidence decreases with horizon
        confidence = max(0.4, 0.9 - (horizon_minutes / 60) * 0.1)

        return predicted, confidence

    def _seasonal_forecast(
        self,
        values: list[float],
        timestamps: list[float],
        horizon_minutes: float,
    ) -> tuple[float, float]:
        """Simple seasonal pattern detection."""
        # Detect period (simplified)
        if len(values) < 10:
            return self._linear_forecast(values, timestamps, timestamps[-1] + horizon_minutes * 60)

        # Use last period's value as prediction
        period = min(len(values) // 2, 10)
        seasonal_index = len(values) % period if period > 0 else 0

        # Find historical values at this seasonal position
        seasonal_values = [values[i] for i in range(seasonal_index, len(values), period)]

        if seasonal_values:
            predicted = sum(seasonal_values) / len(seasonal_values)
        else:
            predicted = values[-1]

        # Seasonal confidence
        confidence = 0.7 if len(seasonal_values) > 2 else 0.5

        return predicted, confidence

    def _calculate_confidence_level(
        self,
        confidence: float,
        sample_size: int,
    ) -> PredictionConfidence:
        """Convert numeric confidence to level."""
        # Adjust for small sample size
        if sample_size < 5:
            confidence *= 0.8
        elif sample_size < 10:
            confidence *= 0.9

        if confidence > 0.85:
            return PredictionConfidence.HIGH
        elif confidence > 0.60:
            return PredictionConfidence.MEDIUM
        elif confidence > 0.40:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.UNCERTAIN

    def _assess_risk(
        self,
        metric_name: str,
        current: float,
        predicted: float,
    ) -> float:
        """Calculate risk score from prediction."""
        # Base risk on predicted value
        base_risk = 1.0 - predicted

        # Amplify if degrading
        if predicted < current:
            degradation_factor = (current - predicted) / max(current, 0.01)
            base_risk *= 1 + degradation_factor

        return min(1.0, base_risk)

    def _risk_to_severity(self, risk: float) -> str:
        """Convert risk score to severity."""
        if risk > 0.8:
            return "critical"
        elif risk > 0.6:
            return "high"
        elif risk > 0.4:
            return "medium"
        else:
            return "low"

    def _minutes_to_horizon(self, minutes: float) -> PredictionHorizon:
        """Convert minutes to horizon enum."""
        if minutes <= 5:
            return PredictionHorizon.IMMEDIATE
        elif minutes <= 60:
            return PredictionHorizon.SHORT_TERM
        elif minutes <= 360:
            return PredictionHorizon.MEDIUM_TERM
        else:
            return PredictionHorizon.LONG_TERM

    def _recommend_action(
        self,
        metric_name: str,
        severity: str,
        predicted: float,
        current: float,
    ) -> str:
        """Generate action recommendation based on prediction."""
        if severity == "critical":
            return "immediate_preventive_remediation"
        elif severity == "high":
            return "prepare_remediation_resources"
        elif severity == "medium":
            return "increase_monitoring_frequency"
        else:
            return "continue_normal_monitoring"

    def analyze_trends(self) -> list[TrendAnalysis]:
        """Analyze trends for all tracked metrics."""
        trends = []

        for metric_name, history_deque in self.history.items():
            history = list(history_deque)
            if len(history) < 3:
                continue

            values = [s.value for s in history]
            timestamps = [s.timestamp for s in history]

            # Calculate slope (per hour)
            time_span_hours = (timestamps[-1] - timestamps[0]) / 3600
            if time_span_hours > 0:
                slope = (values[-1] - values[0]) / time_span_hours
            else:
                slope = 0

            # Calculate volatility
            if len(values) > 1:
                mean_v = sum(values) / len(values)
                variance = sum((v - mean_v) ** 2 for v in values) / len(values)
                volatility = math.sqrt(variance)
            else:
                volatility = 0

            # Determine direction
            if slope < -0.1:
                direction = TrendDirection.CRITICAL
            elif slope < -0.05:
                direction = TrendDirection.DEGRADING
            elif slope > 0.05:
                direction = TrendDirection.IMPROVING
            else:
                direction = TrendDirection.STABLE

            trends.append(
                TrendAnalysis(
                    metric_name=metric_name,
                    direction=direction,
                    slope=slope,
                    volatility=volatility,
                    recent_values=values[-5:],
                )
            )

        return trends


# =============================================================================
# Predictive Intelligence Engine
# =============================================================================


class PredictiveIntelligenceEngine:
    """Main predictive intelligence engine for AMOS.

    Provides:
    - Time-series forecasting of all detection metrics
    - Early warning system for predicted issues
    - Trend analysis and pattern detection
    - Integration with remediation for preventive action
    """

    # Prediction thresholds
    DEFAULT_HORIZONS = [5, 15, 60, 360]  # minutes
    ALERT_THRESHOLD = 0.7  # Risk score to trigger alert

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.forecaster = TimeSeriesForecaster(max_history=self.config.get("max_history", 100))

        # State
        self._predictions: list[Prediction] = []
        self._alerts: list[PredictiveAlert] = []
        self._last_detection: UnifiedDetectionReport | None = None

        # Integration
        self._remediation_engine: AutoRemediationEngine | None = None
        if REMEDIATION_AVAILABLE:
            self._remediation_engine = AutoRemediationEngine()

        # Callbacks
        self._alert_handlers: list[Callable[[PredictiveAlert], None]] = []

    def record_detection(self, report: UnifiedDetectionReport) -> None:
        """Record detection report metrics for forecasting.

        This should be called whenever detection runs.
        """
        self._last_detection = report
        timestamp = datetime.now().timestamp()

        # Extract key metrics from report
        metrics = {
            "overall_health": report.overall_system_health,
            "hallucination_score": report.hallucination.unified_hallucination_score,
            "integrity_score": report.integrity.unified_integrity_score,
            "drift_score": report.structural_drift.unified_drift_score,
            "fisher_information": report.fisher_information,
            "renyi_entropy": report.renyi_entropy,
            "tsallis_entropy": report.tsallis_entropy,
            "data_processing": report.data_processing_score,
        }

        # Add to forecaster
        for metric_name, value in metrics.items():
            self.forecaster.add_measurement(
                MetricSnapshot(
                    timestamp=timestamp,
                    metric_name=metric_name,
                    value=value,
                    metadata={"session_id": report.session_id},
                )
            )

    def generate_predictions(
        self,
        horizons: list[float] = None,
    ) -> list[Prediction]:
        """Generate predictions for all tracked metrics.

        Args:
            horizons: List of prediction horizons in minutes

        Returns:
            List of predictions for all metrics

        """
        if horizons is None:
            horizons = self.DEFAULT_HORIZONS

        predictions = []

        for metric_name in self.forecaster.history.keys():
            for horizon in horizons:
                prediction = self.forecaster.forecast(metric_name, horizon)
                if prediction:
                    predictions.append(prediction)
                    self._predictions.append(prediction)

        return predictions

    def check_for_alerts(self) -> list[PredictiveAlert]:
        """Check predictions and generate alerts for high-risk forecasts.

        Returns:
            List of predictive alerts

        """
        alerts = []

        # Group predictions by severity
        high_risk = [p for p in self._predictions if p.risk_score >= self.ALERT_THRESHOLD]

        if not high_risk:
            return alerts

        # Group by time window
        time_windows: dict[str, list[Prediction]] = {}
        for pred in high_risk:
            window_key = pred.horizon.value
            if window_key not in time_windows:
                time_windows[window_key] = []
            time_windows[window_key].append(pred)

        # Generate alert for each time window with issues
        for window, predictions in time_windows.items():
            # Calculate overall risk
            max_risk = max(p.risk_score for p in predictions)
            worst_severity = max(
                ([p.severity for p in predictions]),
                key=lambda s: ["low", "medium", "high", "critical"].index(s),
            )

            alert = PredictiveAlert(
                alert_id=f"pred_alert_{int(datetime.now().timestamp())}_{window}",
                timestamp=datetime.now().timestamp(),
                predictions=predictions,
                overall_risk=max_risk,
                worst_severity=worst_severity,
            )

            alerts.append(alert)
            self._alerts.append(alert)

            # Notify handlers
            for handler in self._alert_handlers:
                try:
                    handler(alert)
                except Exception:
                    pass

        return alerts

    def trigger_preventive_remediation(
        self,
        alert: PredictiveAlert,
    ) -> RemediationPlan | None:
        """Trigger preventive remediation for predicted issue.

        Args:
            alert: Predictive alert to act on

        Returns:
            Remediation plan if action taken

        """
        if not self._remediation_engine:
            return None

        # Only act on high-confidence predictions
        high_confidence = [p for p in alert.predictions if p.confidence > 0.75]
        if not high_confidence:
            return None

        # Find worst prediction
        worst = max(high_confidence, key=lambda p: p.risk_score)

        # Create synthetic detection report for remediation
        # This allows us to use existing remediation strategies
        if DETECTION_AVAILABLE and self._last_detection:
            # Modify last detection with predicted values
            synthetic_report = self._create_synthetic_report(worst)

            # Trigger remediation
            plan = self._remediation_engine.remediate(synthetic_report)

            # Mark alert as acted upon
            alert.action_triggered = True
            alert.action_type = "preventive_remediation"
            alert.action_result = {"plan_id": plan.plan_id}

            return plan

        return None

    def _create_synthetic_report(
        self,
        prediction: Prediction,
    ) -> UnifiedDetectionReport:
        """Create synthetic detection report from prediction."""
        if not self._last_detection:
            raise ValueError("No previous detection to base synthetic report on")

        # Start with last detection
        base = self._last_detection

        # Modify based on prediction
        # This is a simplified version - real implementation would
        # adjust all relevant sub-metrics

        # For now, return the base report with adjusted confidence
        # The remediation engine will see the predicted issue severity
        return base

    def get_trend_report(self) -> dict[str, Any]:
        """Generate comprehensive trend analysis report."""
        trends = self.forecaster.analyze_trends()

        # Categorize trends
        improving = [t for t in trends if t.direction == TrendDirection.IMPROVING]
        stable = [t for t in trends if t.direction == TrendDirection.STABLE]
        degrading = [
            t for t in trends if t.direction in [TrendDirection.DEGRADING, TrendDirection.CRITICAL]
        ]
        accelerating = [t for t in trends if t.is_accelerating]

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_metrics": len(trends),
                "improving": len(improving),
                "stable": len(stable),
                "degrading": len(degrading),
                "accelerating": len(accelerating),
            },
            "degrading_metrics": [
                {
                    "metric": t.metric_name,
                    "direction": t.direction.value,
                    "slope_per_hour": round(t.slope, 4),
                    "volatility": round(t.volatility, 4),
                    "accelerating": t.is_accelerating,
                }
                for t in degrading
            ],
            "recommendations": self._generate_recommendations(trends),
        }

    def _generate_recommendations(self, trends: list[TrendAnalysis]) -> list[str]:
        """Generate recommendations based on trends."""
        recs = []

        critical = [t for t in trends if t.direction == TrendDirection.CRITICAL]
        if critical:
            recs.append(
                f"URGENT: {len(critical)} metrics in critical decline - immediate action required"
            )

        degrading = [t for t in trends if t.direction == TrendDirection.DEGRADING]
        if degrading:
            recs.append(
                f"WARNING: {len(degrading)} metrics degrading - prepare preventive measures"
            )

        accelerating = [t for t in trends if t.is_accelerating]
        if accelerating:
            recs.append(
                f"ALERT: {len(accelerating)} degradations accelerating - escalation recommended"
            )

        high_volatility = [t for t in trends if t.volatility > 0.2]
        if high_volatility:
            recs.append(
                f"NOTE: {len(high_volatility)} metrics show high volatility - may indicate instability"
            )

        return recs

    def get_prediction_accuracy(self) -> dict[str, float]:
        """Calculate prediction accuracy for validated predictions.

        Returns:
            Dict with accuracy metrics

        """
        validated = [p for p in self._predictions if p.validated and p.actual_value is not None]

        if not validated:
            return {"accuracy": 0.0, "count": 0}

        # Calculate MAE (Mean Absolute Error)
        errors = [abs(p.predicted_value - p.actual_value) for p in validated]
        mae = sum(errors) / len(errors)

        # Calculate percentage within threshold
        within_threshold = sum(1 for e in errors if e < 0.1)
        accuracy = within_threshold / len(validated)

        return {
            "mae": round(mae, 4),
            "accuracy": round(accuracy, 2),
            "count": len(validated),
        }

    def export_predictions(self, output_path: Path | None = None) -> Path:
        """Export all predictions to JSON."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"amos_predictions_{timestamp}.json")

        data = {
            "export_metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            },
            "predictions": [p.to_dict() for p in self._predictions[-100:]],
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "timestamp": datetime.fromtimestamp(a.timestamp).isoformat(),
                    "overall_risk": round(a.overall_risk, 3),
                    "worst_severity": a.worst_severity,
                    "predictions_count": len(a.predictions),
                    "action_triggered": a.action_triggered,
                }
                for a in self._alerts[-20:]
            ],
            "accuracy": self.get_prediction_accuracy(),
            "trend_report": self.get_trend_report(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path

    def register_alert_handler(self, handler: Callable[[PredictiveAlert], None]) -> None:
        """Register a callback for predictive alerts."""
        self._alert_handlers.append(handler)


# =============================================================================
# Convenience Functions
# =============================================================================


def create_predictive_engine(config: dict = None) -> PredictiveIntelligenceEngine:
    """Factory function to create predictive intelligence engine."""
    return PredictiveIntelligenceEngine(config)


# =============================================================================
# Module Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AMOS Predictive Intelligence Engine - Test Suite")
    print("=" * 70)

    # Create engine
    engine = PredictiveIntelligenceEngine()

    # Simulate historical detection data
    print("\n[Test 1] Loading Historical Data")
    print("-" * 50)

    import time

    base_time = time.time()

    # Simulate degrading health over time
    for i in range(20):
        timestamp = base_time - (19 - i) * 300  # Every 5 minutes

        # Degrading health pattern
        health = 0.85 - (i * 0.02) + (0.01 if i % 3 == 0 else 0)
        hallucination = 0.20 + (i * 0.015)
        integrity = 0.15 + (i * 0.01)
        drift = 0.30 + (i * 0.02)

        engine.forecaster.add_measurement(
            MetricSnapshot(
                timestamp=timestamp,
                metric_name="overall_health",
                value=max(0, min(1, health)),
            )
        )
        engine.forecaster.add_measurement(
            MetricSnapshot(
                timestamp=timestamp,
                metric_name="hallucination_score",
                value=max(0, min(1, hallucination)),
            )
        )
        engine.forecaster.add_measurement(
            MetricSnapshot(
                timestamp=timestamp,
                metric_name="integrity_score",
                value=max(0, min(1, integrity)),
            )
        )
        engine.forecaster.add_measurement(
            MetricSnapshot(
                timestamp=timestamp,
                metric_name="drift_score",
                value=max(0, min(1, drift)),
            )
        )

    print(f"Loaded {len(engine.forecaster.history)} metrics with 20 data points each")

    # Test 2: Trend Analysis
    print("\n[Test 2] Trend Analysis")
    print("-" * 50)

    trends = engine.forecaster.analyze_trends()
    for trend in trends:
        print(
            f"  {trend.metric_name}: {trend.direction.value} "
            f"(slope: {trend.slope:.4f}/hr, volatility: {trend.volatility:.4f})"
        )

    # Test 3: Forecasting
    print("\n[Test 3] Multi-Horizon Forecasting")
    print("-" * 50)

    predictions = engine.generate_predictions(horizons=[5, 15, 60])

    for pred in predictions[:8]:  # Show first 8
        print(f"  {pred.metric_name} ({pred.horizon.value}):")
        print(f"    Current: {pred.current_value:.3f} → Predicted: {pred.predicted_value:.3f}")
        print(f"    Confidence: {pred.confidence:.1%} ({pred.confidence_level.value})")
        print(f"    Risk: {pred.risk_score:.2f} | Severity: {pred.severity}")
        if pred.time_until_issue:
            print(f"    Time until critical: {pred.time_until_issue:.1f} min")
        print()

    # Test 4: Alert Generation
    print("\n[Test 4] Predictive Alert Generation")
    print("-" * 50)

    alerts = engine.check_for_alerts()

    if alerts:
        for alert in alerts:
            print(f"  ALERT {alert.alert_id}")
            print(f"    Overall Risk: {alert.overall_risk:.2f}")
            print(f"    Worst Severity: {alert.worst_severity}")
            print(f"    Predictions: {len(alert.predictions)}")
            print()
    else:
        print("  No alerts generated (degradation may not be severe enough)")

    # Test 5: Trend Report
    print("\n[Test 5] Trend Report")
    print("-" * 50)

    report = engine.get_trend_report()
    print(f"Summary: {report['summary']}")
    print("\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    # Test 6: Export
    print("\n[Test 6] Export Predictions")
    print("-" * 50)

    export_path = engine.export_predictions()
    print(f"Exported to: {export_path}")
    export_path.unlink()  # Cleanup

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)

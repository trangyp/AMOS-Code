"""
Predictive Architecture Intelligence Engine.

Learns from historical architecture data to predict future failures.

Features:
- Pattern recognition from failure history
- Correlation detection between architecture metrics
- Predictive scoring for impending degradation
- Early warning system with lead time estimation
- Risk scoring for code changes
- Trend extrapolation for architecture health

The predictive engine enables proactive architecture management.
"""

import math
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FailurePattern:
    """Recognized pattern that leads to architecture failures."""

    pattern_id: str
    name: str
    description: str
    # Preconditions that indicate this pattern
    preconditions: dict[str, tuple[float, float]]  # metric -> (min, max) threshold
    # Historical accuracy
    occurrences: int = 0
    true_positives: int = 0
    false_positives: int = 0
    # Timing
    avg_lead_time_hours: float = 0.0
    # Severity of resulting failure
    typical_severity: str = "medium"  # critical, high, medium, low

    @property
    def accuracy(self) -> float:
        """Calculate prediction accuracy."""
        total = self.true_positives + self.false_positives
        if total == 0:
            return 0.5  # Unknown
        return self.true_positives / total

    @property
    def confidence(self) -> float:
        """Calculate confidence score based on accuracy and occurrences."""
        if self.occurrences < 3:
            return 0.3  # Insufficient data
        return min(0.95, self.accuracy * (1 - 1 / self.occurrences))


@dataclass
class Prediction:
    """A specific prediction about future architecture state."""

    prediction_id: str
    timestamp: float
    pattern_id: str
    metric: str  # Which metric will be affected
    predicted_value: float
    current_value: float
    confidence: float
    lead_time_hours: float
    severity: str
    message: str
    recommended_action: str


@dataclass
class EarlyWarning:
    """Early warning about impending architecture degradation."""

    warning_id: str
    timestamp: float
    warning_type: str  # "degradation", "failure", "critical"
    affected_layers: list[str]
    confidence: float
    lead_time_hours: float
    indicators: list[str]
    recommended_actions: list[str]
    auto_preventable: bool  # Can system auto-fix?


@dataclass
class ChangeRiskAssessment:
    """Risk assessment for a set of code changes."""

    files_changed: list[str]
    timestamp: float
    overall_risk: float  # 0-1, higher = riskier
    risk_factors: list[str]
    protected_invariants_at_risk: list[str]
    predicted_issues: list[str]
    recommended_tests: list[str]
    safe_to_proceed: bool


class PatternRecognizer:
    """Recognizes patterns in historical architecture data."""

    # Known failure patterns from research and experience
    KNOWN_PATTERNS: list[FailurePattern] = [
        FailurePattern(
            pattern_id="p1",
            name="Import Complexity Cascade",
            description="Rising import complexity precedes circular dependency failures",
            preconditions={"import_score": (0.4, 0.7), "syntax_score": (0.8, 1.0)},
            typical_severity="high",
        ),
        FailurePattern(
            pattern_id="p2",
            name="API Drift Preceding Contract Break",
            description="Gradual API score decline predicts contract violation",
            preconditions={"api_score": (0.3, 0.6), "type_score": (0.7, 1.0)},
            typical_severity="critical",
        ),
        FailurePattern(
            pattern_id="p3",
            name="Semantic Ambiguity Buildup",
            description="Declining semantic score indicates ontology drift",
            preconditions={"semantic_score": (0.2, 0.5)},
            typical_severity="medium",
        ),
        FailurePattern(
            pattern_id="p4",
            name="Recovery Path Erosion",
            description="Recovery score decline precedes incident handling failures",
            preconditions={"recovery_score": (0.3, 0.6), "architecture_score": (0.5, 0.8)},
            typical_severity="high",
        ),
        FailurePattern(
            pattern_id="p5",
            name="Test Coverage Blind Spot",
            description="Low test score combined with high complexity predicts regression",
            preconditions={"test_score": (0.0, 0.4), "api_score": (0.6, 1.0)},
            typical_severity="high",
        ),
        FailurePattern(
            pattern_id="p6",
            name="Security Invariant Decay",
            description="Security score decline predicts vulnerability introduction",
            preconditions={"security_score": (0.2, 0.5)},
            typical_severity="critical",
        ),
        FailurePattern(
            pattern_id="p7",
            name="Temporal Order Entropy",
            description="Temporal score decline indicates deployment ordering issues",
            preconditions={"temporal_score": (0.3, 0.6), "runtime_score": (0.5, 0.8)},
            typical_severity="high",
        ),
        FailurePattern(
            pattern_id="p8",
            name="Diagnostic Blindness",
            description="Diagnostic score decline means issues go undetected",
            preconditions={"diagnostic_score": (0.2, 0.5), "observability_score": (0.3, 0.6)},
            typical_severity="medium",
        ),
        FailurePattern(
            pattern_id="p9",
            name="Multi-Layer Degradation",
            description="Simultaneous decline in 3+ metrics predicts system failure",
            preconditions={"overall_score": (0.4, 0.6)},
            typical_severity="critical",
        ),
        FailurePattern(
            pattern_id="p10",
            name="Provenance Trust Collapse",
            description="Provenance score decline precedes supply chain issues",
            preconditions={"provenance_score": (0.2, 0.5)},
            typical_severity="high",
        ),
    ]

    def __init__(self):
        self.patterns: dict[str, FailurePattern] = {p.pattern_id: p for p in self.KNOWN_PATTERNS}
        self.observed_transitions: list[dict[str, Any]] = []

    def analyze_snapshot(self, snapshot: dict[str, float]) -> list[Prediction]:
        """Analyze a health snapshot for predictive patterns."""
        predictions = []

        for pattern in self.patterns.values():
            match_score = self._calculate_pattern_match(pattern, snapshot)

            if match_score > 0.6:  # Threshold for prediction
                # Calculate which metric will be affected
                affected_metric = list(pattern.preconditions.keys())[0]
                current_val = snapshot.get(affected_metric, 1.0)

                prediction = Prediction(
                    prediction_id=f"pred_{int(time.time())}_{pattern.pattern_id}",
                    timestamp=time.time(),
                    pattern_id=pattern.pattern_id,
                    metric=affected_metric,
                    predicted_value=current_val * 0.7,  # Predict 30% degradation
                    current_value=current_val,
                    confidence=match_score * pattern.confidence,
                    lead_time_hours=pattern.avg_lead_time_hours or 24,
                    severity=pattern.typical_severity,
                    message=f"Pattern '{pattern.name}' detected: {pattern.description}",
                    recommended_action=self._get_recommended_action(pattern),
                )
                predictions.append(prediction)

        return sorted(predictions, key=lambda p: p.confidence, reverse=True)

    def _calculate_pattern_match(
        self, pattern: FailurePattern, snapshot: dict[str, float]
    ) -> float:
        """Calculate how well snapshot matches pattern preconditions."""
        matches = 0
        total = len(pattern.preconditions)

        for metric, (min_val, max_val) in pattern.preconditions.items():
            value = snapshot.get(metric, 1.0)
            if min_val <= value <= max_val:
                # Calculate match strength (closer to middle = stronger match)
                mid = (min_val + max_val) / 2
                distance = abs(value - mid) / (max_val - min_val)
                matches += 1 - distance

        return matches / total if total > 0 else 0.0

    def _get_recommended_action(self, pattern: FailurePattern) -> str:
        """Get recommended action for a pattern."""
        actions = {
            "p1": "Review import structure and simplify dependencies",
            "p2": "Strengthen API contract tests and validation",
            "p3": "Create semantic registry to disambiguate terms",
            "p4": "Document and test recovery procedures",
            "p5": "Add tests for high-complexity areas",
            "p6": "Run security audit and add invariant checks",
            "p7": "Validate deployment ordering constraints",
            "p8": "Add observability and diagnostic coverage",
            "p9": "System-wide architecture review required",
            "p10": "Verify dependency provenance and versions",
        }
        return actions.get(pattern.pattern_id, "Review architecture health metrics")

    def learn_from_outcome(
        self,
        prediction_id: str,
        pattern_id: str,
        actual_outcome: str,  # "true_positive", "false_positive", "missed"
        time_to_failure: float = None,
    ):
        """Learn from prediction accuracy to improve future predictions."""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return

        pattern.occurrences += 1

        if actual_outcome == "true_positive":
            pattern.true_positives += 1
            # Update average lead time
            if time_to_failure:
                if pattern.avg_lead_time_hours == 0:
                    pattern.avg_lead_time_hours = time_to_failure
                else:
                    # Exponential moving average
                    pattern.avg_lead_time_hours = (
                        0.7 * pattern.avg_lead_time_hours + 0.3 * time_to_failure
                    )
        elif actual_outcome == "false_positive":
            pattern.false_positives += 1


class CorrelationAnalyzer:
    """Detects correlations between architecture metrics."""

    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metric_history: dict[str, deque[float]] = {
            "syntax": deque(maxlen=history_size),
            "import": deque(maxlen=history_size),
            "type": deque(maxlen=history_size),
            "api": deque(maxlen=history_size),
            "architecture": deque(maxlen=history_size),
            "semantic": deque(maxlen=history_size),
            "temporal": deque(maxlen=history_size),
            "security": deque(maxlen=history_size),
            "recovery": deque(maxlen=history_size),
            "diagnostic": deque(maxlen=history_size),
        }

    def add_snapshot(self, snapshot: dict[str, float]):
        """Add a health snapshot to history."""
        for metric in self.metric_history.keys():
            key = f"{metric}_score"
            if key in snapshot:
                self.metric_history[metric].append(snapshot[key])

    def find_correlations(self) -> list[dict[str, Any]]:
        """Find correlations between metrics."""
        correlations = []
        metrics = list(self.metric_history.keys())

        for i, m1 in enumerate(metrics):
            for m2 in metrics[i + 1 :]:
                corr = self._calculate_correlation(self.metric_history[m1], self.metric_history[m2])
                if abs(corr) > 0.5:  # Significant correlation threshold
                    correlations.append(
                        {
                            "metric_1": m1,
                            "metric_2": m2,
                            "correlation": corr,
                            "strength": "strong" if abs(corr) > 0.7 else "moderate",
                            "direction": "positive" if corr > 0 else "negative",
                        }
                    )

        return sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True)

    def _calculate_correlation(self, x: deque[float], y: deque[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) < 3 or len(y) < 3 or len(x) != len(y):
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(a * b for a, b in zip(x, y))
        sum_x2 = sum(a * a for a in x)
        sum_y2 = sum(b * b for b in y)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))

        if denominator == 0:
            return 0.0

        return numerator / denominator


class TrendExtrapolator:
    """Extrapolates trends to predict future architecture health."""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.trends: dict[str, list[tuple[float, float]]] = {}  # metric -> [(time, value)]

    def add_point(self, metric: str, timestamp: float, value: float):
        """Add a data point for a metric."""
        if metric not in self.trends:
            self.trends[metric] = []
        self.trends[metric].append((timestamp, value))
        # Keep only recent window
        self.trends[metric] = self.trends[metric][-self.window_size :]

    def extrapolate(self, metric: str, hours_ahead: float = 24) -> dict[str, Any]:
        """Extrapolate metric value hours into the future."""
        if metric not in self.trends or len(self.trends[metric]) < 3:
            return None

        points = self.trends[metric]

        # Simple linear regression
        n = len(points)
        sum_t = sum(t for t, _ in points)
        sum_v = sum(v for _, v in points)
        sum_tv = sum(t * v for t, v in points)
        sum_t2 = sum(t * t for t, _ in points)

        # Calculate slope and intercept
        denominator = n * sum_t2 - sum_t * sum_t
        if denominator == 0:
            return None

        slope = (n * sum_tv - sum_t * sum_v) / denominator
        intercept = (sum_v - slope * sum_t) / n

        # Predict future
        future_time = points[-1][0] + hours_ahead * 3600
        predicted_value = slope * future_time + intercept

        # Calculate R-squared (goodness of fit)
        mean_v = sum_v / n
        ss_tot = sum((v - mean_v) ** 2 for _, v in points)
        ss_res = sum((v - (slope * t + intercept)) ** 2 for t, v in points)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            "metric": metric,
            "current_value": points[-1][1],
            "predicted_value": max(0.0, min(1.0, predicted_value)),
            "predicted_time": future_time,
            "hours_ahead": hours_ahead,
            "trend_slope": slope * 3600,  # Per hour
            "confidence": r_squared,
            "trend_direction": "improving" if slope > 0 else "degrading",
        }


class PredictiveArchitectureEngine:
    """
    Master engine for predictive architecture intelligence.

    Combines pattern recognition, correlation analysis, and trend extrapolation
    to predict future architecture failures before they occur.
    """

    def __init__(self, repo_path: Union[str, Path] = None):
        self.repo_path = Path(repo_path) if repo_path else Path(".")
        self.pattern_recognizer = PatternRecognizer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.trend_extrapolator = TrendExtrapolator()
        self.predictions: list[Prediction] = []
        self.warnings: list[EarlyWarning] = []

    def analyze_health_data(self, health_snapshot: dict[str, Any]) -> dict[str, Any]:
        """Analyze health data and generate predictions."""
        current_scores = health_snapshot.get("current", {})

        # Pattern recognition
        predictions = self.pattern_recognizer.analyze_snapshot(current_scores)
        self.predictions.extend(predictions)

        # Update correlation analyzer
        self.correlation_analyzer.add_snapshot(current_scores)

        # Update trend extrapolator
        timestamp = time.time()
        for metric, value in current_scores.items():
            if isinstance(value, (int, float)):
                self.trend_extrapolator.add_point(metric, timestamp, float(value))

        # Generate extrapolations
        extrapolations = []
        for metric in current_scores.keys():
            if isinstance(current_scores[metric], (int, float)):
                ext = self.trend_extrapolator.extrapolate(metric, hours_ahead=48)
                if ext:
                    extrapolations.append(ext)

        # Generate early warnings
        warnings = self._generate_early_warnings(predictions, extrapolations)
        self.warnings.extend(warnings)

        return {
            "predictions": [
                {
                    "id": p.prediction_id,
                    "pattern": p.pattern_id,
                    "metric": p.metric,
                    "current": p.current_value,
                    "predicted": p.predicted_value,
                    "confidence": p.confidence,
                    "lead_time_hours": p.lead_time_hours,
                    "severity": p.severity,
                    "message": p.message,
                    "action": p.recommended_action,
                }
                for p in predictions[:5]  # Top 5
            ],
            "extrapolations": [
                {
                    "metric": e["metric"],
                    "current": e["current_value"],
                    "predicted_48h": e["predicted_value"],
                    "trend": e["trend_direction"],
                    "confidence": e["confidence"],
                }
                for e in extrapolations[:10]
            ],
            "correlations": self.correlation_analyzer.find_correlations()[:5],
            "warnings": [
                {
                    "id": w.warning_id,
                    "type": w.warning_type,
                    "confidence": w.confidence,
                    "lead_time_hours": w.lead_time_hours,
                    "indicators": w.indicators,
                    "actions": w.recommended_actions,
                }
                for w in warnings
            ],
            "overall_risk_score": self._calculate_risk_score(predictions, warnings),
        }

    def assess_change_risk(self, changed_files: list[str]) -> ChangeRiskAssessment:
        """Assess risk of a set of code changes."""
        risk_factors = []
        predicted_issues = []
        recommended_tests = []

        # Check file types
        arch_files = [f for f in changed_files if f.endswith((".py", ".toml", ".yaml"))]
        test_files = [f for f in changed_files if "test" in f.lower()]
        doc_files = [f for f in changed_files if f.endswith(".md")]

        if len(arch_files) > 10:
            risk_factors.append("Large change blast radius")
            predicted_issues.append("Potential entanglement increase")

        if not test_files and len(arch_files) > 0:
            risk_factors.append("No test changes with code changes")
            predicted_issues.append("Test coverage gaps")
            recommended_tests.append("Add unit tests for changed code")

        if any("api" in f.lower() for f in changed_files):
            risk_factors.append("API surface changes")
            predicted_issues.append("Contract compatibility risk")
            recommended_tests.append("Run API contract tests")

        if any("migration" in f.lower() for f in changed_files):
            risk_factors.append("Database migration changes")
            predicted_issues.append("Migration ordering issues")
            recommended_tests.append("Test migration rollback")

        # Calculate overall risk
        base_risk = min(0.9, len(risk_factors) * 0.15)

        # Adjust based on active predictions
        for pred in self.predictions:
            if pred.confidence > 0.7:
                base_risk += 0.1
                predicted_issues.append(f"Predicted: {pred.message}")

        return ChangeRiskAssessment(
            files_changed=changed_files,
            timestamp=time.time(),
            overall_risk=min(1.0, base_risk),
            risk_factors=risk_factors,
            protected_invariants_at_risk=[
                "I_api_contract" if any("api" in f for f in changed_files) else None,
                "I_migration" if any("migration" in f for f in changed_files) else None,
            ],
            predicted_issues=predicted_issues,
            recommended_tests=recommended_tests,
            safe_to_proceed=base_risk < 0.5,
        )

    def _generate_early_warnings(
        self, predictions: list[Prediction], extrapolations: list[dict[str, Any]]
    ) -> list[EarlyWarning]:
        """Generate early warnings from predictions and trends."""
        warnings = []

        # Critical predictions
        critical_preds = [p for p in predictions if p.severity == "critical" and p.confidence > 0.6]

        if critical_preds:
            warnings.append(
                EarlyWarning(
                    warning_id=f"warn_{int(time.time())}_critical",
                    timestamp=time.time(),
                    warning_type="critical",
                    affected_layers=[p.metric for p in critical_preds],
                    confidence=max(p.confidence for p in critical_preds),
                    lead_time_hours=min(p.lead_time_hours for p in critical_preds),
                    indicators=[p.message for p in critical_preds],
                    recommended_actions=[p.recommended_action for p in critical_preds],
                    auto_preventable=False,
                )
            )

        # Trend-based warnings
        degrading = [
            e
            for e in extrapolations
            if e["trend_direction"] == "degrading" and e["confidence"] > 0.6
        ]
        if len(degrading) >= 3:
            warnings.append(
                EarlyWarning(
                    warning_id=f"warn_{int(time.time())}_trend",
                    timestamp=time.time(),
                    warning_type="degradation",
                    affected_layers=[e["metric"] for e in degrading],
                    confidence=sum(e["confidence"] for e in degrading) / len(degrading),
                    lead_time_hours=48,
                    indicators=[f"{e['metric']} degrading" for e in degrading],
                    recommended_actions=["Review architecture invariants"],
                    auto_preventable=False,
                )
            )

        return warnings

    def _calculate_risk_score(
        self, predictions: list[Prediction], warnings: list[EarlyWarning]
    ) -> float:
        """Calculate overall risk score from predictions and warnings."""
        base_score = 0.0

        # Add risk from predictions
        for pred in predictions:
            if pred.confidence > 0.6:
                severity_weight = {"critical": 0.3, "high": 0.2, "medium": 0.1, "low": 0.05}[
                    pred.severity
                ]
                base_score += severity_weight * pred.confidence

        # Add risk from warnings
        for warn in warnings:
            if warn.warning_type == "critical":
                base_score += 0.3 * warn.confidence
            elif warn.warning_type == "degradation":
                base_score += 0.2 * warn.confidence

        return min(1.0, base_score)

    def get_top_predictions(self, n: int = 5) -> list[Prediction]:
        """Get top N predictions by confidence."""
        return sorted(self.predictions, key=lambda p: p.confidence, reverse=True)[:n]

    def get_active_warnings(self) -> list[EarlyWarning]:
        """Get all active early warnings."""
        cutoff = time.time() - 86400  # Last 24 hours
        return [w for w in self.warnings if w.timestamp > cutoff]


def get_predictive_engine(repo_path: Union[str, Path] = None) -> PredictiveArchitectureEngine:
    """Factory function to get predictive engine instance."""
    return PredictiveArchitectureEngine(repo_path)

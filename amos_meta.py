#!/usr/bin/env python3
"""AMOS Meta-cognition System - Section 13 of Architecture

M_{t+1} = Reflect(M_t, Error_{sim}, CollapseQuality_t, MorphOutcome_t, EnergyUse_t)

Meta-cognitive goals:
- Improve prediction
- Improve branch efficiency
- Reduce failure repetition
- Tune evaluator weights
- Calibrate confidence

Parameter adaptation:
Params_{t+1} = Params_t + η · UpdateSignal_t
"""

import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MetaObservation:
    """Observation for meta-cognitive reflection."""

    timestamp: str
    cycle_id: int
    observation_type: str  # simulation_error, collapse_quality, morph_outcome, energy_use
    value: float
    context: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: float = None
    actual_outcome: float = None


@dataclass
class ReflectionResult:
    """Result of meta-cognitive reflection."""

    reflection_id: str
    insights: List[str]
    parameter_updates: Dict[str, float]
    confidence_calibration: Dict[str, float]
    learning_applied: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PredictionTracker:
    """Tracks and improves prediction accuracy.
    Monitors: Error_{sim} = ||Û_{t+1} - U_{t+1}||
    """

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.predictions: List[dict] = []  # {predicted, actual, error, timestamp}
        self.error_history: List[float] = []
        self.accuracy_trend: List[float] = []

    def record_prediction(self, predicted: dict, actual: dict, context: str = ""):
        """Record a prediction and its actual outcome."""
        # Compute prediction error
        error = self._compute_error(predicted, actual)

        entry = {
            "predicted": predicted,
            "actual": actual,
            "error": error,
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.predictions.append(entry)
        self.error_history.append(error)

        # Keep only recent window
        if len(self.predictions) > self.window_size:
            self.predictions.pop(0)
            self.error_history.pop(0)

        return error

    def _compute_error(self, predicted: dict, actual: dict) -> float:
        """Compute normalized prediction error."""
        # Simplified: compare key metrics
        errors = []

        for key in ["success", "cost", "risk"]:
            if key in predicted and key in actual:
                p_val = (
                    float(predicted[key]) if isinstance(predicted[key], (int, float, bool)) else 0.5
                )
                a_val = float(actual[key]) if isinstance(actual[key], (int, float, bool)) else 0.5
                errors.append(abs(p_val - a_val))

        return statistics.mean(errors) if errors else 0.5

    def get_accuracy(self) -> float:
        """Get current prediction accuracy (1 - mean error)."""
        if not self.error_history:
            return 0.5
        return 1.0 - statistics.mean(self.error_history)

    def get_bias(self) -> str:
        """Detect systematic bias in predictions."""
        if len(self.error_history) < 3:
            return "insufficient_data"

        mean_error = statistics.mean(self.error_history)

        if mean_error > 0.3:
            return "overconfident"  # Predictions too optimistic
        elif mean_error < -0.3:
            return "underconfident"  # Predictions too pessimistic
        else:
            return "well_calibrated"

    def improvement_suggestions(self) -> List[str]:
        """Generate suggestions for improving predictions."""
        suggestions = []

        if len(self.error_history) >= 5:
            recent_errors = self.error_history[-5:]
            if statistics.mean(recent_errors) > 0.4:
                suggestions.append("Consider adding more context to predictions")
                suggestions.append("Increase simulation depth")

            variance = statistics.variance(recent_errors) if len(recent_errors) > 1 else 0
            if variance > 0.1:
                suggestions.append("High variance detected - improve model stability")

        return suggestions


class BranchEfficiencyAnalyzer:
    """Analyzes and improves branch generation efficiency.
    Goal: Generate fewer, higher-quality branches.
    """

    def __init__(self):
        self.branch_stats: List[dict] = []
        self.generation_costs: List[float] = []
        self.selection_quality: List[float] = []

    def record_branch_generation(
        self, n_branches: int, cost: float, selected_branch_rank: int, outcome_success: bool
    ):
        """Record branch generation statistics."""
        entry = {
            "n_branches": n_branches,
            "generation_cost": cost,
            "selected_rank": selected_branch_rank,  # 1 = top, higher = worse
            "outcome_success": outcome_success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.branch_stats.append(entry)
        self.generation_costs.append(cost)

        # Quality: success + (1/rank)
        quality = (1.0 if outcome_success else 0.0) + (1.0 / selected_branch_rank)
        self.selection_quality.append(quality)

        # Keep history manageable
        if len(self.branch_stats) > 50:
            self.branch_stats.pop(0)
            self.generation_costs.pop(0)
            self.selection_quality.pop(0)

    def analyze_efficiency(self) -> dict:
        """Analyze branch generation efficiency."""
        if not self.branch_stats:
            return {"status": "no_data"}

        avg_cost = statistics.mean(self.generation_costs)
        avg_quality = statistics.mean(self.selection_quality)
        avg_branches = statistics.mean([s["n_branches"] for s in self.branch_stats])

        # Cost-quality ratio
        efficiency = avg_quality / (avg_cost + 0.01)

        return {
            "avg_generation_cost": avg_cost,
            "avg_selection_quality": avg_quality,
            "avg_branches_generated": avg_branches,
            "efficiency_ratio": efficiency,
            "recommendation": self._recommend(avg_branches, avg_quality),
        }

    def _recommend(self, avg_branches: float, avg_quality: float) -> str:
        """Generate recommendation based on analysis."""
        if avg_branches > 5 and avg_quality < 1.5:
            return "reduce_branch_count"
        elif avg_branches < 3 and avg_quality < 1.5:
            return "increase_branch_diversity"
        elif avg_quality > 1.8:
            return "maintain_current"
        else:
            return "improve_branch_scoring"


class FailurePatternDetector:
    """Detects and learns from failure patterns.
    Goal: Reduce failure repetition.
    """

    def __init__(self):
        self.failures: List[dict] = []
        self.failure_patterns: Dict[str, int] = defaultdict(int)
        self.context_signatures: dict[str, list[str]] = {}

    def record_failure(self, failure_type: str, context: dict, action_taken: str, consequence: str):
        """Record a failure for pattern analysis."""
        entry = {
            "type": failure_type,
            "context": context,
            "action": action_taken,
            "consequence": consequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.failures.append(entry)

        # Extract pattern signature
        signature = self._extract_signature(failure_type, context)
        self.failure_patterns[signature] += 1

        # Store context for future avoidance
        if signature not in self.context_signatures:
            self.context_signatures[signature] = []
        self.context_signatures[signature].append(str(context))

        # Limit history
        if len(self.failures) > 100:
            old = self.failures.pop(0)
            old_sig = self._extract_signature(old["type"], old["context"])
            self.failure_patterns[old_sig] -= 1

    def _extract_signature(self, failure_type: str, context: dict) -> str:
        """Extract identifying signature from failure context."""
        # Simple signature: type + key context elements
        keys = sorted(context.keys())[:3]  # Top 3 keys
        values = [str(context[k])[:20] for k in keys if k in context]
        return f"{failure_type}:{':'.join(values)}"

    def detect_repeating_patterns(self) -> List[dict]:
        """Detect patterns that repeat frequently."""
        repeating = []
        for signature, count in self.failure_patterns.items():
            if count >= 3:  # Threshold for "repeating"
                repeating.append(
                    {
                        "signature": signature,
                        "occurrences": count,
                        "contexts": self.context_signatures.get(signature, [])[:3],
                    }
                )

        return sorted(repeating, key=lambda x: x["occurrences"], reverse=True)

    def should_avoid(self, context: dict, action: str) -> Tuple[bool, str]:
        """Check if an action in a context should be avoided."""
        test_sig = self._extract_signature("any", context)

        for signature, count in self.failure_patterns.items():
            if count >= 2 and self._similar(test_sig, signature):
                return True, f"Similar context led to {count} previous failures"

        return False, ""

    def _similar(self, sig1: str, sig2: str) -> bool:
        """Check if two signatures are similar."""
        # Simple: share common elements
        parts1 = set(sig1.split(":"))
        parts2 = set(sig2.split(":"))
        overlap = len(parts1 & parts2)
        return overlap >= 2


class ParameterAdapter:
    """Adapts system parameters based on performance.
    Params_{t+1} = Params_t + η · UpdateSignal_t
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.current_params: Dict[str, float] = {
            "branch_count": 3.0,
            "risk_threshold": 0.5,
            "confidence_threshold": 0.6,
            "exploration_rate": 0.3,
            "attention_noise": 0.1,
        }
        self.param_history: List[dict] = []
        self.update_signals: dict[str, list[float]] = defaultdict(list)

    def compute_update_signal(
        self, param_name: str, performance_delta: float, gradient: float
    ) -> float:
        """Compute update signal for a parameter."""
        # Signal = performance change direction × gradient
        signal = performance_delta * gradient
        self.update_signals[param_name].append(signal)

        # Use moving average for stability
        if len(self.update_signals[param_name]) > 5:
            self.update_signals[param_name].pop(0)

        return statistics.mean(self.update_signals[param_name])

    def adapt(self, feedback: Dict[str, float]):
        """Adapt parameters based on feedback."""
        old_params = self.current_params.copy()

        for param_name, performance_delta in feedback.items():
            if param_name in self.current_params:
                # Compute gradient (simplified)
                gradient = 1.0 if performance_delta > 0 else -1.0

                # Get smoothed update signal
                signal = self.compute_update_signal(param_name, performance_delta, gradient)

                # Apply update: θ_{t+1} = θ_t + η · signal
                update = self.learning_rate * signal
                self.current_params[param_name] += update

                # Keep within bounds
                self.current_params[param_name] = max(
                    0.0, min(1.0, self.current_params[param_name])
                )

        # Record history
        self.param_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "old": old_params,
                "new": self.current_params.copy(),
                "feedback": feedback,
            }
        )

    def get_params(self) -> dict[str, float]:
        """Get current adapted parameters."""
        return self.current_params.copy()

    def adaptation_report(self) -> dict:
        """Generate report on parameter adaptations."""
        if len(self.param_history) < 2:
            return {"status": "insufficient_history"}

        changes = {}
        for param in self.current_params.keys():
            old_val = self.param_history[0]["old"][param]
            new_val = self.current_params[param]
            changes[param] = {
                "initial": old_val,
                "current": new_val,
                "delta": new_val - old_val,
                "change_percent": ((new_val - old_val) / (old_val + 0.001)) * 100,
            }

        return {
            "total_adaptations": len(self.param_history),
            "parameter_changes": changes,
            "most_changed": max(changes.keys(), key=lambda k: abs(changes[k]["delta"])),
        }


class ConfidenceCalibrator:
    """Calibrates confidence scores to match actual accuracy.
    Goal: Confidence ≈ Actual Success Rate
    """

    def __init__(self):
        self.confidence_predictions: List[tuple] = []  # (confidence, outcome)
        self.calibration_curve: dict[float, float] = {}

    def record(self, confidence: float, success: bool):
        """Record confidence prediction and outcome."""
        self.confidence_predictions.append((confidence, 1.0 if success else 0.0))

        # Keep window
        if len(self.confidence_predictions) > 50:
            self.confidence_predictions.pop(0)

    def get_calibration(self) -> dict:
        """Get calibration statistics."""
        if not self.confidence_predictions:
            return {"status": "no_data"}

        # Bin by confidence level
        bins = defaultdict(list)
        for conf, outcome in self.confidence_predictions:
            bin_key = round(conf * 10) / 10  # 0.1, 0.2, ..., 1.0
            bins[bin_key].append(outcome)

        # Compute calibration for each bin
        calibration = {}
        for bin_key, outcomes in bins.items():
            avg_confidence = bin_key
            avg_success = statistics.mean(outcomes)
            calibration[bin_key] = {
                "predicted": avg_confidence,
                "actual": avg_success,
                "gap": avg_confidence - avg_success,
                "sample_size": len(outcomes),
            }

        # Overall calibration
        all_confidences = [c for c, _ in self.confidence_predictions]
        all_outcomes = [o for _, o in self.confidence_predictions]

        avg_conf = statistics.mean(all_confidences)
        avg_success = statistics.mean(all_outcomes)

        return {
            "bin_calibration": calibration,
            "overall_predicted": avg_conf,
            "overall_actual": avg_success,
            "overall_gap": avg_conf - avg_success,
            "well_calibrated": abs(avg_conf - avg_success) < 0.1,
        }

    def calibrate(self, raw_confidence: float) -> float:
        """Apply calibration correction to raw confidence."""
        cal = self.get_calibration()
        if cal.get("status") == "no_data":
            return raw_confidence

        # Simple correction: adjust by overall gap
        gap = cal.get("overall_gap", 0)
        corrected = raw_confidence - gap

        return max(0.0, min(1.0, corrected))


class AMOSMetaCognition:
    """Complete AMOS Meta-cognition System

    Orchestrates all meta-cognitive functions:
    - Prediction tracking
    - Branch efficiency analysis
    - Failure pattern detection
    - Parameter adaptation
    - Confidence calibration
    """

    def __init__(self):
        self.prediction_tracker = PredictionTracker()
        self.branch_analyzer = BranchEfficiencyAnalyzer()
        self.failure_detector = FailurePatternDetector()
        self.parameter_adapter = ParameterAdapter()
        self.confidence_calibrator = ConfidenceCalibrator()

        self.reflection_history: List[ReflectionResult] = []
        self.meta_goals = [
            "improve_prediction",
            "improve_branch_efficiency",
            "reduce_failure_repetition",
            "tune_evaluator_weights",
            "calibrate_confidence",
        ]

    def reflect(self, cycle_data: dict) -> ReflectionResult:
        """Main reflection function:
        M_{t+1} = Reflect(M_t, Error_{sim}, CollapseQuality_t, MorphOutcome_t, EnergyUse_t)
        """
        insights = []
        param_updates = {}
        confidence_updates = {}

        # 1. Reflect on prediction accuracy
        if "prediction_error" in cycle_data:
            error = cycle_data["prediction_error"]
            self.prediction_tracker.record_prediction(
                cycle_data.get("predicted", {}),
                cycle_data.get("actual", {}),
                cycle_data.get("context", ""),
            )

            accuracy = self.prediction_tracker.get_accuracy()
            insights.append(f"Prediction accuracy: {accuracy:.1%}")

            if accuracy < 0.6:
                insights.append("Low prediction accuracy - increasing exploration")
                param_updates["exploration_rate"] = 0.1  # Increase exploration

        # 2. Reflect on branch efficiency
        if "branch_stats" in cycle_data:
            stats = cycle_data["branch_stats"]
            self.branch_analyzer.record_branch_generation(
                stats["n_branches"], stats["cost"], stats["selected_rank"], stats["outcome_success"]
            )

            efficiency = self.branch_analyzer.analyze_efficiency()
            insights.append(f"Branch efficiency: {efficiency.get('efficiency_ratio', 0):.2f}")

            rec = efficiency.get("recommendation", "")
            if rec == "reduce_branch_count":
                param_updates["branch_count"] = -0.2  # Reduce
                insights.append("Reducing branch count for efficiency")
            elif rec == "increase_branch_diversity":
                param_updates["branch_count"] = 0.2  # Increase
                insights.append("Increasing branch diversity")

        # 3. Reflect on failures
        if cycle_data.get("failure"):
            failure = cycle_data["failure"]
            self.failure_detector.record_failure(
                failure["type"], failure["context"], failure["action"], failure["consequence"]
            )

            patterns = self.failure_detector.detect_repeating_patterns()
            if patterns:
                top_pattern = patterns[0]
                insights.append(
                    f"Detected repeating failure pattern: {top_pattern['occurrences']} times"
                )
                param_updates["risk_threshold"] = 0.1  # Increase risk aversion

        # 4. Reflect on energy use (simplified)
        if "energy_cost" in cycle_data:
            cost = cycle_data["energy_cost"]
            if cost > 100:  # High cost threshold
                insights.append("High energy cost detected - optimizing")
                param_updates["attention_noise"] = -0.05  # Reduce noise

        # 5. Adapt parameters
        if param_updates:
            self.parameter_adapter.adapt(param_updates)
            insights.append("Parameters adapted based on reflection")

        # 6. Calibrate confidence
        if "confidence" in cycle_data and "outcome" in cycle_data:
            self.confidence_calibrator.record(cycle_data["confidence"], cycle_data["outcome"])

            calibration = self.confidence_calibrator.get_calibration()
            if not calibration.get("well_calibrated", True):
                gap = calibration.get("overall_gap", 0)
                insights.append(f"Confidence calibration gap: {gap:+.2f}")
                confidence_updates["correction"] = -gap

        # Create reflection result
        result = ReflectionResult(
            reflection_id=f"refl_{len(self.reflection_history) + 1:04d}",
            insights=insights,
            parameter_updates=param_updates,
            confidence_calibration=confidence_updates,
            learning_applied=len(param_updates) > 0 or len(confidence_updates) > 0,
        )

        self.reflection_history.append(result)
        return result

    def get_meta_status(self) -> dict:
        """Get comprehensive meta-cognitive status."""
        return {
            "total_reflections": len(self.reflection_history),
            "current_parameters": self.parameter_adapter.get_params(),
            "prediction_accuracy": self.prediction_tracker.get_accuracy(),
            "prediction_bias": self.prediction_tracker.get_bias(),
            "failure_patterns_detected": len(self.failure_detector.detect_repeating_patterns()),
            "calibration_status": self.confidence_calibrator.get_calibration(),
            "adaptation_report": self.parameter_adapter.adaptation_report(),
        }

    def suggest_improvements(self) -> List[str]:
        """Generate improvement suggestions across all domains."""
        suggestions = []

        # From prediction tracker
        suggestions.extend(self.prediction_tracker.improvement_suggestions())

        # From branch analyzer
        eff = self.branch_analyzer.analyze_efficiency()
        if eff.get("recommendation") not in ["maintain_current", "no_data"]:
            suggestions.append(f"Branch generation: {eff['recommendation']}")

        # From failure detector
        patterns = self.failure_detector.detect_repeating_patterns()
        if patterns:
            suggestions.append(
                f"Address top failure pattern ({patterns[0]['occurrences']} occurrences)"
            )

        return suggestions


def demo_meta_cognition():
    """Demonstrate AMOS Meta-cognition."""
    print("=" * 70)
    print("🧠 AMOS META-COGNITION SYSTEM - Section 13")
    print("=" * 70)
    print("\nM_{t+1} = Reflect(M_t, Error, CollapseQuality, MorphOutcome, EnergyUse)")
    print("Params_{t+1} = Params_t + η · UpdateSignal_t")
    print("=" * 70)

    # Initialize meta-cognition
    meta = AMOSMetaCognition()

    # Simulate several cycles with feedback
    print("\n[Simulating 5 cognitive cycles with learning...]")

    cycles = [
        {
            "prediction_error": 0.3,
            "predicted": {"success": 0.8, "cost": 50},
            "actual": {"success": 1.0, "cost": 45},
            "context": "cycle_1",
        },
        {
            "branch_stats": {
                "n_branches": 5,
                "cost": 80,
                "selected_rank": 2,
                "outcome_success": True,
            },
            "confidence": 0.7,
            "outcome": True,
        },
        {
            "failure": {
                "type": "timeout",
                "context": {"action": "long_computation", "timeout": 30},
                "action": "execute_heavy_task",
                "consequence": "process_killed",
            }
        },
        {
            "prediction_error": 0.2,
            "predicted": {"success": 0.9, "cost": 40},
            "actual": {"success": 1.0, "cost": 38},
            "energy_cost": 120,
            "confidence": 0.85,
            "outcome": True,
        },
        {
            "branch_stats": {
                "n_branches": 3,
                "cost": 50,
                "selected_rank": 1,
                "outcome_success": True,
            },
            "confidence": 0.9,
            "outcome": True,
        },
    ]

    for i, cycle_data in enumerate(cycles, 1):
        print(f"\n--- Cycle {i} ---")
        result = meta.reflect(cycle_data)

        print(f"Reflection ID: {result.reflection_id}")
        print(f"Learning applied: {result.learning_applied}")
        for insight in result.insights:
            print(f"  • {insight}")

    # Status report
    print("\n" + "=" * 70)
    print("META-COGNITIVE STATUS")
    print("=" * 70)
    status = meta.get_meta_status()

    print(f"\nTotal Reflections: {status['total_reflections']}")
    print(f"Prediction Accuracy: {status['prediction_accuracy']:.1%}")
    print(f"Prediction Bias: {status['prediction_bias']}")
    print(f"Failure Patterns Detected: {status['failure_patterns_detected']}")

    print("\nCurrent Parameters:")
    for param, value in status["current_parameters"].items():
        print(f"  • {param}: {value:.2f}")

    print("\nImprovement Suggestions:")
    for suggestion in meta.suggest_improvements():
        print(f"  • {suggestion}")

    print("\n" + "=" * 70)
    print("✅ AMOS META-COGNITION OPERATIONAL")
    print("=" * 70)
    print("\nMeta-cognitive Capabilities:")
    print("  • Prediction accuracy tracking")
    print("  • Branch efficiency optimization")
    print("  • Failure pattern detection")
    print("  • Parameter adaptation (gradient descent)")
    print("  • Confidence calibration")
    print("  • Continuous learning")
    print("=" * 70)


# ReflectionEngine alias for backward compatibility
class ReflectionEngine(AMOSMetaCognition):
    """Alias for AMOSMetaCognition with simplified reflect interface."""

    def reflect(self, observation: dict) -> dict:
        """Simplified reflection interface."""
        result = super().reflect(
            {
                "prediction_error": abs(
                    observation.get("prediction", 0.5) - observation.get("actual", 0.5)
                ),
                "predicted": {"value": observation.get("prediction", 0.5)},
                "actual": {"value": observation.get("actual", 0.5)},
                "confidence": observation.get("confidence", 0.8),
                "outcome": observation.get("actual", 0.5) > 0.5,
                "context": "reflection",
            }
        )
        return {
            "accuracy": 1.0
            - abs(observation.get("prediction", 0.5) - observation.get("actual", 0.5)),
            "insights": result.insights,
            "parameter_updates": result.parameter_updates,
            "learning_applied": result.learning_applied,
        }


def demo_meta_cognition():
    """Demonstrate AMOS Meta-cognition."""
    print("=" * 70)
    print("🧠 AMOS META-COGNITION SYSTEM - Section 13")
    print("=" * 70)
    print("\nM_{t+1} = Reflect(M_t, Error, CollapseQuality, MorphOutcome, EnergyUse)")
    print("Params_{t+1} = Params_t + η · UpdateSignal_t")
    print("=" * 70)

    # Initialize meta-cognition
    meta = AMOSMetaCognition()

    # Simulate several cycles with feedback
    print("\n[Simulating 5 cognitive cycles with learning...]")

    cycles = [
        {
            "prediction_error": 0.3,
            "predicted": {"success": 0.8, "cost": 50},
            "actual": {"success": 1.0, "cost": 45},
            "context": "cycle_1",
        },
        {
            "branch_stats": {
                "n_branches": 5,
                "cost": 80,
                "selected_rank": 2,
                "outcome_success": True,
            },
            "confidence": 0.7,
            "outcome": True,
        },
        {
            "failure": {
                "type": "timeout",
                "context": {"action": "long_computation", "timeout": 30},
                "action": "execute_heavy_task",
                "consequence": "process_killed",
            }
        },
        {
            "prediction_error": 0.2,
            "predicted": {"success": 0.9, "cost": 40},
            "actual": {"success": 1.0, "cost": 38},
            "energy_cost": 120,
            "confidence": 0.85,
            "outcome": True,
        },
        {
            "branch_stats": {
                "n_branches": 3,
                "cost": 50,
                "selected_rank": 1,
                "outcome_success": True,
            },
            "confidence": 0.9,
            "outcome": True,
        },
    ]

    for i, cycle_data in enumerate(cycles, 1):
        print(f"\n--- Cycle {i} ---")
        result = meta.reflect(cycle_data)

        print(f"Reflection ID: {result.reflection_id}")
        print(f"Learning applied: {result.learning_applied}")
        for insight in result.insights:
            print(f"  • {insight}")

    # Status report
    print("\n" + "=" * 70)
    print("META-COGNITIVE STATUS")
    print("=" * 70)
    status = meta.get_meta_status()

    print(f"\nTotal Reflections: {status['total_reflections']}")
    print(f"Prediction Accuracy: {status['prediction_accuracy']:.1%}")
    print(f"Prediction Bias: {status['prediction_bias']}")
    print(f"Failure Patterns Detected: {status['failure_patterns_detected']}")

    print("\nCurrent Parameters:")
    for param, value in status["current_parameters"].items():
        print(f"  • {param}: {value:.2f}")

    print("\nImprovement Suggestions:")
    for suggestion in meta.suggest_improvements():
        print(f"  • {suggestion}")

    print("\n" + "=" * 70)
    print("✅ AMOS META-COGNITION OPERATIONAL")
    print("=" * 70)
    print("\nMeta-cognitive Capabilities:")
    print("  • Prediction accuracy tracking")
    print("  • Branch efficiency optimization")
    print("  • Failure pattern detection")
    print("  • Parameter adaptation (gradient descent)")
    print("  • Confidence calibration")
    print("  • Continuous learning")
    print("=" * 70)


if __name__ == "__main__":
    demo_meta_cognition()

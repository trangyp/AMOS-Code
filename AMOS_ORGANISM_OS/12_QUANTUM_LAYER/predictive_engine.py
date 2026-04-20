#!/usr/bin/env python3
"""AMOS Predictive Analytics Engine
=================================

Forecasts task completion times, subsystem load, and resource usage.
Uses historical data and probabilistic models for predictions.

Owner: Trang
Version: 1.0.0
"""

import json
import statistics
from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC, timedelta
from pathlib import Path
from typing import Any


@dataclass
class Prediction:
    """A single prediction result."""

    metric: str
    predicted_value: float
    confidence: float
    lower_bound: float
    upper_bound: float
    timestamp: str
    horizon: str


@dataclass
class TaskPrediction:
    """Prediction for a specific task."""

    task_id: str
    task_type: str
    priority: str
    predicted_duration_ms: float
    confidence: float
    std_dev: float = 0.0
    assigned_agent: str = None
    recommended_start: str = ""
    estimated_completion: str = ""


class PredictiveEngine:
    """Predictive analytics engine for AMOS organism.
    Forecasts performance, load, and resource usage.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.analytics_dir = organism_root / "12_QUANTUM_LAYER" / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # Historical data storage
        self.execution_history: list[dict[str, Any]] = []
        self.subsystem_metrics: dict[str, list[dict]] = {}

        # Load historical data
        self._load_history()

        # Baseline metrics for predictions
        self.baseline_durations = {
            "analysis": {"mean": 500, "std": 200},
            "code": {"mean": 1200, "std": 500},
            "documentation": {"mean": 800, "std": 300},
            "security": {"mean": 600, "std": 250},
            "test": {"mean": 1000, "std": 400},
        }

        # Priority multipliers
        self.priority_multipliers = {
            "CRITICAL": 0.7,  # Critical tasks get priority (faster)
            "HIGH": 0.85,
            "MEDIUM": 1.0,
            "LOW": 1.3,  # Low priority tasks may wait longer
        }

    def _load_history(self) -> None:
        """Load historical execution data."""
        history_file = self.analytics_dir / "execution_history.json"
        if history_file.exists():
            try:
                with open(history_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.execution_history = data.get("executions", [])
                    self.subsystem_metrics = data.get("subsystem_metrics", {})
            except Exception as e:
                print(f"[PREDICTIVE] Error loading history: {e}")

    def _save_history(self) -> None:
        """Save historical data."""
        history_file = self.analytics_dir / "execution_history.json"
        data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "total_executions": len(self.execution_history),
            "executions": self.execution_history[-1000:],  # Keep last 1000
            "subsystem_metrics": self.subsystem_metrics,
        }
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def record_execution(
        self, task_type: str, priority: str, duration_ms: float, agent_id: str, success: bool
    ) -> None:
        """Record execution for future predictions."""
        self.execution_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "task_type": task_type,
                "priority": priority,
                "duration_ms": duration_ms,
                "agent_id": agent_id,
                "success": success,
            }
        )
        self._save_history()

    def predict_task_duration(
        self, task_type: str, priority: str, agent_id: str = None
    ) -> TaskPrediction:
        """Predict duration for a task."""
        # Get baseline for task type
        baseline = self.baseline_durations.get(task_type, {"mean": 1000, "std": 400})

        # Apply priority multiplier
        multiplier = self.priority_multipliers.get(priority, 1.0)

        # Calculate prediction
        predicted_duration = baseline["mean"] * multiplier

        # Adjust confidence based on data availability
        historical_count = sum(1 for e in self.execution_history if e["task_type"] == task_type)

        if historical_count >= 10:
            # Use historical data for better prediction
            type_history = [
                e["duration_ms"]
                for e in self.execution_history
                if e["task_type"] == task_type and e["success"]
            ]
            if type_history:
                predicted_duration = statistics.mean(type_history) * multiplier
                std_dev = (
                    statistics.stdev(type_history) if len(type_history) > 1 else baseline["std"]
                )
                confidence = min(0.95, 0.7 + (historical_count / 100))
            else:
                std_dev = baseline["std"]
                confidence = 0.7
        else:
            std_dev = baseline["std"]
            confidence = 0.6

        # Calculate time estimates
        now = datetime.now(UTC)
        recommended_start = now.isoformat()
        estimated_completion = (now + timedelta(milliseconds=predicted_duration)).isoformat()

        return TaskPrediction(
            task_id="",
            task_type=task_type,
            priority=priority,
            predicted_duration_ms=predicted_duration,
            confidence=confidence,
            std_dev=std_dev,
            assigned_agent=agent_id,
            recommended_start=recommended_start,
            estimated_completion=estimated_completion,
        )

    def predict_queue_clearance(self, pending_count: int) -> Prediction:
        """Predict when pending queue will be cleared."""
        if pending_count == 0:
            return Prediction(
                metric="queue_clearance_time",
                predicted_value=0,
                confidence=1.0,
                lower_bound=0,
                upper_bound=0,
                timestamp=datetime.now(UTC).isoformat(),
                horizon="immediate",
            )

        # Average processing rate (tasks per second)
        avg_duration = 800  # ms per task
        processing_rate = 1000 / avg_duration  # tasks per second

        # Estimated clearance time
        clearance_seconds = pending_count / processing_rate

        # Add variance
        variance = clearance_seconds * 0.2  # 20% variance

        return Prediction(
            metric="queue_clearance_time",
            predicted_value=clearance_seconds,
            confidence=0.75,
            lower_bound=max(0, clearance_seconds - variance),
            upper_bound=clearance_seconds + variance,
            timestamp=datetime.now(UTC).isoformat(),
            horizon=f"{int(clearance_seconds)}s",
        )

    def predict_subsystem_load(self, subsystem: str, horizon_minutes: int = 5) -> Prediction:
        """Predict load for a subsystem."""
        # Get historical load data
        metrics = self.subsystem_metrics.get(subsystem, [])

        if len(metrics) >= 3:
            recent_loads = [m.get("load", 50) for m in metrics[-10:]]
            avg_load = statistics.mean(recent_loads)
            trend = recent_loads[-1] - recent_loads[0]

            # Project forward
            predicted_load = avg_load + (trend * horizon_minutes / 5)
            predicted_load = max(0, min(100, predicted_load))

            std_dev = statistics.stdev(recent_loads) if len(recent_loads) > 1 else 10
            confidence = min(0.9, 0.6 + (len(metrics) / 50))
        else:
            # Default prediction
            predicted_load = 50
            std_dev = 15
            confidence = 0.5

        return Prediction(
            metric=f"{subsystem}_load",
            predicted_value=predicted_load,
            confidence=confidence,
            lower_bound=max(0, predicted_load - std_dev),
            upper_bound=min(100, predicted_load + std_dev),
            timestamp=datetime.now(UTC).isoformat(),
            horizon=f"{horizon_minutes}m",
        )

    def predict_resource_usage(self, resource_type: str, horizon_hours: int = 24) -> Prediction:
        """Predict resource usage (compute, storage, budget)."""
        if resource_type == "compute":
            base = 45  # % CPU
            growth_rate = 0.5  # % per hour
        elif resource_type == "storage":
            base = 30  # % disk
            growth_rate = 0.2
        elif resource_type == "budget":
            base = 25  # % budget used
            growth_rate = 1.0
        else:
            base = 50
            growth_rate = 0.3

        predicted = base + (growth_rate * horizon_hours)
        variance = predicted * 0.15

        return Prediction(
            metric=f"{resource_type}_usage",
            predicted_value=predicted,
            confidence=0.7,
            lower_bound=max(0, predicted - variance),
            upper_bound=min(100, predicted + variance),
            timestamp=datetime.now(UTC).isoformat(),
            horizon=f"{horizon_hours}h",
        )

    def get_all_predictions(self) -> dict[str, Any]:
        """Get comprehensive predictions for all systems."""
        # Load current queue status
        try:
            import sys

            sys.path.insert(0, str(self.root / "07_METABOLISM"))
            from task_queue import TaskQueue

            queue = TaskQueue(self.root)
            queue_status = queue.get_status()
            pending_count = queue_status.get("pending", 0)
        except Exception:
            pending_count = 0

        predictions = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "queue": {
                "pending_tasks": pending_count,
                "clearance_prediction": self.predict_queue_clearance(pending_count).__dict__,
            },
            "subsystems": {},
            "resources": {},
            "task_types": {},
        }

        # Predict for all subsystems
        for subsystem in [
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_SKELETON",
            "06_MUSCLE",
            "07_METABOLISM",
        ]:
            pred = self.predict_subsystem_load(subsystem, horizon_minutes=5)
            predictions["subsystems"][subsystem] = pred.__dict__

        # Resource predictions
        for resource in ["compute", "storage", "budget"]:
            pred = self.predict_resource_usage(resource, horizon_hours=24)
            predictions["resources"][resource] = pred.__dict__

        # Task type predictions
        for task_type in ["analysis", "code", "documentation", "security"]:
            pred = self.predict_task_duration(task_type, "MEDIUM")
            predictions["task_types"][task_type] = {
                "predicted_duration_ms": pred.predicted_duration_ms,
                "confidence": pred.confidence,
                "estimated_seconds": pred.predicted_duration_ms / 1000,
            }

        return predictions

    def get_forecast_summary(self) -> str:
        """Generate human-readable forecast summary."""
        predictions = self.get_all_predictions()

        lines = [
            "AMOS Predictive Forecast",
            "=" * 40,
            f"Generated: {predictions['timestamp']}",
            "",
            "Queue Status:",
            f"  Pending tasks: {predictions['queue']['pending_tasks']}",
        ]

        if predictions["queue"]["pending_tasks"] > 0:
            clearance = predictions["queue"]["clearance_prediction"]
            lines.append(f"  Estimated clearance: {clearance['horizon']}")

        lines.extend(
            [
                "",
                "Subsystem Load (5min forecast):",
            ]
        )

        for subsys, pred in predictions["subsystems"].items():
            load = pred["predicted_value"]
            status = "HIGH" if load > 80 else "MEDIUM" if load > 50 else "LOW"
            lines.append(f"  {subsys}: {load:.1f}% ({status})")

        lines.extend(
            [
                "",
                "Resource Usage (24h forecast):",
            ]
        )

        for resource, pred in predictions["resources"].items():
            usage = pred["predicted_value"]
            lines.append(f"  {resource}: {usage:.1f}%")

        lines.extend(
            [
                "",
                "Task Duration Estimates:",
            ]
        )

        for task_type, pred in predictions["task_types"].items():
            seconds = pred["estimated_seconds"]
            conf = pred["confidence"] * 100
            lines.append(f"  {task_type}: ~{seconds:.1f}s (conf: {conf:.0f}%)")

        return "\n".join(lines)


def main() -> int:
    """CLI for Predictive Engine."""
    print("=" * 50)
    print("AMOS Predictive Analytics Engine")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    engine = PredictiveEngine(organism_root)

    # Show forecast
    print("\n" + engine.get_forecast_summary())

    # Example: Predict specific task
    print("\n" + "=" * 40)
    print("Example Predictions:")
    print("=" * 40)

    for task_type in ["analysis", "code", "security"]:
        for priority in ["MEDIUM", "HIGH", "CRITICAL"]:
            pred = engine.predict_task_duration(task_type, priority)
            print(f"\n{priority} {task_type}:")
            print(f"  Duration: {pred.predicted_duration_ms:.0f}ms")
            print(f"  Confidence: {pred.confidence * 100:.0f}%")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

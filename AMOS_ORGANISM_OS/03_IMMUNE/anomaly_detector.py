#!/usr/bin/env python3
"""AMOS Anomaly Detection System
==============================

Monitors subsystem behavior and detects unusual patterns.
Alerts on anomalies and suggests remediation actions.

Owner: Trang
Version: 1.0.0
"""

import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of anomalies detected."""

    HIGH_LOAD = "high_load"
    SLOW_RESPONSE = "slow_response"
    ERROR_SPIKE = "error_spike"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNUSUAL_PATTERN = "unusual_pattern"
    SUBSYSTEM_DOWN = "subsystem_down"


@dataclass
class Anomaly:
    """Detected anomaly."""

    id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    subsystem: str
    metric: str
    expected_value: float
    actual_value: float
    deviation_percent: float
    timestamp: str
    description: str
    remediation: List[str]
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MetricBaseline:
    """Baseline metrics for comparison."""

    metric_name: str
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    sample_count: int
    last_updated: str


class AnomalyDetector:
    """Anomaly detection system for AMOS organism.
    Uses statistical methods to identify unusual behavior.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.immune_dir = organism_root / "03_IMMUNE"
        self.analytics_dir = self.immune_dir / "anomaly_detection"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.baselines: Dict[str, MetricBaseline] = {}
        self.anomalies: List[Anomaly] = []
        self.recent_metrics: Dict[str, list[float]] = {}

        # Detection thresholds
        self.thresholds = {
            "warning": 2.0,  # 2 standard deviations
            "critical": 3.5,  # 3.5 standard deviations
        }

        # Load existing data
        self._load_baselines()
        self._load_anomalies()

    def _load_baselines(self) -> None:
        """Load metric baselines from disk."""
        baseline_file = self.analytics_dir / "baselines.json"
        if baseline_file.exists():
            try:
                with open(baseline_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for metric, baseline_data in data.get("baselines", {}).items():
                        self.baselines[metric] = MetricBaseline(
                            metric_name=metric,
                            mean=baseline_data["mean"],
                            std_dev=baseline_data["std_dev"],
                            min_value=baseline_data["min_value"],
                            max_value=baseline_data["max_value"],
                            sample_count=baseline_data["sample_count"],
                            last_updated=baseline_data["last_updated"],
                        )
            except Exception as e:
                print(f"[ANOMALY] Error loading baselines: {e}")

    def _save_baselines(self) -> None:
        """Save metric baselines to disk."""
        baseline_file = self.analytics_dir / "baselines.json"
        data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "baselines": {
                metric: {
                    "mean": b.mean,
                    "std_dev": b.std_dev,
                    "min_value": b.min_value,
                    "max_value": b.max_value,
                    "sample_count": b.sample_count,
                    "last_updated": b.last_updated,
                }
                for metric, b in self.baselines.items()
            },
        }
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_anomalies(self) -> None:
        """Load anomaly history from disk."""
        anomalies_file = self.analytics_dir / "anomalies.json"
        if anomalies_file.exists():
            try:
                with open(anomalies_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for anomaly_data in data.get("anomalies", []):
                        self.anomalies.append(
                            Anomaly(
                                id=anomaly_data["id"],
                                anomaly_type=AnomalyType(anomaly_data["anomaly_type"]),
                                severity=AnomalySeverity(anomaly_data["severity"]),
                                subsystem=anomaly_data["subsystem"],
                                metric=anomaly_data["metric"],
                                expected_value=anomaly_data["expected_value"],
                                actual_value=anomaly_data["actual_value"],
                                deviation_percent=anomaly_data["deviation_percent"],
                                timestamp=anomaly_data["timestamp"],
                                description=anomaly_data["description"],
                                remediation=anomaly_data["remediation"],
                                acknowledged=anomaly_data.get("acknowledged", False),
                                resolved=anomaly_data.get("resolved", False),
                            )
                        )
            except Exception as e:
                print(f"[ANOMALY] Error loading anomalies: {e}")

    def _save_anomalies(self) -> None:
        """Save anomalies to disk."""
        anomalies_file = self.analytics_dir / "anomalies.json"
        data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "total_count": len(self.anomalies),
            "active_count": len(self.get_active_anomalies()),
            "anomalies": [
                {
                    "id": a.id,
                    "anomaly_type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "subsystem": a.subsystem,
                    "metric": a.metric,
                    "expected_value": a.expected_value,
                    "actual_value": a.actual_value,
                    "deviation_percent": a.deviation_percent,
                    "timestamp": a.timestamp,
                    "description": a.description,
                    "remediation": a.remediation,
                    "acknowledged": a.acknowledged,
                    "resolved": a.resolved,
                }
                for a in self.anomalies[-200:]  # Keep last 200
            ],
        }
        with open(anomalies_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def update_baseline(self, metric_name: str, value: float) -> None:
        """Update baseline for a metric with new sample."""
        if metric_name not in self.recent_metrics:
            self.recent_metrics[metric_name] = []

        self.recent_metrics[metric_name].append(value)

        # Keep last 100 samples
        if len(self.recent_metrics[metric_name]) > 100:
            self.recent_metrics[metric_name] = self.recent_metrics[metric_name][-100:]

        # Update baseline if we have enough samples
        samples = self.recent_metrics[metric_name]
        if len(samples) >= 10:
            mean = statistics.mean(samples)
            std_dev = statistics.stdev(samples) if len(samples) > 1 else 0

            self.baselines[metric_name] = MetricBaseline(
                metric_name=metric_name,
                mean=mean,
                std_dev=std_dev if std_dev > 0 else 1.0,  # Avoid division by zero
                min_value=min(samples),
                max_value=max(samples),
                sample_count=len(samples),
                last_updated=datetime.now(UTC).isoformat(),
            )

            self._save_baselines()

    def detect_anomaly(self, subsystem: str, metric: str, value: float) -> Optional[Anomaly]:
        """Detect if a metric value is anomalous."""
        metric_key = f"{subsystem}.{metric}"

        # Update baseline first
        self.update_baseline(metric_key, value)

        # Check if we have enough baseline data
        if metric_key not in self.baselines:
            return None

        baseline = self.baselines[metric_key]

        # Calculate deviation in standard deviations
        if baseline.std_dev == 0:
            return None

        deviation = abs(value - baseline.mean) / baseline.std_dev

        # Determine severity
        if deviation >= self.thresholds["critical"]:
            severity = AnomalySeverity.CRITICAL
        elif deviation >= self.thresholds["warning"]:
            severity = AnomalySeverity.WARNING
        else:
            return None

        # Determine anomaly type
        if metric == "load" and value > baseline.mean:
            anomaly_type = AnomalyType.HIGH_LOAD
        elif metric == "response_time" and value > baseline.mean:
            anomaly_type = AnomalyType.SLOW_RESPONSE
        elif metric == "error_rate" and value > baseline.mean:
            anomaly_type = AnomalyType.ERROR_SPIKE
        elif metric == "cpu" or metric == "memory":
            anomaly_type = AnomalyType.RESOURCE_EXHAUSTION
        else:
            anomaly_type = AnomalyType.UNUSUAL_PATTERN

        # Calculate deviation percent
        if baseline.mean != 0:
            deviation_percent = ((value - baseline.mean) / baseline.mean) * 100
        else:
            deviation_percent = 0

        # Generate remediation suggestions
        remediation = self._generate_remediation(anomaly_type, subsystem, metric)

        # Create anomaly
        anomaly = Anomaly(
            id=f"anom_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{len(self.anomalies)}",
            anomaly_type=anomaly_type,
            severity=severity,
            subsystem=subsystem,
            metric=metric,
            expected_value=baseline.mean,
            actual_value=value,
            deviation_percent=deviation_percent,
            timestamp=datetime.now(UTC).isoformat(),
            description=f"{anomaly_type.value} detected in {subsystem}:{metric} "
            f"(expected {baseline.mean:.2f}, got {value:.2f}, "
            f"deviation: {deviation:.1f}σ)",
            remediation=remediation,
        )

        self.anomalies.append(anomaly)
        self._save_anomalies()

        print(f"[ANOMALY] {severity.value.upper()}: {anomaly.description}")

        return anomaly

    def _generate_remediation(
        self, anomaly_type: AnomalyType, subsystem: str, metric: str
    ) -> List[str]:
        """Generate remediation suggestions based on anomaly type."""
        remediation_map = {
            AnomalyType.HIGH_LOAD: [
                f"Scale up {subsystem} resources",
                "Distribute load across multiple agents",
                "Enable request throttling",
            ],
            AnomalyType.SLOW_RESPONSE: [
                "Check database query performance",
                "Enable caching layer",
                "Optimize algorithm complexity",
            ],
            AnomalyType.ERROR_SPIKE: [
                "Review recent code changes",
                "Check external service health",
                "Enable circuit breaker pattern",
            ],
            AnomalyType.RESOURCE_EXHAUSTION: [
                "Increase resource allocation",
                "Enable resource cleanup",
                "Restart subsystem if necessary",
            ],
            AnomalyType.UNUSUAL_PATTERN: [
                "Monitor for continued unusual behavior",
                "Review recent configuration changes",
                "Check for external factors",
            ],
            AnomalyType.SUBSYSTEM_DOWN: [
                "Attempt automatic restart",
                "Route traffic to backup subsystem",
                "Notify operations team",
            ],
        }

        return remediation_map.get(anomaly_type, ["Investigate root cause"])

    def check_all_subsystems(self) -> List[Anomaly]:
        """Run anomaly detection on all subsystems."""
        detected = []

        # Simulate checking various metrics for each subsystem
        subsystems = [
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_SKELETON",
            "06_MUSCLE",
            "07_METABOLISM",
            "08_WORLD_MODEL",
            "09_SOCIAL_ENGINE",
            "10_LIFE_ENGINE",
            "11_LEGAL_BRAIN",
            "12_QUANTUM_LAYER",
            "13_FACTORY",
        ]

        for subsystem in subsystems:
            # Check load (simulated)
            import random

            load = random.gauss(50, 15)  # Normal around 50%
            if random.random() < 0.1:  # 10% chance of anomaly
                load = random.gauss(85, 10)  # High load

            anomaly = self.detect_anomaly(subsystem, "load", load)
            if anomaly:
                detected.append(anomaly)

        return detected

    def get_active_anomalies(self) -> List[Anomaly]:
        """Get all unresolved anomalies."""
        cutoff = (datetime.now(UTC) - timedelta(hours=24)).isoformat()
        return [a for a in self.anomalies if not a.resolved and a.timestamp > cutoff]

    def acknowledge_anomaly(self, anomaly_id: str) -> bool:
        """Acknowledge an anomaly."""
        for anomaly in self.anomalies:
            if anomaly.id == anomaly_id:
                anomaly.acknowledged = True
                self._save_anomalies()
                return True
        return False

    def resolve_anomaly(self, anomaly_id: str) -> bool:
        """Mark an anomaly as resolved."""
        for anomaly in self.anomalies:
            if anomaly.id == anomaly_id:
                anomaly.resolved = True
                self._save_anomalies()
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get detector status."""
        active = self.get_active_anomalies()
        critical = sum(1 for a in active if a.severity == AnomalySeverity.CRITICAL)
        warning = sum(1 for a in active if a.severity == AnomalySeverity.WARNING)

        return {
            "status": "operational",
            "active_anomalies": len(active),
            "critical": critical,
            "warning": warning,
            "baselines_tracked": len(self.baselines),
            "total_detected": len(self.anomalies),
        }

    def get_health_score(self) -> float:
        """Calculate overall health score based on anomalies."""
        active = self.get_active_anomalies()
        if not active:
            return 100.0

        # Critical anomalies reduce score more
        critical_penalty = sum(20 for a in active if a.severity == AnomalySeverity.CRITICAL)
        warning_penalty = sum(5 for a in active if a.severity == AnomalySeverity.WARNING)

        return max(0.0, 100.0 - critical_penalty - warning_penalty)


def main() -> int:
    """CLI for Anomaly Detection."""
    print("=" * 50)
    print("AMOS Anomaly Detection System")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    detector = AnomalyDetector(organism_root)

    print("\nRunning anomaly detection scan...")
    detected = detector.check_all_subsystems()

    if detected:
        print(f"\nDetected {len(detected)} anomalies:")
        for a in detected:
            icon = "🔴" if a.severity == AnomalySeverity.CRITICAL else "🟡"
            print(f"\n{icon} {a.severity.value.upper()}: {a.subsystem}")
            print(f"   {a.description}")
            print("   Remediation:")
            for r in a.remediation:
                print(f"     • {r}")
    else:
        print("\n✓ No anomalies detected")

    # Show status
    status = detector.get_status()
    health = detector.get_health_score()

    print("\nDetector Status:")
    print(f"  Health Score: {health:.1f}%")
    print(f"  Active: {status['active_anomalies']}")
    print(f"  Critical: {status['critical']}")
    print(f"  Warning: {status['warning']}")
    print(f"  Baselines: {status['baselines_tracked']}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

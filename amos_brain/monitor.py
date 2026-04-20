"""AMOS Brain Cognitive Monitor - Observability and monitoring system."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from .laws import GlobalLaws

UTC = UTC

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: float
    metric_type: str
    value: float
    labels: dict[str, str]


@dataclass
class Alert:
    """Monitoring alert."""

    alert_id: str
    timestamp: str
    severity: str
    metric: str
    threshold: float
    actual_value: float
    message: str
    acknowledged: bool = False


class CognitiveMonitor:
    """AMOS Brain Cognitive Monitor.

    Provides observability and monitoring:
    1. Real-time metrics collection
    2. Law compliance dashboards
    3. Performance analytics
    4. Anomaly detection
    5. Alerting system
    6. Decision audit logging
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".amos_brain" / "monitor"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._metrics: list[MetricPoint] = []
        self._alerts: list[Alert] = []
        self._audit_log: list[dict] = []
        self._hooks: list[Callable] = []

        # Thresholds
        self.thresholds = {
            "reasoning_time_ms": 5000,  # Alert if reasoning takes >5s
            "law_violation_rate": 0.1,  # Alert if >10% violations
            "error_rate": 0.05,  # Alert if >5% errors
        }

        self._start_time = time.time()

    def record_reasoning(
        self,
        task_description: str,
        processing_time_ms: int,
        law_violations: int,
        confidence: str,
        kernels_used: list[str],
    ):
        """Record reasoning metrics."""
        timestamp = time.time()

        # Record metrics
        self._metrics.append(
            MetricPoint(
                timestamp=timestamp,
                metric_type="reasoning_time_ms",
                value=processing_time_ms,
                labels={"confidence": confidence},
            )
        )

        self._metrics.append(
            MetricPoint(
                timestamp=timestamp,
                metric_type="law_violations",
                value=law_violations,
                labels={"task": task_description[:50]},
            )
        )

        self._metrics.append(
            MetricPoint(
                timestamp=timestamp,
                metric_type="kernels_activated",
                value=len(kernels_used),
                labels={"kernels": ",".join(kernels_used[:3])},
            )
        )

        # Check thresholds
        if processing_time_ms > self.thresholds["reasoning_time_ms"]:
            self._create_alert(
                severity="warning",
                metric="reasoning_time_ms",
                threshold=self.thresholds["reasoning_time_ms"],
                actual_value=processing_time_ms,
                message=f"Slow reasoning: {processing_time_ms}ms for '{task_description[:30]}...'",
            )

        # Audit log
        self._audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "reasoning_complete",
                "task": task_description[:100],
                "processing_time_ms": processing_time_ms,
                "law_violations": law_violations,
                "confidence": confidence,
                "kernels": kernels_used,
            }
        )

        self._trigger_hooks("reasoning", task_description, processing_time_ms)

    def record_tool_decision(
        self, tool_name: str, approved: bool, risk_level: str, violations: list[dict]
    ):
        """Record tool decision metrics."""
        timestamp = time.time()

        self._metrics.append(
            MetricPoint(
                timestamp=timestamp,
                metric_type="tool_decision",
                value=1 if approved else 0,
                labels={"tool": tool_name, "risk": risk_level},
            )
        )

        self._metrics.append(
            MetricPoint(
                timestamp=timestamp,
                metric_type="tool_violations",
                value=len(violations),
                labels={"tool": tool_name},
            )
        )

        # Alert on dangerous blocks
        if not approved and risk_level == "high":
            self._create_alert(
                severity="info",
                metric="tool_blocked",
                threshold=0,
                actual_value=1,
                message=f"Blocked high-risk tool: {tool_name}",
            )

        self._audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "tool_decision",
                "tool": tool_name,
                "approved": approved,
                "risk_level": risk_level,
                "violations": violations,
            }
        )

    def record_law_compliance(self, law_id: str, compliant: bool, context: str):
        """Record law compliance check."""
        self._metrics.append(
            MetricPoint(
                timestamp=time.time(),
                metric_type="law_compliance",
                value=1 if compliant else 0,
                labels={"law": law_id, "context": context[:30]},
            )
        )

        if not compliant:
            self._create_alert(
                severity="warning",
                metric=f"law_{law_id}",
                threshold=1,
                actual_value=0,
                message=f"Law {law_id} violation in {context[:50]}...",
            )

    def get_metrics_summary(self, window_seconds: int = 3600) -> dict:
        """Get metrics summary for time window."""
        cutoff = time.time() - window_seconds
        recent = [m for m in self._metrics if m.timestamp > cutoff]

        if not recent:
            return {"error": "No metrics in time window"}

        # Calculate aggregates
        reasoning_times = [m.value for m in recent if m.metric_type == "reasoning_time_ms"]
        violations = [m.value for m in recent if m.metric_type == "law_violations"]
        tool_decisions = [m for m in recent if m.metric_type == "tool_decision"]

        approved = sum(1 for m in tool_decisions if m.value == 1)
        blocked = len(tool_decisions) - approved

        return {
            "window_seconds": window_seconds,
            "total_metrics": len(recent),
            "reasoning": {
                "count": len(reasoning_times),
                "avg_time_ms": sum(reasoning_times) / len(reasoning_times)
                if reasoning_times
                else 0,
                "max_time_ms": max(reasoning_times) if reasoning_times else 0,
            },
            "compliance": {
                "total_violations": sum(violations),
                "avg_violations_per_task": sum(violations) / len(violations) if violations else 0,
            },
            "tools": {
                "total_decisions": len(tool_decisions),
                "approved": approved,
                "blocked": blocked,
                "block_rate": blocked / len(tool_decisions) if tool_decisions else 0,
            },
            "alerts_active": len([a for a in self._alerts if not a.acknowledged]),
        }

    def get_law_compliance_dashboard(self) -> dict:
        """Get law compliance dashboard."""
        laws = GlobalLaws()
        compliance = {}

        for law_id in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            law = laws.get_law(law_id)
            if law:
                # Get metrics for this law
                law_metrics = [
                    m
                    for m in self._metrics
                    if m.metric_type == "law_compliance" and m.labels.get("law") == law_id
                ]

                if law_metrics:
                    compliant_count = sum(1 for m in law_metrics if m.value == 1)
                    total = len(law_metrics)
                    compliance[law_id] = {
                        "name": law.name,
                        "compliance_rate": compliant_count / total,
                        "checks": total,
                        "violations": total - compliant_count,
                    }
                else:
                    compliance[law_id] = {
                        "name": law.name,
                        "compliance_rate": 1.0,
                        "checks": 0,
                        "violations": 0,
                    }

        return compliance

    def detect_anomalies(self) -> list[dict]:
        """Detect anomalies in recent metrics."""
        anomalies = []

        # Check for sudden spikes in reasoning time
        recent_times = [
            m.value for m in self._metrics[-20:] if m.metric_type == "reasoning_time_ms"
        ]
        if len(recent_times) >= 10:
            avg = sum(recent_times[:-5]) / len(recent_times[:-5])
            recent_avg = sum(recent_times[-5:]) / 5

            if avg > 0 and recent_avg > avg * 2:  # 2x spike
                anomalies.append(
                    {
                        "type": "reasoning_time_spike",
                        "severity": "warning",
                        "message": f"Reasoning time increased {recent_avg / avg:.1f}x",
                        "avg_before": avg,
                        "avg_recent": recent_avg,
                    }
                )

        # Check for high violation rates
        recent_violations = [
            m.value for m in self._metrics[-20:] if m.metric_type == "law_violations"
        ]
        if recent_violations:
            violation_rate = sum(1 for v in recent_violations if v > 0) / len(recent_violations)
            if violation_rate > self.thresholds["law_violation_rate"]:
                anomalies.append(
                    {
                        "type": "high_violation_rate",
                        "severity": "critical",
                        "message": f"High law violation rate: {violation_rate:.1%}",
                        "rate": violation_rate,
                    }
                )

        return anomalies

    def get_alerts(self, acknowledged: bool = None) -> list[Alert]:
        """Get alerts, optionally filtered."""
        if acknowledged is None:
            return self._alerts
        return [a for a in self._alerts if a.acknowledged == acknowledged]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def export_audit_log(self, filepath: Optional[Path] = None) -> Path:
        """Export audit log to file."""
        if filepath is None:
            filepath = self.storage_path / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, "w") as f:
            json.dump(self._audit_log, f, indent=2, default=str)

        return filepath

    def register_hook(self, callback: Callable):
        """Register callback for monitoring events."""
        self._hooks.append(callback)

    def _create_alert(
        self, severity: str, metric: str, threshold: float, actual_value: float, message: str
    ):
        """Create a monitoring alert."""
        alert = Alert(
            alert_id=f"ALERT-{len(self._alerts) + 1:04d}",
            timestamp=datetime.now().isoformat(),
            severity=severity,
            metric=metric,
            threshold=threshold,
            actual_value=actual_value,
            message=message,
        )
        self._alerts.append(alert)

        self._trigger_hooks("alert", alert)

    def _trigger_hooks(self, event_type: str, *data: Any):
        """Trigger registered hooks."""
        for hook in self._hooks:
            try:
                hook(event_type, *data)
            except Exception as e:
                logger.debug(f"Hook execution failed: {e}")


@lru_cache(maxsize=1)
def get_monitor() -> CognitiveMonitor:
    """Get or create global monitor instance (singleton)."""
    return CognitiveMonitor()

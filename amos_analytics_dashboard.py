#!/usr/bin/env python3
"""AMOS Analytics & Monitoring Dashboard (Layer 26)
=================================================

Real-time analytics and monitoring for AMOS Brain v20.
Provides comprehensive observability across all 25+ layers.

Features:
- Real-time system metrics
- Layer performance tracking
- Cognitive analytics
- Law compliance monitoring
- Multi-agent coordination stats
- Knowledge engine usage
- Interactive dashboard API

Usage:
    python amos_analytics_dashboard.py --start    # Start dashboard
    python amos_analytics_dashboard.py --metrics  # Show metrics
    python amos_analytics_dashboard.py --report   # Generate report

Creator: Trang Phan
System: AMOS vInfinity - Layer 26
"""

import argparse
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class LayerMetrics:
    """Metrics for a single layer."""

    layer_id: int
    name: str
    requests: int = 0
    errors: int = 0
    avg_response_time: float = 0.0
    status: str = "active"
    last_active: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SystemMetrics:
    """System-wide metrics."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    uptime_seconds: float = 0.0
    total_requests: int = 0
    total_errors: int = 0
    active_layers: int = 0
    cache_hit_rate: float = 0.0
    law_violations: int = 0
    active_agents: int = 0
    engines_loaded: int = 0


class AnalyticsDashboard:
    """Analytics & Monitoring Dashboard - Layer 26.

    Provides comprehensive observability:
    - Real-time layer performance tracking
    - Cognitive analytics (think/decide patterns)
    - Law compliance monitoring
    - Cache performance
    - Multi-agent coordination stats
    - Knowledge engine usage analytics
    - Historical trend analysis

    Integrates with all 25 previous layers for full visibility.
    """

    VERSION = "26.0.0"
    LAYERS_SUPPORTED = 25

    def __init__(self):
        self.start_time = time.time()
        self.layer_metrics: Dict[int, LayerMetrics] = {}
        self.system_metrics = SystemMetrics()
        self.historical_data: List[SystemMetrics] = []
        self._initialize_layer_tracking()

    def _initialize_layer_tracking(self) -> None:
        """Initialize tracking for all 25 layers."""
        layer_names = {
            1: "Brain Loader",
            2: "Cognitive Stack",
            3: "Kernel Router",
            4: "Task Processor",
            5: "Global Laws",
            6: "Agent Bridge",
            7: "State Manager",
            8: "Meta Controller",
            9: "Monitor",
            10: "Facade",
            11: "Config",
            12: "Cookbook",
            13: "Demos",
            14: "ClawSpring",
            15: "Documentation",
            16: "Integration Test",
            17: "Cookbook Fix",
            18: "Organism Bridge",
            19: "Unified API",
            20: "Ecosystem Integrator",
            21: "Production Deployment",
            22: "Final Validation",
            23: "Knowledge Engine",
            24: "Multi-Agent Orchestrator",
            25: "Performance Engine",
        }

        for i in range(1, self.LAYERS_SUPPORTED + 1):
            self.layer_metrics[i] = LayerMetrics(layer_id=i, name=layer_names.get(i, f"Layer {i}"))

    def record_request(self, layer: int, response_time: float, error: bool = False) -> None:
        """Record a request for a specific layer."""
        if layer in self.layer_metrics:
            metric = self.layer_metrics[layer]
            metric.requests += 1
            if error:
                metric.errors += 1
            # Update average response time
            metric.avg_response_time = (
                metric.avg_response_time * (metric.requests - 1) + response_time
            ) / metric.requests
            metric.last_active = datetime.now(UTC).isoformat()

        self.system_metrics.total_requests += 1
        if error:
            self.system_metrics.total_errors += 1

    def record_law_violation(self) -> None:
        """Record a law compliance violation."""
        self.system_metrics.law_violations += 1

    def update_cache_metrics(self, hit_rate: float) -> None:
        """Update cache performance metrics."""
        self.system_metrics.cache_hit_rate = hit_rate

    def update_agent_count(self, count: int) -> None:
        """Update active agent count."""
        self.system_metrics.active_agents = count

    def update_engine_count(self, count: int) -> None:
        """Update loaded engine count."""
        self.system_metrics.engines_loaded = count

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        uptime = time.time() - self.start_time
        error_rate = (
            self.system_metrics.total_errors / self.system_metrics.total_requests
            if self.system_metrics.total_requests > 0
            else 0
        )

        # Determine health status
        if error_rate < 0.01 and uptime > 60:
            status = "healthy"
        elif error_rate < 0.05:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "error_rate": f"{error_rate:.2%}",
            "total_requests": self.system_metrics.total_requests,
            "active_layers": sum(1 for m in self.layer_metrics.values() if m.requests > 0),
            "cache_hit_rate": f"{self.system_metrics.cache_hit_rate:.1%}",
            "law_violations": self.system_metrics.law_violations,
            "active_agents": self.system_metrics.active_agents,
            "engines_loaded": self.system_metrics.engines_loaded,
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"

    def get_layer_performance(self) -> List[dict[str, Any]]:
        """Get performance metrics for all layers."""
        return [
            {
                "layer": m.layer_id,
                "name": m.name,
                "requests": m.requests,
                "errors": m.errors,
                "error_rate": f"{m.errors / m.requests:.2%}" if m.requests > 0 else "0%",
                "avg_response_ms": f"{m.avg_response_time * 1000:.2f}",
                "status": m.status,
            }
            for m in self.layer_metrics.values()
        ]

    def get_cognitive_analytics(self) -> Dict[str, Any]:
        """Get cognitive operation analytics."""
        # Aggregate cognitive layer metrics (L10)
        cognitive = self.layer_metrics.get(10)

        return {
            "total_think_operations": cognitive.requests if cognitive else 0,
            "think_error_rate": (
                f"{cognitive.errors / cognitive.requests:.2%}"
                if cognitive and cognitive.requests > 0
                else "0%"
            ),
            "avg_think_time_ms": (
                f"{cognitive.avg_response_time * 1000:.2f}" if cognitive else "0"
            ),
            "law_compliance_rate": (
                f"{1 - self.system_metrics.law_violations / max(cognitive.requests, 1):.2%}"
                if cognitive
                else "N/A"
            ),
            "cache_efficiency": f"{self.system_metrics.cache_hit_rate:.1%}",
        }

    def get_top_performers(self, n: int = 5) -> List[dict[str, Any]]:
        """Get top N performing layers by request count."""
        sorted_layers = sorted(self.layer_metrics.values(), key=lambda m: m.requests, reverse=True)

        return [
            {
                "layer": m.layer_id,
                "name": m.name,
                "requests": m.requests,
                "avg_response_ms": f"{m.avg_response_time * 1000:.2f}",
            }
            for m in sorted_layers[:n]
        ]

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        return {
            "report_id": f"RPT-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now(UTC).isoformat(),
            "system": self.get_system_health(),
            "cognitive": self.get_cognitive_analytics(),
            "layers": self.get_layer_performance(),
            "top_performers": self.get_top_performers(),
            "version": self.VERSION,
            "layer": 26,
        }

    def export_metrics(self, filepath: str) -> bool:
        """Export metrics to JSON file."""
        try:
            report = self.generate_report()
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def snapshot(self) -> None:
        """Take a metrics snapshot for historical tracking."""
        snapshot = SystemMetrics(
            timestamp=datetime.now(UTC).isoformat(),
            uptime_seconds=time.time() - self.start_time,
            total_requests=self.system_metrics.total_requests,
            total_errors=self.system_metrics.total_errors,
            active_layers=sum(1 for m in self.layer_metrics.values() if m.requests > 0),
            cache_hit_rate=self.system_metrics.cache_hit_rate,
            law_violations=self.system_metrics.law_violations,
            active_agents=self.system_metrics.active_agents,
            engines_loaded=self.system_metrics.engines_loaded,
        )
        self.historical_data.append(snapshot)

        # Keep only last 100 snapshots
        if len(self.historical_data) > 100:
            self.historical_data = self.historical_data[-100:]

    def get_trends(self) -> Dict[str, list[Any]]:
        """Get metric trends over time."""
        if not self.historical_data:
            return {}

        return {
            "timestamps": [s.timestamp for s in self.historical_data],
            "requests": [s.total_requests for s in self.historical_data],
            "errors": [s.total_errors for s in self.historical_data],
            "active_layers": [s.active_layers for s in self.historical_data],
        }

    def status(self) -> Dict[str, Any]:
        """Get dashboard status."""
        return {
            "dashboard": "AnalyticsDashboard",
            "version": self.VERSION,
            "layer": 26,
            "uptime": self._format_uptime(time.time() - self.start_time),
            "snapshots": len(self.historical_data),
            "status": "active",
        }


# Global instance
_dashboard_instance: Optional[AnalyticsDashboard] = None


def get_dashboard() -> AnalyticsDashboard:
    """Get global analytics dashboard instance."""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = AnalyticsDashboard()
    return _dashboard_instance


def record_metric(layer: int, response_time: float, error: bool = False) -> None:
    """Quick metric recording."""
    get_dashboard().record_request(layer, response_time, error)


def get_health_report() -> Dict[str, Any]:
    """Quick health report."""
    return get_dashboard().get_system_health()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AMOS Analytics Dashboard (Layer 26)")
    parser.add_argument("--start", action="store_true", help="Start dashboard monitoring")
    parser.add_argument("--metrics", action="store_true", help="Show current metrics")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument("--health", action="store_true", help="Show health status")

    args = parser.parse_args()

    dashboard = AnalyticsDashboard()

    if args.start:
        print("=" * 70)
        print("AMOS Analytics Dashboard (Layer 26)")
        print("=" * 70)
        print("\nMonitoring 25 layers...")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                dashboard.snapshot()
                health = dashboard.get_system_health()
                print(
                    f"\r[{health['status'].upper()}] "
                    f"Uptime: {health['uptime_formatted']} | "
                    f"Requests: {health['total_requests']} | "
                    f"Error Rate: {health['error_rate']}",
                    end="",
                    flush=True,
                )
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")

    elif args.metrics:
        report = dashboard.get_layer_performance()
        print("\nLayer Performance:")
        print("-" * 70)
        for layer in report[:10]:  # Top 10
            print(
                f"  L{layer['layer']:02d} {layer['name'][:25]:25s} | "
                f"Requests: {layer['requests']:5d} | "
                f"Errors: {layer['errors']:3d}"
            )

    elif args.report:
        report = dashboard.generate_report()
        print(json.dumps(report, indent=2))

    elif args.health:
        health = dashboard.get_system_health()
        print(f"\nSystem Health: {health['status'].upper()}")
        print(f"  Uptime: {health['uptime_formatted']}")
        print(f"  Requests: {health['total_requests']}")
        print(f"  Error Rate: {health['error_rate']}")
        print(f"  Cache Hit Rate: {health['cache_hit_rate']}")
        print(f"  Active Agents: {health['active_agents']}")
        print(f"  Engines: {health['engines_loaded']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""AMOS Observability Metrics v14.0.0

Prometheus metrics instrumentation for the AMOS Production Orchestrator.
Provides comprehensive observability for module activation, memory bridges,
guardrails, and system health.
"""

import time
from contextlib import contextmanager
from typing import Any

from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)


class AMOSMetrics:
    """Prometheus metrics collector for AMOS orchestrator."""

    def __init__(self) -> None:
        """Initialize all Prometheus metrics."""
        # Info metric
        self.version_info = Info(
            "amos_version",
            "AMOS orchestrator version information",
        )
        self.version_info.info({"version": "14.0.0", "release": "production"})

        # Module metrics
        self.modules_total = Gauge(
            "amos_modules_total",
            "Total number of discovered modules",
            ["tier"],
        )
        self.modules_activated = Gauge(
            "amos_modules_activated_total",
            "Number of activated modules",
            ["tier"],
        )
        self.module_activation_duration = Histogram(
            "amos_module_activation_duration_seconds",
            "Time spent activating modules",
            ["module_name", "tier"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
        )
        self.module_activation_failures = Counter(
            "amos_module_activation_failures_total",
            "Number of module activation failures",
            ["module_name", "tier"],
        )

        # Memory bridge metrics
        self.memory_bridges_total = Gauge(
            "amos_memory_bridges_total",
            "Total number of memory bridges",
            ["memory_type"],
        )
        self.memory_bridges_active = Gauge(
            "amos_memory_bridges_active",
            "Number of active memory bridges",
            ["memory_type"],
        )

        # Guardrail metrics
        self.guardrails_total = Gauge(
            "amos_guardrails_total",
            "Total number of guardrail rules",
        )
        self.guardrail_violations = Counter(
            "amos_guardrail_violations_total",
            "Number of guardrail violations",
            ["rule_name", "action"],
        )

        # System health metrics
        self.system_health = Gauge(
            "amos_system_health",
            "Overall system health (1 = healthy, 0 = unhealthy)",
        )
        self.activation_rate = Gauge(
            "amos_activation_rate",
            "Percentage of modules successfully activated",
        )
        self.cycle_duration = Histogram(
            "amos_cycle_duration_seconds",
            "Duration of orchestrator cycles",
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
        )

        # API metrics
        self.api_requests_total = Counter(
            "amos_api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
        )
        self.api_request_duration = Histogram(
            "amos_api_request_duration_seconds",
            "API request duration",
            ["method", "endpoint"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
        )

        # Dependency metrics
        self.dependency_graph_nodes = Gauge(
            "amos_dependency_graph_nodes",
            "Number of nodes in dependency graph",
        )
        self.dependency_graph_edges = Gauge(
            "amos_dependency_graph_edges",
            "Number of edges in dependency graph",
        )

    def update_module_metrics(
        self,
        modules: dict[str, Any],
        tier_counts: dict[str, int],
    ) -> None:
        """Update module-related metrics."""
        for tier, count in tier_counts.items():
            self.modules_total.labels(tier=tier).set(count)

        activated_by_tier: dict[str, int] = {}
        for module in modules.values():
            tier = module.tier.name
            activated_by_tier[tier] = activated_by_tier.get(tier, 0)
            if module.activated:
                activated_by_tier[tier] += 1

        for tier, count in activated_by_tier.items():
            self.modules_activated.labels(tier=tier).set(count)

        total = len(modules)
        activated = sum(1 for m in modules.values() if m.activated)
        rate = activated / total if total > 0 else 0
        self.activation_rate.set(rate)
        health = 1.0 if rate > 0.8 else 0.5 if rate > 0.5 else 0.0
        self.system_health.set(health)

    def update_memory_bridge_metrics(self, bridges: list[Any]) -> None:
        """Update memory bridge metrics."""
        by_type: dict[str, int] = {}
        active_by_type: dict[str, int] = {}

        for bridge in bridges:
            memory_type = bridge.memory_type.value
            by_type[memory_type] = by_type.get(memory_type, 0) + 1
            if bridge.active:
                active_by_type[memory_type] = active_by_type.get(memory_type, 0) + 1

        for memory_type, count in by_type.items():
            self.memory_bridges_total.labels(memory_type=memory_type).set(count)

        for memory_type, count in active_by_type.items():
            self.memory_bridges_active.labels(memory_type=memory_type).set(count)

    def update_guardrail_metrics(self, guardrails: list[dict[str, Any]]) -> None:
        """Update guardrail metrics."""
        self.guardrails_total.set(len(guardrails))

    def update_dependency_graph_metrics(self, nodes: int, edges: int) -> None:
        """Update dependency graph metrics."""
        self.dependency_graph_nodes.set(nodes)
        self.dependency_graph_edges.set(edges)

    @contextmanager
    def track_activation(self, module_name: str, tier: str):
        """Context manager to track module activation time."""
        start = time.time()
        try:
            yield
            duration = time.time() - start
            self.module_activation_duration.labels(
                module_name=module_name,
                tier=tier,
            ).observe(duration)
        except Exception:
            self.module_activation_failures.labels(
                module_name=module_name,
                tier=tier,
            ).inc()
            raise

    @contextmanager
    def track_api_request(self, method: str, endpoint: str):
        """Context manager to track API request duration."""
        start = time.time()
        status = "200"
        try:
            yield
        except Exception:
            status = "500"
            raise
        finally:
            duration = time.time() - start
            self.api_request_duration.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            self.api_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status,
            ).inc()

    def get_metrics_response(self) -> Response:
        """Generate Prometheus metrics HTTP response."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )


# Singleton instance
_metrics: Optional[AMOSMetrics] = None


def get_metrics() -> AMOSMetrics:
    """Get or create singleton metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = AMOSMetrics()
    return _metrics

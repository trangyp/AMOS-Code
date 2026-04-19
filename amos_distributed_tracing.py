#!/usr/bin/env python3
"""AMOS Distributed Tracing v14.0.0

OpenTelemetry instrumentation for distributed tracing across the 5-layer
orchestrator architecture. Provides request flow visibility through:
- Layer 0: Discovery
- Layer 1: Dependency Graph
- Layer 2: Activation
- Layer 3: Memory Bridges
- Layer 4: Guardrails
- Layer 5: API
"""

import functools
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind, Status, StatusCode


class AMOSTracing:
    """Distributed tracing for AMOS orchestrator."""

    def __init__(self, service_name: str = "amos-orchestrator") -> None:
        """Initialize OpenTelemetry tracing."""
        self.service_name = service_name

        # Resource attributes
        resource = Resource.create(
            {
                SERVICE_NAME: service_name,
                SERVICE_VERSION: "14.0.0",
                "deployment.environment": "production",
            }
        )

        # Tracer provider
        self.provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.provider)

        # OTLP exporter to Jaeger
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://jaeger:4318/v1/traces",
            timeout=10,
        )

        # Span processors
        self.provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Console exporter for debugging (optional)
        # self.provider.add_span_processor(
        #     BatchSpanProcessor(ConsoleSpanExporter())
        # )

        # Tracer instance
        self.tracer = trace.get_tracer(__name__)

    def instrument_fastapi(self, app: Any) -> None:
        """Instrument FastAPI application."""
        FastAPIInstrumentor.instrument_app(app)

    @contextmanager
    def span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] = None,
    ):
        """Context manager for creating spans."""
        with self.tracer.start_as_current_span(
            name,
            kind=kind,
            attributes=attributes,
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    def trace_layer_0_discovery(self, modules_count: int) -> None:
        """Trace module discovery."""
        with self.span(
            "layer_0.discovery",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.layer": 0,
                "amos.operation": "discovery",
                "amos.modules.discovered": modules_count,
            },
        ):
            pass

    def trace_layer_1_dependency_graph(
        self,
        nodes: int,
        edges: int,
        cycles_detected: int,
    ) -> None:
        """Trace dependency graph building."""
        with self.span(
            "layer_1.dependency_graph",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.layer": 1,
                "amos.operation": "dependency_graph",
                "amos.graph.nodes": nodes,
                "amos.graph.edges": edges,
                "amos.graph.cycles": cycles_detected,
            },
        ):
            pass

    def trace_layer_2_activation(
        self,
        module_name: str,
        tier: str,
        activated: bool,
        duration_ms: float,
    ) -> None:
        """Trace module activation."""
        with self.span(
            "layer_2.activation",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.layer": 2,
                "amos.operation": "activation",
                "amos.module.name": module_name,
                "amos.module.tier": tier,
                "amos.module.activated": activated,
                "amos.activation.duration_ms": duration_ms,
            },
        ):
            pass

    def trace_layer_3_memory_bridge(
        self,
        bridge_type: str,
        modules_connected: int,
    ) -> None:
        """Trace memory bridge establishment."""
        with self.span(
            "layer_3.memory_bridge",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.layer": 3,
                "amos.operation": "memory_bridge",
                "amos.memory.type": bridge_type,
                "amos.memory.modules_connected": modules_connected,
            },
        ):
            pass

    def trace_layer_4_guardrails(self, rules_count: int) -> None:
        """Trace guardrail installation."""
        with self.span(
            "layer_4.guardrails",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.layer": 4,
                "amos.operation": "guardrails",
                "amos.guardrails.rules_count": rules_count,
            },
        ):
            pass

    def trace_layer_5_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Trace API request (complements FastAPI auto-instrumentation)."""
        with self.span(
            "layer_5.api_request",
            kind=SpanKind.SERVER,
            attributes={
                "amos.layer": 5,
                "amos.operation": "api",
                "http.method": method,
                "http.route": endpoint,
                "http.status_code": status_code,
                "http.duration_ms": duration_ms,
            },
        ):
            pass

    def trace_initialization(
        self,
        modules_total: int,
        modules_activated: int,
        bridges_count: int,
        guardrails_count: int,
        duration_ms: float,
    ) -> None:
        """Trace complete initialization cycle."""
        with self.span(
            "amos.initialization",
            kind=SpanKind.INTERNAL,
            attributes={
                "amos.operation": "initialization",
                "amos.modules.total": modules_total,
                "amos.modules.activated": modules_activated,
                "amos.activation.rate": modules_activated / modules_total
                if modules_total > 0
                else 0,
                "amos.bridges.count": bridges_count,
                "amos.guardrails.count": guardrails_count,
                "amos.init.duration_ms": duration_ms,
            },
        ):
            pass


def traced_method(span_name: str = None):
    """Decorator to trace method execution."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            name = span_name or func.__name__

            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.args_count", len(args) + len(kwargs))

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator


# Singleton instance
_tracing: Optional[AMOSTracing] = None


def get_tracing(service_name: str = "amos-orchestrator") -> AMOSTracing:
    """Get or create singleton tracing instance."""
    global _tracing
    if _tracing is None:
        _tracing = AMOSTracing(service_name)
    return _tracing

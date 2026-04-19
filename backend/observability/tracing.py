"""
AMOS SuperBrain Distributed Tracing v2.0.0

OpenTelemetry-based distributed tracing for tracking requests across all 12
governed systems with governance decision visibility.

Architecture:
- OpenTelemetry SDK for trace collection
- Jaeger/Zipkin compatible exporters
- Governance span attributes for ActionGate decisions
- Automatic context propagation across async boundaries

Owner: Trang Phan
Version: 2.0.0
"""

import functools
from collections.abc import Callable
from contextlib import contextmanager

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class SuperBrainTracer:
    """Distributed tracer with governance-aware spans."""

    def __init__(self, service_name: str = "amos-superbrain"):
        self.service_name = service_name
        self._tracer: trace.Tracer = None
        self._initialized = False

        if OPENTELEMETRY_AVAILABLE:
            self._init_tracer()

    def _init_tracer(self):
        """Initialize OpenTelemetry tracer with exporters."""
        try:
            # Configure resource
            resource = Resource.create(
                {
                    SERVICE_NAME: self.service_name,
                    SERVICE_VERSION: "2.0.0",
                    "deployment.environment": "production",
                    "superbrain.version": "2.0.0",
                    "superbrain.systems": "12",
                }
            )

            # Create provider
            provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(provider)

            # Add Jaeger exporter (if configured)
            try:
                jaeger_exporter = JaegerExporter(
                    agent_host_name="localhost",
                    agent_port=6831,
                )
                provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
            except Exception:
                pass  # Jaeger not configured

            # Add OTLP exporter for CloudWatch/other backends
            try:
                otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            except Exception:
                pass  # OTLP not configured

            self._tracer = trace.get_tracer(__name__)
            self._initialized = True

        except Exception as e:
            print(f"Tracer initialization failed: {e}")
            self._initialized = False

    @contextmanager
    def start_governed_span(self, name: str, system: str, operation: str, attributes: dict = None):
        """Start a span with governance tracking."""
        if not OPENTELEMETRY_AVAILABLE or not self._tracer:
            yield None
            return

        # Build span attributes
        span_attrs = {
            "superbrain.governed": True,
            "superbrain.system": system,
            "superbrain.operation": operation,
            "superbrain.version": "2.0.0",
        }

        if attributes:
            span_attrs.update(attributes)

        with self._tracer.start_as_current_span(name, attributes=span_attrs) as span:
            # Record governance decision if SuperBrain available
            if SUPERBRAIN_AVAILABLE:
                try:
                    brain = get_super_brain()
                    if brain and hasattr(brain, "action_gate"):
                        action_result = brain.action_gate.validate_action(
                            agent_id=system, action=operation, details={"traced": True}
                        )
                        span.set_attribute("superbrain.authorized", action_result.authorized)
                        span.set_attribute(
                            "superbrain.reason", getattr(action_result, "reason", "unknown")
                        )

                        if not action_result.authorized:
                            span.set_status(Status(StatusCode.ERROR, "Governance blocked"))
                except Exception:
                    pass  # Fail open

            yield span

    def trace_governed_method(self, system: str, operation: str, attributes: dict = None):
        """Decorator to trace governed methods."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.start_governed_span(
                    name=f"{system}.{operation}",
                    system=system,
                    operation=operation,
                    attributes=attributes,
                ) as span:
                    try:
                        result = func(*args, **kwargs)
                        if span:
                            span.set_attribute("superbrain.success", True)
                        return result
                    except Exception as e:
                        if span:
                            span.set_attribute("superbrain.success", False)
                            span.set_attribute("error.message", str(e))
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

            # Async version
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.start_governed_span(
                    name=f"{system}.{operation}",
                    system=system,
                    operation=operation,
                    attributes=attributes,
                ) as span:
                    try:
                        result = await func(*args, **kwargs)
                        if span:
                            span.set_attribute("superbrain.success", True)
                        return result
                    except Exception as e:
                        if span:
                            span.set_attribute("superbrain.success", False)
                            span.set_attribute("error.message", str(e))
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return wrapper

        return decorator


# Global tracer instance
tracer = SuperBrainTracer()


# Convenience functions for common patterns
def trace_cognitive_router_task(task: str):
    """Trace a cognitive router task with governance."""
    return tracer.start_governed_span(
        name="cognitive_router.route_task",
        system="cognitive_router",
        operation="route_task",
        attributes={"task.length": len(task)},
    )


def trace_circuit_breaker_action(circuit_name: str, action: str):
    """Trace a circuit breaker action with governance."""
    return tracer.start_governed_span(
        name=f"resilience_engine.circuit_{action}",
        system="resilience_engine",
        operation=f"circuit_{action}",
        attributes={"circuit.name": circuit_name},
    )


def trace_knowledge_load(file_count: int):
    """Trace knowledge loading with governance."""
    return tracer.start_governed_span(
        name="knowledge_loader.load",
        system="knowledge_loader",
        operation="load_knowledge",
        attributes={"file.count": file_count},
    )


def trace_orchestrator_task(task_type: str, complexity: str):
    """Trace orchestrator task with governance."""
    return tracer.start_governed_span(
        name="master_orchestrator.process_task",
        system="master_orchestrator",
        operation="process_task",
        attributes={"task.type": task_type, "task.complexity": complexity},
    )


# Import for type checking
import asyncio

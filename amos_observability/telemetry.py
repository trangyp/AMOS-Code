from __future__ import annotations

"""OpenTelemetry setup and configuration for AMOS."""

import os
from typing import Any, Optional

try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import (
        DEPLOYMENT_ENVIRONMENT,
        SERVICE_NAME,
        SERVICE_VERSION,
        Resource,
    )
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Global instances
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None


def setup_observability(
    service_name: str = "amos-equation-api",
    service_version: str = "15.0.0",
    environment: str = "development",
    otlp_endpoint: str = None,
    console_export: bool = False,
) -> bool:
    """Initialize OpenTelemetry with OTLP exporters.

    Args:
        service_name: Name of the service for tracing
        service_version: Version identifier
        environment: deployment environment (dev/staging/prod)
        otlp_endpoint: OTLP collector endpoint (defaults to OTEL_EXPORTER_OTLP_ENDPOINT env var)
        console_export: Also export to console for debugging

    Returns:
        True if observability was set up successfully
    """
    if not OTEL_AVAILABLE:
        print(
            "OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi"
        )
        return False

    global _tracer_provider, _meter_provider

    # Create resource with service information
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            DEPLOYMENT_ENVIRONMENT: environment,
            "service.namespace": "amos",
            "host.name": os.uname().nodename if hasattr(os, "uname") else "unknown",
        }
    )

    # Configure tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint available
    endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    try:
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    except Exception as e:
        print(f"Warning: Could not configure OTLP exporter: {e}")

    # Add console exporter for debugging
    if console_export or os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true":
        console_exporter = ConsoleSpanExporter()
        _tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    trace.set_tracer_provider(_tracer_provider)

    # Configure metrics
    metric_readers = []

    try:
        otlp_metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
        metric_readers.append(
            PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=60000)
        )
    except Exception as e:
        print(f"Warning: Could not configure OTLP metric exporter: {e}")

    _meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    metrics.set_meter_provider(_meter_provider)

    print(f"✅ Observability initialized for {service_name} v{service_version} [{environment}]")
    print(f"   OTLP Endpoint: {endpoint}")

    return True


def get_tracer(name: str = "amos-equation-api") -> Any:
    """Get OpenTelemetry tracer instance."""
    if not OTEL_AVAILABLE:
        return _NoOpTracer()
    return trace.get_tracer(name)


def get_meter(name: str = "amos-equation-api") -> Any:
    """Get OpenTelemetry meter instance."""
    if not OTEL_AVAILABLE:
        return _NoOpMeter()
    return metrics.get_meter(name)


def instrument_fastapi(app: Any) -> bool:
    """Instrument FastAPI application with OpenTelemetry."""
    if not OTEL_AVAILABLE:
        return False

    try:
        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
        return True
    except Exception as e:
        print(f"Warning: Could not instrument FastAPI: {e}")
        return False


class _NoOpTracer:
    """No-op tracer for when OpenTelemetry is not available."""

    def start_as_current_span(self, name: str, **kwargs: Any):
        return _NoOpContextManager()

    def start_span(self, name: str, **kwargs: Any):
        return _NoOpSpan()


class _NoOpSpan:
    """No-op span for when OpenTelemetry is not available."""

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_status(self, status: Any) -> None:
        pass

    def record_exception(self, exception: Exception) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _NoOpContextManager:
    """No-op context manager."""

    def __enter__(self):
        return _NoOpSpan()

    def __exit__(self, *args: Any) -> None:
        pass


class _NoOpMeter:
    """No-op meter for when OpenTelemetry is not available."""

    def create_counter(self, name: str, **kwargs: Any) -> Any:
        return _NoOpInstrument()

    def create_histogram(self, name: str, **kwargs: Any) -> Any:
        return _NoOpInstrument()

    def create_up_down_counter(self, name: str, **kwargs: Any) -> Any:
        return _NoOpInstrument()

    def create_gauge(self, name: str, **kwargs: Any) -> Any:
        return _NoOpInstrument()


class _NoOpInstrument:
    """No-op instrument."""

    def add(self, value: Any, attributes: Any = None) -> None:
        pass

    def record(self, value: Any, attributes: Any = None) -> None:
        pass

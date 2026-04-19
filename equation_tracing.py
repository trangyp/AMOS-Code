#!/usr/bin/env python3
"""AMOS Equation Distributed Tracing - OpenTelemetry Integration."""

import os
import socket
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.trace import Span, Status, StatusCode

    _otel_available = True
except ImportError:
    _otel_available = False

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    _fastapi_instrumentation = True
except ImportError:
    _fastapi_instrumentation = False


def setup_telemetry(
    service_name: str = None,
    otel_endpoint: str = None,
) -> bool:
    """Initialize OpenTelemetry with production configuration."""
    if not _otel_available:
        return False

    svc = service_name or os.getenv("OTEL_SERVICE_NAME", "amos-equation-api")
    env = os.getenv("ENVIRONMENT", "development")
    endpoint = otel_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4318")

    resource = Resource.create(
        {
            "service.name": svc,
            "service.version": os.getenv("APP_VERSION", "2.1.0"),
            "deployment.environment": env,
            "service.instance.id": socket.gethostname(),
            "host.name": socket.gethostname(),
        }
    )

    provider = TracerProvider(resource=resource)

    if env in ["production", "staging"]:
        otlp = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"http://{endpoint}/v1/traces"),
            max_queue_size=2048,
            schedule_delay_millis=5000,
            max_export_batch_size=512,
        )
        provider.add_span_processor(otlp)
    else:
        console = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(console)

    trace.set_tracer_provider(provider)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"http://{endpoint}/v1/metrics"),
        export_interval_millis=5000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    return True


def instrument_fastapi(app: Any) -> None:
    """Instrument FastAPI app with OpenTelemetry."""
    if _otel_available and _fastapi_instrumentation:
        FastAPIInstrumentor.instrument_app(app)


@contextmanager
def create_span(
    name: str,
    attributes: Dict[str, Any] = None,
) -> Generator[Span, None, None]:
    """Create a custom span with attributes."""
    if not _otel_available:
        yield None
        return

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span


def set_span_error(span: Span, exception: Exception) -> None:
    """Mark span as failed with exception details."""
    if span and _otel_available:
        span.set_status(Status(StatusCode.ERROR, str(exception)))
        span.record_exception(exception)


def get_trace_context() -> dict[str, str]:
    """Get current trace context for propagation."""
    if not _otel_available:
        return {}

    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        trace_id = ctx.trace_id
        span_id = ctx.span_id
        return {
            "trace_id": hex(trace_id)[2:].zfill(32),
            "span_id": hex(span_id)[2:].zfill(16),
        }
    return {}

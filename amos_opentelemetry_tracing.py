#!/usr/bin/env python3
"""AMOS OpenTelemetry Tracing - Distributed Observability (Phase 14+ Enhancement)
==============================================================================

Enterprise-grade distributed tracing for AMOS FastAPI Gateway with:
- Automatic endpoint instrumentation
- Database query tracing
- External service call tracing
- Correlation with existing Prometheus metrics
- Integration with performance profiler
- Jaeger/Zipkin export support

Architecture:
- OpenTelemetry SDK for trace collection
- OTLP exporter for Jaeger/Zipkin
- FastAPI auto-instrumentation middleware
- Custom span attributes for AMOS context
- Trace context propagation across services

Usage:
    from amos_opentelemetry_tracing import setup_tracing, get_tracer

    # Setup in FastAPI app
    setup_tracing(
        service_name="amos-gateway",
        jaeger_endpoint="http://jaeger:4317"
    )

    # Manual span creation
    with get_tracer().start_as_current_span("equation_execution") as span:
        span.set_attribute("equation.name", "softmax")
        result = execute_equation()

Integration:
- amos_fastapi_gateway.py - Auto-instrumentation
- amos_performance_profiler.py - Span correlation
- amos_metrics_exporter.py - Metric-trace linking

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

from __future__ import annotations

import functools
import os
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    print("OpenTelemetry not installed. Tracing disabled.")
    print(
        "Install: pip install opentelemetry-api opentelemetry-sdk "
        "opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-redis "
        "opentelemetry-instrumentation-sqlalchemy opentelemetry-exporter-otlp"
    )

# Performance profiler integration
try:
    from amos_performance_profiler import get_profiler

    PROFILER_AVAILABLE = True
except ImportError:
    PROFILER_AVAILABLE = False


T = TypeVar("T")


class AMOSTracing:
    """
    AMOS OpenTelemetry tracing manager.

    Provides distributed tracing for:
    - HTTP requests through FastAPI
    - Database queries via SQLAlchemy
    - Redis cache operations
    - Custom business logic spans
    """

    _instance: AMOSTracing | None = None
    _tracer_provider: TracerProvider | None = None
    _tracer: trace.Tracer = None
    _initialized = False

    def __new__(cls) -> AMOSTracing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._service_name = "amos-gateway"
        self._service_version = "1.0.0"
        self._exporter_endpoint = None

    def setup(
        self,
        service_name: str = "amos-gateway",
        service_version: str = "1.0.0",
        jaeger_endpoint: str = None,
        zipkin_endpoint: str = None,
        console_export: bool = False,
        sampling_rate: float = 1.0,
    ) -> bool:
        """
        Initialize OpenTelemetry tracing.

        Args:
            service_name: Name of the service for tracing
            service_version: Service version
            jaeger_endpoint: Jaeger OTLP endpoint (e.g., http://jaeger:4317)
            zipkin_endpoint: Zipkin endpoint (e.g., http://zipkin:9411)
            console_export: Also export to console for debugging
            sampling_rate: Trace sampling rate (0.0-1.0)

        Returns:
            True if setup successful, False otherwise
        """
        if not OPENTELEMETRY_AVAILABLE:
            print("⚠️  OpenTelemetry not available. Tracing disabled.")
            return False

        self._service_name = service_name
        self._service_version = service_version

        # Create resource
        resource = Resource.create(
            {
                SERVICE_NAME: service_name,
                SERVICE_VERSION: service_version,
                "deployment.environment": os.getenv("ENVIRONMENT", "production"),
            }
        )

        # Create tracer provider
        self._tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self._tracer_provider)

        # Setup exporters
        processors = []

        if jaeger_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint)
            processors.append(BatchSpanProcessor(otlp_exporter))
            self._exporter_endpoint = jaeger_endpoint
            print(f"✅ Jaeger exporter configured: {jaeger_endpoint}")

        if zipkin_endpoint:
            from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter

            zipkin_exporter = ZipkinExporter(endpoint=zipkin_endpoint)
            processors.append(BatchSpanProcessor(zipkin_exporter))
            print(f"✅ Zipkin exporter configured: {zipkin_endpoint}")

        if console_export or not processors:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            console_exporter = ConsoleSpanExporter()
            processors.append(BatchSpanProcessor(console_exporter))
            print("✅ Console exporter configured")

        # Add processors to provider
        for processor in processors:
            self._tracer_provider.add_span_processor(processor)

        # Get tracer
        self._tracer = trace.get_tracer(service_name, service_version)

        print(f"✅ OpenTelemetry tracing initialized for {service_name}")
        return True

    def instrument_fastapi(self, app: Any) -> bool:
        """
        Auto-instrument FastAPI application.

        Args:
            app: FastAPI application instance

        Returns:
            True if instrumentation successful
        """
        if not OPENTELEMETRY_AVAILABLE or not self._tracer:
            return False

        try:
            FastAPIInstrumentor.instrument_app(app)
            print("✅ FastAPI auto-instrumentation enabled")
            return True
        except Exception as e:
            print(f"⚠️  FastAPI instrumentation failed: {e}")
            return False

    def instrument_redis(self) -> bool:
        """Instrument Redis operations."""
        if not OPENTELEMETRY_AVAILABLE:
            return False

        try:
            RedisInstrumentor().instrument()
            print("✅ Redis auto-instrumentation enabled")
            return True
        except Exception as e:
            print(f"⚠️  Redis instrumentation failed: {e}")
            return False

    def instrument_sqlalchemy(self, engine: Any) -> bool:
        """
        Instrument SQLAlchemy database operations.

        Args:
            engine: SQLAlchemy engine instance
        """
        if not OPENTELEMETRY_AVAILABLE:
            return False

        try:
            SQLAlchemyInstrumentor().instrument(
                engine=engine, enable_commenter=True, commenter_options={}
            )
            print("✅ SQLAlchemy auto-instrumentation enabled")
            return True
        except Exception as e:
            print(f"⚠️  SQLAlchemy instrumentation failed: {e}")
            return False

    def get_tracer(self) -> trace.Tracer:
        """Get the configured tracer instance."""
        return self._tracer

    @contextmanager
    def start_span(
        self,
        name: str,
        attributes: dict[str, Any] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL,
    ):
        """
        Context manager for creating a span.

        Args:
            name: Span name
            attributes: Span attributes
            kind: Span kind (INTERNAL, SERVER, CLIENT, etc.)

        Usage:
            with tracing.start_span("equation_execution") as span:
                span.set_attribute("equation.name", "softmax")
                result = execute()
        """
        if not self._tracer:
            yield None
            return

        with self._tracer.start_as_current_span(name, kind=kind) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            yield span

    def trace_method(self, name: str = None, attributes: dict[str, Any] = None) -> Callable:
        """
        Decorator for tracing method calls.

        Args:
            name: Span name (defaults to method name)
            attributes: Additional span attributes

        Usage:
            @tracing.trace_method("execute_equation")
            async def execute(self, name: str, inputs: dict) -> dict:
                return await self._execute(name, inputs)
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            span_name = name or func.__name__

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                if not self._tracer:
                    return await func(*args, **kwargs)

                with self._tracer.start_as_current_span(span_name) as span:
                    # Add attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)

                    # Add function parameters as attributes (sanitized)
                    for i, arg in enumerate(args[1:]):  # Skip self
                        if isinstance(arg, (str, int, float, bool)):
                            span.set_attribute(f"arg.{i}", arg)

                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_attribute(f"kwarg.{key}", value)

                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                if not self._tracer:
                    return func(*args, **kwargs)

                with self._tracer.start_as_current_span(span_name) as span:
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)

                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                        raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    def shutdown(self) -> None:
        """Shutdown tracing and flush spans."""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
            print("✅ OpenTelemetry tracing shutdown")


# Global instance
def get_tracing() -> AMOSTracing:
    """Get the global AMOS tracing instance."""
    return AMOSTracing()


def setup_tracing(
    service_name: str = "amos-gateway",
    service_version: str = "1.0.0",
    jaeger_endpoint: str = None,
    zipkin_endpoint: str = None,
    console_export: bool = False,
    sampling_rate: float = 1.0,
) -> bool:
    """
    Convenience function to setup tracing.

    Reads configuration from environment variables:
    - OTEL_SERVICE_NAME
    - OTEL_SERVICE_VERSION
    - OTEL_JAEGER_ENDPOINT
    - OTEL_ZIPKIN_ENDPOINT
    - OTEL_CONSOLE_EXPORT
    - OTEL_SAMPLING_RATE
    """
    tracing = get_tracing()

    # Override with environment variables
    service_name = os.getenv("OTEL_SERVICE_NAME", service_name)
    service_version = os.getenv("OTEL_SERVICE_VERSION", service_version)
    jaeger_endpoint = os.getenv("OTEL_JAEGER_ENDPOINT", jaeger_endpoint)
    zipkin_endpoint = os.getenv("OTEL_ZIPKIN_ENDPOINT", zipkin_endpoint)
    console_export = os.getenv("OTEL_CONSOLE_EXPORT", str(console_export)).lower() == "true"
    sampling_rate = float(os.getenv("OTEL_SAMPLING_RATE", sampling_rate))

    return tracing.setup(
        service_name=service_name,
        service_version=service_version,
        jaeger_endpoint=jaeger_endpoint,
        zipkin_endpoint=zipkin_endpoint,
        console_export=console_export,
        sampling_rate=sampling_rate,
    )


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance."""
    return get_tracing().get_tracer()


def instrument_fastapi(app: Any) -> bool:
    """Instrument FastAPI application."""
    return get_tracing().instrument_fastapi(app)


# Import asyncio check
import asyncio
from typing import TypeVar

__all__ = [
    "AMOSTracing",
    "get_tracing",
    "get_tracer",
    "setup_tracing",
    "instrument_fastapi",
]

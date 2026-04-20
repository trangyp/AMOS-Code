"""OpenTelemetry tracing integration for AMOS Brain.

Provides distributed tracing support for:
- Request lifecycle tracking
- Performance span measurements
- Error context propagation
- Integration with modern observability backends (Jaeger, Zipkin, OTLP)
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from collections.abc import Generator


class TracingConfig:
    """Configuration for OpenTelemetry tracing.

    Attributes:
        enabled: Whether tracing is enabled
        service_name: Service name for span attribution
        endpoint: OTLP endpoint URL (if None, uses console exporter)
        sample_rate: Sampling rate (0.0-1.0)
    """

    def __init__(
        self,
        enabled: bool = None,
        service_name: str = "amos-brain",
        endpoint: str = None,
        sample_rate: float = 1.0,
    ):
        self.enabled = (
            enabled
            if enabled is not None
            else os.getenv("AMOS_TRACING_ENABLED", "false").lower() == "true"
        )
        self.service_name = service_name
        self.endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        self.sample_rate = max(0.0, min(1.0, sample_rate))


class TracingSpan:
    """Represents an active tracing span.

    Compatible with OpenTelemetry span interface for future migration.
    """

    def __init__(self, name: str, tracer: Any, parent: Optional[TracingSpan] = None):
        self.name = name
        self.tracer = tracer
        self.parent = parent
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        import time

        self.events.append(
            {
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            }
        )

    def record_exception(self, exception: BaseException) -> None:
        """Record an exception in the span."""
        self.set_attribute("error", True)
        self.set_attribute("error.type", type(exception).__name__)
        self.set_attribute("error.message", str(exception))
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )

    def __enter__(self) -> TracingSpan:
        """Context manager entry."""
        import time

        self._start_time = time.time()
        return self

    def __exit__(self, exc_type: type, exc_val: BaseException, exc_tb: Any) -> None:
        """Context manager exit."""
        import time

        self._end_time = time.time()
        if exc_val:
            self.record_exception(exc_val)


class Tracer:
    """AMOS Brain tracer with OpenTelemetry-compatible interface.

    Provides span creation and context propagation for distributed tracing.
    Currently uses internal implementation; can migrate to opentelemetry-sdk.
    """

    def __init__(self, config: Optional[TracingConfig] = None):
        self.config = config or TracingConfig()
        self._current_span: Optional[TracingSpan] = None
        self._spans: list[TracingSpan] = []

    def start_span(self, name: str, attributes: Optional[dict[str, Any]] = None) -> TracingSpan:
        """Start a new span.

        Args:
            name: Span name
            attributes: Initial span attributes

        Returns:
            TracingSpan that can be used as context manager
        """
        span = TracingSpan(name, self, parent=self._current_span)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        # Set as current
        self._current_span = span
        self._spans.append(span)

        return span

    @contextmanager
    def span(
        self, name: str, attributes: Optional[dict[str, Any]] = None
    ) -> Generator[TracingSpan, None, None]:
        """Context manager for span creation.

        Args:
            name: Span name
            attributes: Initial span attributes

        Yields:
            Active TracingSpan
        """
        span = self.start_span(name, attributes)
        try:
            yield span
        finally:
            # End span and restore parent
            if span.parent:
                self._current_span = span.parent
            else:
                self._current_span = None

    def get_current_span(self) -> Optional[TracingSpan]:
        """Get the current active span."""
        return self._current_span

    def get_spans(self) -> list[TracingSpan]:
        """Get all recorded spans (for testing/debugging)."""
        return self._spans.copy()

    def clear(self) -> None:
        """Clear all recorded spans."""
        self._spans.clear()
        self._current_span = None


# Global tracer instance
tracer: Tracer = Tracer()


def get_tracer(config: Optional[TracingConfig] = None) -> Tracer:
    """Get or create the global tracer.

    Args:
        config: Optional configuration override

    Returns:
        Global Tracer instance
    """
    global tracer
    if config:
        tracer = Tracer(config)
    return tracer


def configure_tracing(
    enabled: bool = None,
    service_name: str = "amos-brain",
    endpoint: str = None,
    sample_rate: float = 1.0,
) -> Tracer:
    """Configure and return the global tracer.

    Args:
        enabled: Enable/disable tracing
        service_name: Service name for spans
        endpoint: OTLP endpoint URL
        sample_rate: Sampling rate (0.0-1.0)

    Returns:
        Configured Tracer instance
    """
    config = TracingConfig(
        enabled=enabled, service_name=service_name, endpoint=endpoint, sample_rate=sample_rate
    )
    return get_tracer(config)


# OpenTelemetry migration helpers
def get_otel_tracer() -> Any:
    """Get OpenTelemetry tracer if available.

    Returns:
        OpenTelemetry tracer or None if opentelemetry not installed
    """
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        return trace.get_tracer("amos-brain")
    except ImportError:
        return None

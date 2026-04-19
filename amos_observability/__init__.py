"""AMOS Observability - OpenTelemetry monitoring and tracing.

This module provides comprehensive observability for the AMOS Equation API including:
- Distributed tracing with OpenTelemetry
- Custom metrics for equation usage analytics
- Structured logging with correlation IDs
- Performance monitoring

Usage:
    from amos_observability import setup_observability, get_tracer

    setup_observability(service_name="amos-equation-api")

    with get_tracer().start_as_current_span("compute_equation") as span:
        span.set_attribute("equation.name", "kinetic_energy")
        result = compute_equation(...)
"""

from .logging import StructuredLogger, get_logger
from .metrics import EquationMetrics, PerformanceMetrics
from .middleware import ObservabilityMiddleware
from .telemetry import get_meter, get_tracer, setup_observability

__version__ = "1.0.0"

__all__ = [
    "setup_observability",
    "get_tracer",
    "get_meter",
    "EquationMetrics",
    "PerformanceMetrics",
    "StructuredLogger",
    "get_logger",
    "ObservabilityMiddleware",
]

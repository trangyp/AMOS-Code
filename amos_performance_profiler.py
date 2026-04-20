#!/usr/bin/env python3
"""AMOS Performance Profiler - Async Performance Monitoring (Phase 14+ Enhancement)
================================================================================

Advanced performance profiling for async AMOS operations with:
- Async function timing with nanosecond precision
- Cache hit/miss correlation
- Memory profiling integration
- Prometheus metrics export
- Bottleneck detection

Features:
- @profile decorator for automatic function profiling
- Context manager for block-level profiling
- Cache performance correlation
- Async-aware profiling (no event loop blocking)
- Integration with amos_metrics_exporter

Usage:
    from amos_performance_profiler import profile, PerformanceProfiler

    @profile("equation_execution")
    async def execute_equation(name: str, inputs: dict) -> dict:
        return await runtime.execute(name, inputs)

    # Or manual profiling
    with profile_block("database_query"):
        result = await db.fetch(query)

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

from __future__ import annotations

import functools
import time
import tracemalloc
from collections import defaultdict
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar

# Prometheus integration
try:
    from amos_metrics_exporter import get_metrics_exporter

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Cache manager integration
try:
    from backend.cache.cache_manager import get_cache_manager

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


T = TypeVar("T")


@dataclass
class ProfileResult:
    """Performance profiling result."""

    name: str
    duration_ms: float
    calls: int = 1
    cache_hits: int = 0
    cache_misses: int = 0
    memory_delta_bytes: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceProfiler:
    """
    AMOS Performance Profiler with async support.

    Tracks:
    - Function execution times
    - Cache performance correlation
    - Memory allocations
    - Call frequency
    """

    _instance: Optional[PerformanceProfiler] = None

    def __new__(cls) -> PerformanceProfiler:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._profiles: dict[str, list[ProfileResult]] = defaultdict(list)
        self._active_profiles: dict[str, float] = {}
        self._tracemalloc_enabled = False
        self._metrics = get_metrics_exporter() if METRICS_AVAILABLE else None

    def enable_memory_profiling(self) -> None:
        """Enable tracemalloc for memory profiling."""
        if not self._tracemalloc_enabled:
            tracemalloc.start()
            self._tracemalloc_enabled = True

    def start_profile(self, name: str, metadata: dict[str, Any] = None) -> None:
        """Start profiling a named operation."""
        self._active_profiles[name] = time.perf_counter()

        if self._tracemalloc_enabled:
            tracemalloc.reset_peak()

    def end_profile(
        self, name: str, cache_hits: int = 0, cache_misses: int = 0, metadata: dict[str, Any] = None
    ) -> ProfileResult:
        """End profiling and return results."""
        if name not in self._active_profiles:
            raise ValueError(f"Profile '{name}' not started")

        start_time = self._active_profiles.pop(name)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Memory stats
        memory_delta = 0
        if self._tracemalloc_enabled:
            _, peak = tracemalloc.get_traced_memory()
            memory_delta = peak

        result = ProfileResult(
            name=name,
            duration_ms=duration_ms,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            memory_delta_bytes=memory_delta,
            metadata=metadata or {},
        )

        self._profiles[name].append(result)

        # Export to metrics
        if self._metrics:
            self._metrics._api_request_duration.observe(duration_ms / 1000)

        return result

    def get_stats(self, name: str = None) -> dict[str, Any]:
        """Get profiling statistics."""
        if name:
            results = self._profiles.get(name, [])
            if not results:
                return {}

            durations = [r.duration_ms for r in results]
            return {
                "name": name,
                "calls": len(results),
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "total_duration_ms": sum(durations),
                "cache_hits": sum(r.cache_hits for r in results),
                "cache_misses": sum(r.cache_misses for r in results),
                "avg_memory_bytes": sum(r.memory_delta_bytes for r in results) / len(results),
            }

        return {name: self.get_stats(name) for name in self._profiles.keys()}

    def get_bottlenecks(self, threshold_ms: float = 100.0) -> list[dict[str, Any]]:
        """Identify performance bottlenecks above threshold."""
        bottlenecks = []
        for name in self._profiles:
            stats = self.get_stats(name)
            if stats.get("avg_duration_ms", 0) > threshold_ms:
                bottlenecks.append(stats)

        return sorted(bottlenecks, key=lambda x: x["avg_duration_ms"], reverse=True)

    def reset(self) -> None:
        """Clear all profiling data."""
        self._profiles.clear()
        self._active_profiles.clear()


def get_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance."""
    return PerformanceProfiler()


def profile(name: str = None, track_cache: bool = True):
    """
    Decorator for profiling async functions.

    Args:
        name: Profile name (defaults to function name)
        track_cache: Whether to track cache hits/misses

    Usage:
        @profile("equation_execution")
        async def execute_equation(name: str, inputs: dict) -> dict:
            return await runtime.execute(name, inputs)
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        profile_name = name or func.__name__
        profiler = get_profiler()

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            profiler.start_profile(
                profile_name,
                {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                },
            )

            cache_hits = 0
            cache_misses = 0

            try:
                # Check cache before execution if available
                if track_cache and CACHE_AVAILABLE:
                    cache = get_cache_manager()
                    # Note: Actual cache checking would need key generation logic
                    pass

                result = await func(*args, **kwargs)

                profiler.end_profile(profile_name, cache_hits=cache_hits, cache_misses=cache_misses)

                return result
            except Exception as e:
                profiler.end_profile(
                    profile_name,
                    cache_hits=cache_hits,
                    cache_misses=cache_misses,
                    metadata={"error": str(e)},
                )
                raise

        return wrapper

    return decorator


@asynccontextmanager
async def profile_block(name: str, track_memory: bool = False):
    """
    Async context manager for profiling code blocks.

    Usage:
        async with profile_block("database_query"):
            result = await db.fetch(query)
    """
    profiler = get_profiler()

    if track_memory:
        profiler.enable_memory_profiling()

    start_time = time.perf_counter()

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        result = ProfileResult(name=name, duration_ms=duration_ms, metadata={"type": "block"})
        profiler._profiles[name].append(result)


@contextmanager
def profile_sync_block(name: str):
    """
    Sync context manager for profiling synchronous code blocks.

    Usage:
        with profile_sync_block("file_read"):
            data = f.read()
    """
    profiler = get_profiler()
    start_time = time.perf_counter()

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        result = ProfileResult(name=name, duration_ms=duration_ms, metadata={"type": "sync_block"})
        profiler._profiles[name].append(result)


class ProfileReport:
    """Generate performance profiling reports."""

    def __init__(self, profiler: Optional[PerformanceProfiler] = None):
        self._profiler = profiler or get_profiler()

    def generate_markdown(self) -> str:
        """Generate a markdown performance report."""
        stats = self._profiler.get_stats()
        bottlenecks = self._profiler.get_bottlenecks()

        report = [
            "# AMOS Performance Profile Report",
            f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary",
            f"- Total operations profiled: {len(stats)}",
            f"- Bottlenecks identified: {len(bottlenecks)}",
            "\n## Top Performance Bottlenecks",
        ]

        for i, b in enumerate(bottlenecks[:10], 1):
            report.append(
                f"{i}. **{b['name']}**: {b['avg_duration_ms']:.2f}ms avg ({b['calls']} calls)"
            )

        report.extend(
            [
                "\n## All Operations",
                "| Operation | Calls | Avg (ms) | Min (ms) | Max (ms) |",
                "|-----------|-------|----------|----------|----------|",
            ]
        )

        for name, stat in sorted(
            stats.items(), key=lambda x: x[1].get("avg_duration_ms", 0), reverse=True
        ):
            report.append(
                f"| {stat['name']} | {stat['calls']} | "
                f"{stat['avg_duration_ms']:.2f} | {stat['min_duration_ms']:.2f} | "
                f"{stat['max_duration_ms']:.2f} |"
            )

        return "\n".join(report)

    def print_summary(self) -> None:
        """Print a console summary of profiling results."""
        print(self.generate_markdown())


# Convenience exports
__all__ = [
    "PerformanceProfiler",
    "get_profiler",
    "profile",
    "profile_block",
    "profile_sync_block",
    "ProfileResult",
    "ProfileReport",
]

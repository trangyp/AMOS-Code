#!/usr/bin/env python3
"""AMOS Ecosystem v2.0 - Performance Benchmarking Suite.

Measures performance metrics for all critical components:
- Cognitive routing latency
- Multi-agent orchestration throughput
- Organism bridge response times
- Memory usage patterns
"""

import sys
import time
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, stdev
from typing import Any, Callable

import psutil

# Add paths
sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""

    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    memory_mb: float
    throughput_ops_sec: float


class PerformanceBenchmark:
    """Benchmark suite for AMOS Ecosystem."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.process = psutil.Process()

    def _measure_memory(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def _run_benchmark(
        self, name: str, fn: Callable[[], Any], iterations: int = 100, warmup: int = 10
    ) -> BenchmarkResult:
        """Run a benchmark and collect metrics."""
        print(f"  Benchmarking: {name} ({iterations} iterations)...")

        # Warmup
        for _ in range(warmup):
            try:
                fn()
            except Exception:
                pass

        # Measure
        times = []
        memory_start = self._measure_memory()

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                fn()
            except Exception as e:
                print(f"    Error: {e}")
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        memory_end = self._measure_memory()

        total_time = sum(times)
        avg_time = mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = stdev(times) if len(times) > 1 else 0
        throughput = iterations / (total_time / 1000)  # ops/sec

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            std_dev_ms=std_dev,
            memory_mb=memory_end - memory_start,
            throughput_ops_sec=throughput,
        )

        self.results.append(result)
        return result

    def benchmark_cognitive_router(self) -> BenchmarkResult:
        """Benchmark cognitive routing performance."""
        from amos_cognitive_router import CognitiveRouter

        router = CognitiveRouter()
        tasks = [
            "Design REST API endpoint",
            "Implement authentication",
            "Optimize database query",
            "Write unit tests",
            "Deploy to production",
        ]
        counter = [0]

        def task():
            task_desc = tasks[counter[0] % len(tasks)]
            router.analyze(task_desc)
            counter[0] += 1

        return self._run_benchmark("Cognitive Router", task, 50)

    def benchmark_organism_bridge(self) -> BenchmarkResult:
        """Benchmark organism bridge performance."""
        from organism_bridge import get_organism_bridge

        bridge = get_organism_bridge()

        def task():
            bridge.enhance_cognitive_analysis("Test task for benchmarking")

        return self._run_benchmark("Organism Bridge", task, 50)

    def benchmark_master_orchestrator(self) -> BenchmarkResult:
        """Benchmark master orchestrator performance."""
        from master_orchestrator import MasterOrchestrator

        orchestrator = MasterOrchestrator()
        counter = [0]

        def task():
            orchestrator.orchestrate_cognitive_task(
                f"bench_{counter[0]}", "Design microservice architecture", "HIGH"
            )
            counter[0] += 1

        return self._run_benchmark("Master Orchestrator", task, 20)

    def benchmark_system_validator(self) -> BenchmarkResult:
        """Benchmark system validator performance."""
        from system_validator import SystemValidator

        def task():
            validator = SystemValidator()
            validator.validate_all()

        return self._run_benchmark("System Validator", task, 10)

    def benchmark_dashboard_server(self) -> BenchmarkResult:
        """Benchmark dashboard server startup."""
        from dashboard_server import DashboardServer

        def task():
            server = DashboardServer(port=0)
            server.get_status()

        return self._run_benchmark("Dashboard Server", task, 20)

    def run_all_benchmarks(self) -> None:
        """Run complete benchmark suite."""
        print("=" * 70)
        print("AMOS ECOSYSTEM v2.0 - PERFORMANCE BENCHMARK SUITE")
        print("=" * 70)
        print(f"Started: {datetime.now().isoformat()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Platform: {sys.platform}")
        print("=" * 70)
        print()

        benchmarks = [
            self.benchmark_cognitive_router,
            self.benchmark_organism_bridge,
            self.benchmark_master_orchestrator,
            self.benchmark_system_validator,
            self.benchmark_dashboard_server,
        ]

        for benchmark_fn in benchmarks:
            try:
                benchmark_fn()
            except Exception as e:
                print(f"  Failed: {e}")
            print()

        self._print_summary()

    def _print_summary(self) -> None:
        """Print benchmark summary."""
        print("=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)
        print()

        # Header
        print(
            f"{'Component':<25} {'Avg (ms)':<12} {'Min (ms)':<12} "
            f"{'Max (ms)':<12} {'Throughput':<15}"
        )
        print("-" * 70)

        # Results
        for r in self.results:
            print(
                f"{r.name:<25} {r.avg_time_ms:<12.2f} {r.min_time_ms:<12.2f} "
                f"{r.max_time_ms:<12.2f} {r.throughput_ops_sec:<15.1f}"
            )

        print("-" * 70)
        print()

        # Performance grades
        print("PERFORMANCE GRADES:")
        for r in self.results:
            grade = self._grade_performance(r.avg_time_ms, r.name)
            print(f"  {r.name:<25} {grade}")

        print()
        print("=" * 70)

        # Overall score
        avg_throughput = mean([r.throughput_ops_sec for r in self.results])
        print(f"Overall: {avg_throughput:.1f} ops/sec")

        if all(r.avg_time_ms < 100 for r in self.results):
            print("Performance Status: 🟢 EXCELLENT")
        elif all(r.avg_time_ms < 500 for r in self.results):
            print("Performance Status: 🟢 GOOD")
        else:
            print("Performance Status: 🟡 ACCEPTABLE")

        print("=" * 70)

    def _grade_performance(self, avg_ms: float, name: str) -> str:
        """Assign performance grade."""
        thresholds = {
            "Cognitive Router": (10, 50, 100),
            "Organism Bridge": (20, 100, 200),
            "Master Orchestrator": (50, 200, 500),
            "System Validator": (100, 500, 1000),
            "Dashboard Server": (10, 50, 100),
        }

        low, med, high = thresholds.get(name, (50, 200, 500))

        if avg_ms < low:
            return f"🟢 EXCELLENT (<{low:.0f}ms)"
        elif avg_ms < med:
            return f"🟢 GOOD (<{med:.0f}ms)"
        elif avg_ms < high:
            return f"🟡 ACCEPTABLE (<{high:.0f}ms)"
        else:
            return f"🔴 NEEDS OPTIMIZATION (>={high:.0f}ms)"

    def export_results(self, filename: str = "benchmark_results.json") -> None:
        """Export results to JSON."""
        import json

        data = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform,
            "results": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "total_time_ms": r.total_time_ms,
                    "avg_time_ms": r.avg_time_ms,
                    "min_time_ms": r.min_time_ms,
                    "max_time_ms": r.max_time_ms,
                    "std_dev_ms": r.std_dev_ms,
                    "memory_mb": r.memory_mb,
                    "throughput_ops_sec": r.throughput_ops_sec,
                }
                for r in self.results
            ],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults exported to: {filename}")


def main():
    """Main entry point."""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
    benchmark.export_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())

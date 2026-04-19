"""AMOS Benchmark Suite v21.0.0"""

import time
import tracemalloc
from dataclasses import dataclass
from statistics import mean


@dataclass
class BenchmarkResult:
    name: str
    phase: str
    mean_ms: float
    ops_per_sec: float


class AMOSBenchmark:
    """Benchmark suite for AMOS SuperBrain."""

    def benchmark_phase(
        self, name: str, phase: str, func, iterations: int = 100
    ) -> BenchmarkResult:
        """Benchmark a function."""
        times = []
        tracemalloc.start()

        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append((end - start) * 1000)

        tracemalloc.stop()
        mean_ms = mean(times)

        return BenchmarkResult(
            name=name,
            phase=phase,
            mean_ms=mean_ms,
            ops_per_sec=1000.0 / mean_ms if mean_ms > 0 else 0,
        )

    def run_all(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        results = []

        # SuperBrain benchmark
        try:
            from amos_superbrain_equation_bridge import AMOSSuperBrainBridge

            bridge = AMOSSuperBrainBridge()
            results.append(
                self.benchmark_phase(
                    "sigmoid", "superbrain", lambda: bridge.compute("sigmoid", {"x": 0.5})
                )
            )
        except Exception as e:
            print(f"SuperBrain benchmark failed: {e}")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Run all benchmarks")
    args = parser.parse_args()

    if args.all:
        print("AMOS Benchmark Suite v21.0.0")
        print("=" * 40)

        benchmark = AMOSBenchmark()
        results = benchmark.run_all()

        print(f"\nRan {len(results)} benchmarks:\n")
        for r in results:
            print(f"  {r.name}: {r.mean_ms:.3f}ms ({r.ops_per_sec:.1f} ops/sec)")

        print("\nBenchmark complete!")
    else:
        print("Use --all to run benchmarks")


if __name__ == "__main__":
    main()

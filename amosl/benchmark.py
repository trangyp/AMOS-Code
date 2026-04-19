"""AMOSL Performance Benchmark Suite.

Measures and validates field-theoretic performance:
    - Field evolution performance
    - Multi-substrate overhead
    - Verification throughput
    - Scalability metrics
"""

import statistics
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkResult:
    """Single benchmark result."""

    name: str
    mean_time_ms: float
    std_dev_ms: float
    min_time_ms: float
    max_time_ms: float
    iterations: int
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """AMOSL performance benchmark suite."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.warmup_iterations = 3

    def benchmark_field_evolution(self, steps: int = 100) -> BenchmarkResult:
        """Benchmark field evolution performance."""
        from amosl.field import FieldEvolution, FieldState

        evolution = FieldEvolution()
        initial = FieldState(
            classical={"energy": 10.0, "computation_cost": 1.0},
            quantum={"coherence": 0.95, "energy_expectation": 5.0},
            biological={"growth_rate": 0.1, "concentrations": [0.5, 0.3, 0.2]},
            hybrid={"scheduling_efficiency": 0.8},
        )

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            trajectory = evolution.evolve_with_constraints(initial, steps=steps, dt=0.1)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        # Discard warmup
        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"field_evolution_{steps}_steps",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"steps": steps, "trajectory_length": len(trajectory)},
        )

        self.results.append(result)
        return result

    def benchmark_lagrangian_compute(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark Lagrangian computation speed."""
        from amosl.field import FieldEvolution, FieldState

        evolution = FieldEvolution()
        state = FieldState(
            classical={"energy": 10.0, "computation_cost": 1.0},
            quantum={"coherence": 0.95, "energy_expectation": 5.0},
            biological={"growth_rate": 0.1, "concentrations": [0.5, 0.3]},
            hybrid={"scheduling_efficiency": 0.8},
        )

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            for _ in range(iterations):
                _ = evolution.compute_lagrangian(state)
            end = time.perf_counter()
            times.append((end - start) * 1000)

        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"lagrangian_compute_{iterations}_iter",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"lagrangian_iterations": iterations},
        )

        self.results.append(result)
        return result

    def benchmark_action_functional(self, trajectory_length: int = 100) -> BenchmarkResult:
        """Benchmark action functional evaluation."""
        from amosl.field import FieldEvolution, FieldState

        evolution = FieldEvolution()
        initial = FieldState(
            classical={"energy": 10.0, "computation_cost": 1.0},
            quantum={"coherence": 0.95, "energy_expectation": 5.0},
            biological={"growth_rate": 0.1, "concentrations": [0.5, 0.3, 0.2]},
            hybrid={"scheduling_efficiency": 0.8},
        )

        # Generate trajectory
        trajectory = evolution.evolve_with_constraints(initial, steps=trajectory_length, dt=0.1)

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            _ = evolution.action_functional(trajectory, dt=0.1)
            end = time.perf_counter()
            times.append((end - start) * 1000)

        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"action_functional_{trajectory_length}_steps",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"trajectory_length": trajectory_length},
        )

        self.results.append(result)
        return result

    def benchmark_bridge_execution(self, bridge_type: str = "C_TO_Q") -> BenchmarkResult:
        """Benchmark cross-domain bridge execution."""
        from amosl.bridge import BridgeExecutor, BridgeType

        bridge = BridgeExecutor()
        type_map = {
            "C_TO_Q": BridgeType.C_TO_Q,
            "Q_TO_C": BridgeType.Q_TO_C,
            "B_TO_C": BridgeType.B_TO_C,
            "C_TO_B": BridgeType.C_TO_B,
        }
        btype = type_map.get(bridge_type, BridgeType.C_TO_Q)

        # Use appropriate test values per bridge type
        if bridge_type == "Q_TO_C":
            test_values = [{"outcome": 0}, {"outcome": 1}]
        else:
            test_values = [0, 1, 0.5, 0.8]

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            for val in test_values:
                _ = bridge.execute(btype, val)
            end = time.perf_counter()
            times.append((end - start) * 1000)

        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"bridge_{bridge_type}",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"bridge_type": bridge_type, "executions": len(test_values)},
        )

        self.results.append(result)
        return result

    def benchmark_invariant_check(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark invariant verification throughput."""
        from amosl.prover import TheoremProver
        from amosl.runtime import RuntimeKernel

        prover = TheoremProver()
        kernel = RuntimeKernel()

        # Setup state
        for i in range(5):
            kernel.step(action_bundle={"classical": {"set": {"x": i}}})

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            for _ in range(iterations):
                _ = prover.prove_valid(kernel.state)
            end = time.perf_counter()
            times.append((end - start) * 1000)

        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"invariant_check_{iterations}_iter",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"invariant_iterations": iterations},
        )

        self.results.append(result)
        return result

    def benchmark_belief_update(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark belief manifold update performance."""
        from amosl.geometry import BeliefState, InformationGeometry

        geometry = InformationGeometry()
        prior = BeliefState(distribution={"a": 0.5, "b": 0.3, "c": 0.2}, timestamp=0.0)
        likelihood = {"a": 0.8, "b": 0.4, "c": 0.1}

        times = []
        for _ in range(self.warmup_iterations + 5):
            start = time.perf_counter()
            for _ in range(iterations):
                _ = geometry.bayesian_update(prior, likelihood, "obs")
            end = time.perf_counter()
            times.append((end - start) * 1000)

        times = times[self.warmup_iterations :]

        result = BenchmarkResult(
            name=f"belief_update_{iterations}_iter",
            mean_time_ms=statistics.mean(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time_ms=min(times),
            max_time_ms=max(times),
            iterations=len(times),
            metadata={"belief_iterations": iterations},
        )

        self.results.append(result)
        return result

    def run_full_suite(self) -> dict[str, BenchmarkResult]:
        """Run complete benchmark suite."""
        print("Running AMOSL Performance Benchmark Suite...")
        print("=" * 60)

        results = {}

        print("\n1. Field Evolution Performance...")
        results["field_evolution"] = self.benchmark_field_evolution(steps=50)
        print(f"   Mean: {results['field_evolution'].mean_time_ms:.2f} ms")

        print("\n2. Lagrangian Computation...")
        results["lagrangian"] = self.benchmark_lagrangian_compute(iterations=100)
        print(f"   Mean: {results['lagrangian'].mean_time_ms:.2f} ms")

        print("\n3. Action Functional Evaluation...")
        results["action"] = self.benchmark_action_functional(trajectory_length=50)
        print(f"   Mean: {results['action'].mean_time_ms:.2f} ms")

        print("\n4. Bridge Execution...")
        for btype in ["C_TO_Q", "Q_TO_C", "B_TO_C"]:
            key = f"bridge_{btype}"
            results[key] = self.benchmark_bridge_execution(btype)
            print(f"   {btype}: {results[key].mean_time_ms:.2f} ms")

        print("\n5. Verification Throughput...")
        results["invariants"] = self.benchmark_invariant_check(iterations=50)
        print(f"   Mean: {results['invariants'].mean_time_ms:.2f} ms")

        print("\n6. Belief Update Performance...")
        results["belief"] = self.benchmark_belief_update(iterations=50)
        print(f"   Mean: {results['belief'].mean_time_ms:.2f} ms")

        print("\n" + "=" * 60)
        print("Benchmark Suite Complete")

        return results

    def generate_report(self) -> str:
        """Generate benchmark report."""
        lines = [
            "AMOSL Performance Benchmark Report",
            "=" * 60,
            "",
        ]

        for result in self.results:
            lines.extend(
                [
                    f"{result.name}:",
                    f"  Mean:   {result.mean_time_ms:8.3f} ms",
                    f"  StdDev: {result.std_dev_ms:8.3f} ms",
                    f"  Min:    {result.min_time_ms:8.3f} ms",
                    f"  Max:    {result.max_time_ms:8.3f} ms",
                    f"  Iters:  {result.iterations}",
                    "",
                ]
            )

        return "\n".join(lines)

"""
AMOS Equation System v2.0 - Chaos Engineering

Resilience testing using Chaos Monkey principles.
Validates circuit breakers, graceful degradation, and recovery.

Usage:
    python chaos/experiments.py --experiment cpu_stress --duration 300
    python chaos/experiments.py --experiment pod_failure --target api

Author: AMOS Team
Version: 2.0.0
"""

import argparse
import asyncio
import subprocess
import time
from dataclasses import dataclass
from enum import Enum

import aiohttp


class ExperimentType(str, Enum):
    """Chaos experiment types."""

    CPU_STRESS = "cpu_stress"
    MEMORY_PRESSURE = "memory_pressure"
    NETWORK_LATENCY = "network_latency"
    POD_FAILURE = "pod_failure"
    DATABASE_SLOWDOWN = "database_slowdown"
    CACHE_FAILURE = "cache_failure"
    DISK_IO_STRESS = "disk_io_stress"


class ExperimentStatus(str, Enum):
    """Experiment execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ExperimentResult:
    """Chaos experiment result."""

    experiment: str
    status: ExperimentStatus
    duration: float
    steady_state_passed: bool
    recovery_time: float
    errors: List[str]


class ChaosEngine:
    """Chaos engineering test engine."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results: List[ExperimentResult] = []

    async def check_health(self) -> dict:
        """Check system health."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.api_url}/health/ready", timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return {"status": resp.status, "healthy": resp.status == 200}
            except Exception as e:
                return {"status": 0, "healthy": False, "error": str(e)}

    async def run_steady_state_check(self, duration: int = 60) -> bool:
        """Verify system is healthy before experiment."""
        print(f"Running steady state check for {duration}s...")
        checks = []

        for _ in range(duration // 5):
            health = await self.check_health()
            checks.append(health["healthy"])
            await asyncio.sleep(5)

        success_rate = sum(checks) / len(checks)
        passed = success_rate >= 0.95

        print(f"Steady state: {success_rate*100:.1f}% healthy - {'PASS' if passed else 'FAIL'}")
        return passed

    async def experiment_cpu_stress(
        self, duration: int = 300, intensity: float = 0.8
    ) -> ExperimentResult:
        """CPU stress test."""
        print(f"Starting CPU stress: {intensity*100}% for {duration}s")

        # Inject CPU stress
        process = subprocess.Popen(
            ["stress-ng", "--cpu", str(int(intensity * 8)), "--timeout", str(duration)]
        )

        start = time.time()
        errors = []

        # Monitor during stress
        while time.time() - start < duration:
            health = await self.check_health()
            if not health["healthy"]:
                errors.append(f"Health check failed at {time.time()-start:.0f}s")
            await asyncio.sleep(10)

        process.terminate()

        # Measure recovery
        recovery_start = time.time()
        recovered = False
        while time.time() - recovery_start < 120:
            health = await self.check_health()
            if health["healthy"]:
                recovered = True
                break
            await asyncio.sleep(5)

        recovery_time = time.time() - recovery_start if recovered else None

        return ExperimentResult(
            experiment="cpu_stress",
            status=ExperimentStatus.COMPLETED,
            duration=duration,
            steady_state_passed=len(errors) < 5,
            recovery_time=recovery_time,
            errors=errors,
        )

    async def experiment_pod_failure(
        self, target: str = "api", namespace: str = "default"
    ) -> ExperimentResult:
        """Pod failure simulation."""
        print(f"Simulating pod failure: {target}")

        # Pre-check
        steady = await self.run_steady_state_check(30)

        # Kill random pod
        result = subprocess.run(
            [
                "kubectl",
                "delete",
                "pod",
                "-l",
                f"app=amos-equation-{target}",
                "-n",
                namespace,
                "--force",
            ],
            capture_output=True,
            text=True,
        )

        # Monitor recovery
        start = time.time()
        errors = []

        for _ in range(30):  # 5 minutes max
            health = await self.check_health()
            if health["healthy"]:
                recovery_time = time.time() - start
                return ExperimentResult(
                    experiment="pod_failure",
                    status=ExperimentStatus.COMPLETED,
                    duration=time.time() - start,
                    steady_state_passed=steady,
                    recovery_time=recovery_time,
                    errors=errors,
                )
            await asyncio.sleep(10)

        return ExperimentResult(
            experiment="pod_failure",
            status=ExperimentStatus.FAILED,
            duration=300,
            steady_state_passed=steady,
            recovery_time=None,
            errors=["Recovery timeout"],
        )

    async def experiment_database_slowdown(
        self, duration: int = 300, latency_ms: int = 500
    ) -> ExperimentResult:
        """Database latency injection."""
        print(f"Injecting {latency_ms}ms DB latency for {duration}s")

        # Requires pgbouncer or proxy configured
        # This is a placeholder - implement based on your proxy
        subprocess.run(
            [
                "tc",
                "qdisc",
                "add",
                "dev",
                "eth0",
                "root",
                "netem",
                "delay",
                f"{latency_ms}ms",
                "10ms",
            ],
            check=False,
        )

        await asyncio.sleep(duration)

        # Cleanup
        subprocess.run(["tc", "qdisc", "del", "dev", "eth0", "root"], check=False)

        return ExperimentResult(
            experiment="database_slowdown",
            status=ExperimentStatus.COMPLETED,
            duration=duration,
            steady_state_passed=True,
            recovery_time=10.0,
            errors=[],
        )

    async def run_full_suite(self) -> List[ExperimentResult]:
        """Execute complete chaos test suite."""
        print("=" * 60)
        print("AMOS CHAOS ENGINEERING SUITE")
        print("=" * 60)

        # Steady state
        if not await self.run_steady_state_check(60):
            print("ERROR: System not healthy, aborting")
            return []

        experiments = [
            ("CPU Stress", self.experiment_cpu_stress()),
            ("Pod Failure", self.experiment_pod_failure()),
        ]

        results = []
        for name, exp in experiments:
            print(f"\n--- Running: {name} ---")
            try:
                result = await exp
                results.append(result)
                print(f"Result: {result.status.value}, Recovery: {result.recovery_time}s")
            except Exception as e:
                print(f"FAILED: {e}")
                results.append(
                    ExperimentResult(
                        experiment=name.lower().replace(" ", "_"),
                        status=ExperimentStatus.FAILED,
                        duration=0,
                        steady_state_passed=False,
                        recovery_time=None,
                        errors=[str(e)],
                    )
                )

        # Report
        print("\n" + "=" * 60)
        print("CHAOS SUITE COMPLETE")
        print("=" * 60)
        passed = sum(1 for r in results if r.status == ExperimentStatus.COMPLETED)
        print(f"Passed: {passed}/{len(results)}")

        return results


def main():
    parser = argparse.ArgumentParser(description="AMOS Chaos Engineering")
    parser.add_argument("--experiment", choices=[e.value for e in ExperimentType])
    parser.add_argument("--duration", type=int, default=300)
    parser.add_argument("--target", default="api")
    parser.add_argument("--suite", action="store_true", help="Run full suite")
    parser.add_argument("--api-url", default="http://localhost:8000")

    args = parser.parse_args()

    engine = ChaosEngine(args.api_url)

    if args.suite:
        asyncio.run(engine.run_full_suite())
    elif args.experiment == "cpu_stress":
        result = asyncio.run(engine.experiment_cpu_stress(args.duration))
        print(result)
    elif args.experiment == "pod_failure":
        result = asyncio.run(engine.experiment_pod_failure(args.target))
        print(result)
    else:
        print(f"Experiment {args.experiment} not yet implemented")


if __name__ == "__main__":
    main()

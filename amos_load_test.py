#!/usr/bin/env python3
"""AMOS Load Testing Suite - Performance and Stress Testing

Features:
- Concurrent request load generation
- Endpoint-specific testing
- Gradual ramp-up and spike testing
- Real-time metrics validation
- Performance baseline establishment

Usage:
    python amos_load_test.py --duration 60 --concurrency 10
    python amos_load_test.py --endpoint /think --ramp-up
"""

import argparse
import asyncio
import json
import statistics
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime

import aiohttp
from typing import Dict, List


@dataclass
class LoadTestResult:
    """Result of a load test."""

    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: Dict[str, int] = field(default_factory=dict)
    start_time: datetime = None
    end_time: datetime = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

    @property
    def requests_per_second(self) -> float:
        if self.duration_seconds > 0:
            return self.total_requests / self.duration_seconds
        return 0

    @property
    def avg_response_time(self) -> float:
        if self.response_times:
            return statistics.mean(self.response_times)
        return 0

    @property
    def p95_response_time(self) -> float:
        if len(self.response_times) > 1:
            sorted_times = sorted(self.response_times)
            idx = int(len(sorted_times) * 0.95)
            return sorted_times[idx]
        return self.avg_response_time

    @property
    def error_rate(self) -> float:
        if self.total_requests > 0:
            return (self.failed / self.total_requests) * 100
        return 0


class AMOSLoadTester:
    """Load testing suite for AMOS Brain API."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.results = LoadTestResult()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    async def test_health_endpoint(self, session: aiohttp.ClientSession) -> bool:
        """Test health endpoint."""
        start = time.time()
        try:
            async with session.get(f"{self.base_url}/health", timeout=5) as resp:
                duration = time.time() - start
                with self._lock:
                    self.results.response_times.append(duration * 1000)
                    self.results.total_requests += 1
                    if resp.status == 200:
                        self.results.successful += 1
                        return True
                    else:
                        self.results.failed += 1
                        error_key = f"HTTP_{resp.status}"
                        self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
                        return False
        except Exception as e:
            with self._lock:
                self.results.total_requests += 1
                self.results.failed += 1
                error_key = type(e).__name__
                self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
            return False

    async def test_think_endpoint(self, session: aiohttp.ClientSession) -> bool:
        """Test think endpoint."""
        start = time.time()
        try:
            payload = {"query": "What is the load test query?", "domain": "software"}
            async with session.post(f"{self.base_url}/think", json=payload, timeout=30) as resp:
                duration = time.time() - start
                with self._lock:
                    self.results.response_times.append(duration * 1000)
                    self.results.total_requests += 1
                    if resp.status == 200:
                        self.results.successful += 1
                        return True
                    else:
                        self.results.failed += 1
                        error_key = f"HTTP_{resp.status}"
                        self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
                        return False
        except Exception as e:
            with self._lock:
                self.results.total_requests += 1
                self.results.failed += 1
                error_key = type(e).__name__
                self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
            return False

    async def test_decide_endpoint(self, session: aiohttp.ClientSession) -> bool:
        """Test decide endpoint."""
        start = time.time()
        try:
            payload = {"question": "Should we run a load test?", "options": ["Yes", "No"]}
            async with session.post(f"{self.base_url}/decide", json=payload, timeout=30) as resp:
                duration = time.time() - start
                with self._lock:
                    self.results.response_times.append(duration * 1000)
                    self.results.total_requests += 1
                    if resp.status == 200:
                        self.results.successful += 1
                        return True
                    else:
                        self.results.failed += 1
                        error_key = f"HTTP_{resp.status}"
                        self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
                        return False
        except Exception as e:
            with self._lock:
                self.results.total_requests += 1
                self.results.failed += 1
                error_key = type(e).__name__
                self.results.errors[error_key] = self.results.errors.get(error_key, 0) + 1
            return False

    async def run_constant_load(self, duration: int, concurrency: int, endpoint: str = "mixed"):
        """Run constant load test."""
        print("\n🚀 Starting constant load test")
        print(f"   Duration: {duration}s | Concurrency: {concurrency} | Endpoint: {endpoint}")

        self.results.start_time = datetime.now(timezone.utc)
        self._stop_event.clear()

        async with aiohttp.ClientSession() as session:
            # Pre-warm
            await self._warmup(session)

            # Start workers
            tasks = [self._worker(session, duration, endpoint) for _ in range(concurrency)]

            await asyncio.gather(*tasks)

        self.results.end_time = datetime.now(timezone.utc)

    async def _warmup(self, session: aiohttp.ClientSession):
        """Warmup the system."""
        print("   Warming up...")
        for _ in range(5):
            await self.test_health_endpoint(session)
        await asyncio.sleep(1)

    async def _worker(self, session: aiohttp.ClientSession, duration: int, endpoint: str):
        """Worker that sends requests until duration expires."""
        end_time = time.time() + duration

        while time.time() < end_time and not self._stop_event.is_set():
            if endpoint == "health":
                await self.test_health_endpoint(session)
            elif endpoint == "think":
                await self.test_think_endpoint(session)
            elif endpoint == "decide":
                await self.test_decide_endpoint(session)
            else:  # mixed
                import random

                choice = random.choice(["health", "think", "decide"])
                if choice == "health":
                    await self.test_health_endpoint(session)
                elif choice == "think":
                    await self.test_think_endpoint(session)
                else:
                    await self.test_decide_endpoint(session)

    async def run_ramp_up_test(self, max_concurrency: int = 50, step: int = 5):
        """Run ramp-up test to find breaking point."""
        print(f"\n📈 Starting ramp-up test (max: {max_concurrency}, step: {step})")

        results_by_concurrency = {}

        for concurrency in range(step, max_concurrency + 1, step):
            print(f"\n   Testing with {concurrency} concurrent connections...")

            # Reset results for this step
            self.results = LoadTestResult()

            await self.run_constant_load(duration=30, concurrency=concurrency)

            results_by_concurrency[concurrency] = {
                "rps": self.results.requests_per_second,
                "avg_latency": self.results.avg_response_time,
                "p95_latency": self.results.p95_response_time,
                "error_rate": self.results.error_rate,
                "total_requests": self.results.total_requests,
            }

            print(
                f"   RPS: {self.results.requests_per_second:.1f} | "
                f"Avg: {self.results.avg_response_time:.0f}ms | "
                f"Errors: {self.results.error_rate:.1f}%"
            )

            # Stop if error rate exceeds 5%
            if self.results.error_rate > 5:
                print(f"   ⚠️  Breaking point reached at {concurrency} concurrency")
                break

        return results_by_concurrency

    def print_report(self):
        """Print test report."""
        print("\n" + "=" * 70)
        print("📊 LOAD TEST RESULTS")
        print("=" * 70)
        print(f"Duration: {self.results.duration_seconds:.1f}s")
        print(f"Total Requests: {self.results.total_requests}")
        print(f"Successful: {self.results.successful}")
        print(f"Failed: {self.results.failed}")
        print("\n📈 Performance:")
        print(f"   Requests/sec: {self.results.requests_per_second:.1f}")
        print(f"   Avg Response: {self.results.avg_response_time:.1f}ms")
        print(f"   P95 Response: {self.results.p95_response_time:.1f}ms")
        print(
            f"   Min Response: {min(self.results.response_times):.1f}ms"
            if self.results.response_times
            else "   N/A"
        )
        print(
            f"   Max Response: {max(self.results.response_times):.1f}ms"
            if self.results.response_times
            else "   N/A"
        )
        print(f"\n❌ Errors: {self.results.error_rate:.2f}%")
        if self.results.errors:
            for error, count in sorted(self.results.errors.items(), key=lambda x: -x[1]):
                print(f"   {error}: {count}")
        print("=" * 70)

        # Performance grade
        if self.results.error_rate < 1 and self.results.avg_response_time < 200:
            print("🏆 Grade: EXCELLENT")
        elif self.results.error_rate < 5 and self.results.avg_response_time < 500:
            print("✅ Grade: GOOD")
        elif self.results.error_rate < 10:
            print("⚠️  Grade: ACCEPTABLE")
        else:
            print("❌ Grade: POOR")

    def save_report(self, filename: str = "load_test_report.json"):
        """Save report to file."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_url": self.base_url,
            "total_requests": self.results.total_requests,
            "successful": self.results.successful,
            "failed": self.results.failed,
            "duration_seconds": self.results.duration_seconds,
            "requests_per_second": self.results.requests_per_second,
            "avg_response_time_ms": self.results.avg_response_time,
            "p95_response_time_ms": self.results.p95_response_time,
            "error_rate": self.results.error_rate,
            "errors": self.results.errors,
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="AMOS Load Testing Suite")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent connections")
    parser.add_argument(
        "--endpoint",
        default="mixed",
        choices=["health", "think", "decide", "mixed"],
        help="Endpoint to test",
    )
    parser.add_argument("--ramp-up", action="store_true", help="Run ramp-up test")
    parser.add_argument("--output", default="load_test_report.json", help="Output file")

    args = parser.parse_args()

    print("=" * 70)
    print("🧪 AMOS LOAD TESTING SUITE")
    print("=" * 70)
    print(f"Target: {args.url}")

    tester = AMOSLoadTester(args.url)

    try:
        if args.ramp_up:
            asyncio.run(tester.run_ramp_up_test())
        else:
            asyncio.run(
                tester.run_constant_load(
                    duration=args.duration, concurrency=args.concurrency, endpoint=args.endpoint
                )
            )

        tester.print_report()
        tester.save_report(args.output)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        tester.print_report()


if __name__ == "__main__":
    main()

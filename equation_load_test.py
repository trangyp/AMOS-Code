#!/usr/bin/env python3
"""Load testing script for AMOS Equation API."""

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[ERROR] requests not installed. pip install requests")
    sys.exit(1)

try:
    import websockets

    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class EquationAPILoadTest:
    """Load test suite for Equation API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url
        self.results: List[dict[str, Any]] = []

    def test_health_endpoint(self, iterations: int = 100) -> Dict[str, Any]:
        """Test health check endpoint."""
        url = f"{self.base_url}/health/"
        times = []
        errors = 0

        for _ in range(iterations):
            start = time.time()
            try:
                r = requests.get(url, timeout=5)
                if r.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            times.append(time.time() - start)

        return {
            "endpoint": "health",
            "iterations": iterations,
            "errors": errors,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "rps": iterations / sum(times),
        }

    def test_verify_endpoint(self, iterations: int = 50) -> Dict[str, Any]:
        """Test verification endpoint."""
        url = f"{self.base_url}/api/equations/verify"
        code = "def test():\n    x = []\n    return x"
        times = []
        errors = 0

        for _ in range(iterations):
            start = time.time()
            try:
                r = requests.post(url, json={"code": code, "language": "python"}, timeout=10)
                if r.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            times.append(time.time() - start)

        return {
            "endpoint": "verify",
            "iterations": iterations,
            "errors": errors,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "rps": iterations / sum(times),
        }

    def test_query_endpoint(self, iterations: int = 100) -> Dict[str, Any]:
        """Test query endpoint."""
        url = f"{self.base_url}/api/equations/query"
        times = []
        errors = 0

        for _ in range(iterations):
            start = time.time()
            try:
                r = requests.get(url, params={"language": "python"}, timeout=5)
                if r.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            times.append(time.time() - start)

        return {
            "endpoint": "query",
            "iterations": iterations,
            "errors": errors,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "rps": iterations / sum(times),
        }

    def run_concurrent_test(self, concurrency: int = 10) -> Dict[str, Any]:
        """Run concurrent load test."""
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.test_health_endpoint, 20) for _ in range(concurrency)]
            results = [f.result() for f in futures]

        total_rps = sum(r["rps"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        total_requests = sum(r["iterations"] for r in results)

        return {
            "concurrency": concurrency,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "combined_rps": total_rps,
            "error_rate": total_errors / total_requests if total_requests else 0,
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute full test suite."""
        print("=" * 60)
        print("AMOS Equation API Load Test Suite")
        print("=" * 60)

        tests = [
            ("Health Endpoint", self.test_health_endpoint, 100),
            ("Verify Endpoint", self.test_verify_endpoint, 50),
            ("Query Endpoint", self.test_query_endpoint, 100),
        ]

        for name, test_fn, iterations in tests:
            print(f"\n[TEST] {name} ({iterations} iterations)")
            result = test_fn(iterations)
            self.results.append(result)
            print(f"  Avg: {result['avg_time']:.3f}s")
            print(f"  RPS: {result['rps']:.2f}")
            print(f"  Errors: {result['errors']}/{iterations}")

        print("\n" + "=" * 60)
        print("Concurrent Load Test")
        print("=" * 60)
        concurrent = self.run_concurrent_test(concurrency=10)
        print(f"  Total Requests: {concurrent['total_requests']}")
        print(f"  Combined RPS: {concurrent['combined_rps']:.2f}")
        print(f"  Error Rate: {concurrent['error_rate']:.2%}")

        return {"tests": self.results, "concurrent": concurrent}


def main() -> int:
    """Run load tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test = EquationAPILoadTest(base_url)
    test.run_all_tests()
    return 0


if __name__ == "__main__":
    sys.exit(main())

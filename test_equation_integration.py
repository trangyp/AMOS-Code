#!/usr/bin/env python3
"""Comprehensive integration tests for AMOS Equation System."""

import json
import sys
import time
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))


class EquationIntegrationTest:
    """Full integration test suite."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url
        self.results: list[dict[str, Any]] = []
        self.passed = 0
        self.failed = 0

    def log(self, test: str, status: str, details: str = "") -> None:
        """Log test result."""
        symbol = "✓" if status == "PASS" else "✗"
        print(f"  {symbol} {test}: {status}")
        if details:
            print(f"      {details}")
        self.results.append({"test": test, "status": status, "details": details})
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1

    def test_api_startup(self) -> bool:
        """Test API is running."""
        try:
            r = requests.get(f"{self.base_url}/api/equations/status", timeout=5)
            if r.status_code == 200:
                self.log("API Startup", "PASS", f"Status: {r.json().get('health', 'unknown')}")
                return True
            else:
                self.log("API Startup", "FAIL", f"HTTP {r.status_code}")
                return False
        except Exception as e:
            self.log("API Startup", "FAIL", str(e))
            return False

    def test_metrics_endpoint(self) -> bool:
        """Test Prometheus metrics."""
        try:
            r = requests.get(f"{self.base_url}/metrics", timeout=5)
            if r.status_code == 200 and "amos_" in r.text:
                self.log("Metrics Endpoint", "PASS", "Prometheus metrics available")
                return True
            else:
                self.log("Metrics Endpoint", "FAIL", "Metrics not found")
                return False
        except Exception as e:
            self.log("Metrics Endpoint", "FAIL", str(e))
            return False

    def test_health_checks(self) -> bool:
        """Test all health endpoints."""
        endpoints = ["/health/", "/health/live", "/health/ready", "/health/detailed"]
        all_pass = True
        for ep in endpoints:
            try:
                r = requests.get(f"{self.base_url}{ep}", timeout=5)
                if r.status_code == 200:
                    self.log(f"Health {ep}", "PASS")
                else:
                    self.log(f"Health {ep}", "FAIL", f"HTTP {r.status_code}")
                    all_pass = False
            except Exception as e:
                self.log(f"Health {ep}", "FAIL", str(e))
                all_pass = False
        return all_pass

    def test_verification_api(self) -> bool:
        """Test code verification endpoint."""
        code = "def test():\n    x = []\n    return x"
        try:
            r = requests.post(
                f"{self.base_url}/api/equations/verify",
                json={"code": code, "language": "python"},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                violations = data.get("summary", {}).get("violations", 0)
                self.log("Verification API", "PASS", f"Found {violations} violations")
                return True
            else:
                self.log("Verification API", "FAIL", f"HTTP {r.status_code}")
                return False
        except Exception as e:
            self.log("Verification API", "FAIL", str(e))
            return False

    def test_query_api(self) -> bool:
        """Test equation query endpoint."""
        try:
            r = requests.get(
                f"{self.base_url}/api/equations/query", params={"language": "python"}, timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                count = len(data) if isinstance(data, list) else 0
                self.log("Query API", "PASS", f"Found {count} equations")
                return True
            else:
                self.log("Query API", "FAIL", f"HTTP {r.status_code}")
                return False
        except Exception as e:
            self.log("Query API", "FAIL", str(e))
            return False

    def test_websocket_connection(self) -> bool:
        """Test WebSocket streaming."""
        try:
            import websocket

            ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
            ws = websocket.create_connection(f"{ws_url}/ws/verify", timeout=5)
            ws.send(json.dumps({"code": "def test(): pass", "language": "python"}))
            response = ws.recv()
            ws.close()
            data = json.loads(response)
            if data.get("status") == "started":
                self.log("WebSocket Connection", "PASS", "Real-time streaming working")
                return True
            else:
                self.log("WebSocket Connection", "FAIL", "Unexpected response")
                return False
        except ImportError:
            self.log("WebSocket Connection", "SKIP", "websocket-client not installed")
            return True
        except Exception as e:
            self.log("WebSocket Connection", "FAIL", str(e))
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS is enabled."""
        try:
            r = requests.options(
                f"{self.base_url}/api/equations/verify",
                headers={"Origin": "http://localhost:3000"},
                timeout=5,
            )
            if "access-control-allow-origin" in r.headers:
                self.log("CORS Headers", "PASS", "CORS enabled")
                return True
            else:
                self.log("CORS Headers", "WARN", "CORS headers not present")
                return True  # Non-critical
        except Exception as e:
            self.log("CORS Headers", "FAIL", str(e))
            return False

    def test_end_to_end_workflow(self) -> bool:
        """Test complete user workflow."""
        try:
            # Step 1: Check status
            r1 = requests.get(f"{self.base_url}/api/equations/status", timeout=5)
            if r1.status_code != 200:
                self.log("E2E Workflow", "FAIL", "Status check failed")
                return False

            # Step 2: Verify code
            code = "def risky():\n    return []"
            r2 = requests.post(
                f"{self.base_url}/api/equations/verify",
                json={"code": code, "language": "python"},
                timeout=10,
            )
            if r2.status_code != 200:
                self.log("E2E Workflow", "FAIL", "Verification failed")
                return False

            # Step 3: Query equations
            r3 = requests.get(
                f"{self.base_url}/api/equations/query", params={"language": "python"}, timeout=5
            )
            if r3.status_code != 200:
                self.log("E2E Workflow", "FAIL", "Query failed")
                return False

            self.log("E2E Workflow", "PASS", "Full workflow completed")
            return True
        except Exception as e:
            self.log("E2E Workflow", "FAIL", str(e))
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute complete test suite."""
        print("\n" + "=" * 60)
        print("AMOS Equation System - Integration Test Suite")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print("=" * 60 + "\n")

        tests = [
            self.test_api_startup,
            self.test_health_checks,
            self.test_metrics_endpoint,
            self.test_verification_api,
            self.test_query_api,
            self.test_websocket_connection,
            self.test_cors_headers,
            self.test_end_to_end_workflow,
        ]

        for test in tests:
            test()
            time.sleep(0.1)

        print("\n" + "=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)

        return {
            "passed": self.passed,
            "failed": self.failed,
            "total": self.passed + self.failed,
            "success_rate": self.passed / (self.passed + self.failed)
            if (self.passed + self.failed) > 0
            else 0,
            "results": self.results,
        }


def main() -> int:
    """Run integration tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test = EquationIntegrationTest(base_url)
    results = test.run_all_tests()

    if results["failed"] > 0:
        print("\n✗ Some tests failed")
        return 1
    else:
        print("\n✓ All tests passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())

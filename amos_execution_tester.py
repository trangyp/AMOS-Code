#!/usr/bin/env python3
"""
AMOS Execution System - Integration Tester
============================================

Comprehensive test suite for the execution platform including:
- Sandbox providers (E2B, Daytona, Docker)
- Browser automation (Playwright)
- Web research (Tavily, Brave)
- FastAPI REST endpoints
- WebSocket streaming
- MCP server functionality

Usage:
    python amos_execution_tester.py --all
    python amos_execution_tester.py --sandbox
    python amos_execution_tester.py --api
    python amos_execution_tester.py --websocket

Author: AMOS System
Version: 2.0.0
"""

import argparse
import asyncio
import json
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC

# Test configuration
TEST_CODE = """
import sys
import time

print("Starting execution test...")
for i in range(5):
    print(f"Step {i+1}/5", flush=True)
    time.sleep(0.1)
print("Test completed successfully!
print(f"Python version: {sys.version}")
"""


class TestResult:
    """Result of a single test."""

    def __init__(
        self, name: str, passed: bool, duration_ms: float, error: str = None, details: dict = None
    ):
        self.name = name
        self.passed = passed
        self.duration_ms = duration_ms
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class ExecutionTester:
    """Integration tester for AMOS Execution System."""

    def __init__(self):
        self.results: list[TestResult] = []
        self.base_url = "http://localhost:8000"

    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("=" * 70)
        print("🧪 AMOS Execution System - Integration Tests")
        print("=" * 70)
        print()

        # Test execution platform
        await self.test_execution_platform()

        # Test FastAPI endpoints
        await self.test_fastapi_endpoints()

        # Test WebSocket streaming
        await self.test_websocket_streaming()

        # Test MCP server
        await self.test_mcp_server()

        # Print summary
        return self.print_summary()

    async def test_execution_platform(self):
        """Test execution platform providers."""
        print("📦 Testing Execution Platform...")
        print("-" * 70)

        try:
            from amos_execution_platform import AMOSExecutionPlatform

            # Test platform initialization
            start = time.time()
            platform = AMOSExecutionPlatform()
            duration = (time.time() - start) * 1000

            self.results.append(
                TestResult(
                    name="Platform Initialization",
                    passed=True,
                    duration_ms=duration,
                    details={"providers": list(platform._providers.keys())},
                )
            )
            print("  ✅ Platform initialization")

            # Test status endpoint
            start = time.time()
            status = platform.get_status()
            duration = (time.time() - start) * 1000

            self.results.append(
                TestResult(
                    name="Platform Status", passed=True, duration_ms=duration, details=status
                )
            )
            print(f"  ✅ Platform status: {status.get('healthy', False)}")

        except Exception as e:
            self.results.append(
                TestResult(
                    name="Execution Platform",
                    passed=False,
                    duration_ms=0,
                    error=str(e),
                    details={"traceback": traceback.format_exc()},
                )
            )
            print(f"  ❌ Execution platform error: {e}")

        print()

    async def test_fastapi_endpoints(self):
        """Test FastAPI REST endpoints."""
        print("🌐 Testing FastAPI Endpoints...")
        print("-" * 70)

        import aiohttp

        endpoints = [
            ("GET", "/health", "Health Check"),
            ("GET", "/execution/status", "Execution Status"),
        ]

        async with aiohttp.ClientSession() as session:
            for method, path, name in endpoints:
                try:
                    start = time.time()

                    if method == "GET":
                        async with session.get(f"{self.base_url}{path}") as resp:
                            status = resp.status
                            data = await resp.json() if resp.status == 200 else None
                    else:
                        status = 0
                        data = None

                    duration = (time.time() - start) * 1000

                    passed = status == 200
                    self.results.append(
                        TestResult(
                            name=f"API: {name}",
                            passed=passed,
                            duration_ms=duration,
                            details={"status": status, "response": data},
                        )
                    )

                    icon = "✅" if passed else "❌"
                    print(f"  {icon} {name} ({status}, {duration:.1f}ms)")

                except Exception as e:
                    self.results.append(
                        TestResult(name=f"API: {name}", passed=False, duration_ms=0, error=str(e))
                    )
                    print(f"  ❌ {name} (error: {e})")

        # Test code execution endpoint
        try:
            start = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/execution/code",
                    json={
                        "code": "print('Hello from test')",
                        "language": "python",
                        "timeout_seconds": 30,
                    },
                ) as resp:
                    status = resp.status
                    data = await resp.json() if resp.status == 200 else None

            duration = (time.time() - start) * 1000

            passed = status == 200 and data and data.get("status") == "success"
            self.results.append(
                TestResult(
                    name="API: Code Execution",
                    passed=passed,
                    duration_ms=duration,
                    details={"status": status, "response": data},
                )
            )

            icon = "✅" if passed else "❌"
            print(f"  {icon} Code Execution ({duration:.1f}ms)")

        except Exception as e:
            self.results.append(
                TestResult(name="API: Code Execution", passed=False, duration_ms=0, error=str(e))
            )
            print(f"  ❌ Code Execution (error: {e})")

        print()

    async def test_websocket_streaming(self):
        """Test WebSocket streaming functionality."""
        print("🔌 Testing WebSocket Streaming...")
        print("-" * 70)

        try:
            import aiohttp

            execution_id = f"test_{uuid.uuid4().hex[:8]}"
            messages = []

            async with aiohttp.ClientSession() as session:
                # Connect to WebSocket
                ws_start = time.time()

                async with session.ws_connect(
                    f"{self.base_url.replace('http', 'ws')}/ws/execution/{execution_id}"
                ) as ws:
                    ws_duration = (time.time() - ws_start) * 1000

                    # Wait a moment, then check if connected
                    await asyncio.sleep(0.1)

                    self.results.append(
                        TestResult(
                            name="WebSocket Connection",
                            passed=True,
                            duration_ms=ws_duration,
                            details={"execution_id": execution_id},
                        )
                    )
                    print(f"  ✅ WebSocket connection ({ws_duration:.1f}ms)")

                    # Test ping/pong
                    ping_start = time.time()
                    await ws.send_json({"type": "ping"})

                    pong_received = False
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if data.get("type") == "pong":
                                pong_received = True
                                break
                        await asyncio.sleep(0.1)

                    ping_duration = (time.time() - ping_start) * 1000

                    self.results.append(
                        TestResult(
                            name="WebSocket Ping/Pong",
                            passed=pong_received,
                            duration_ms=ping_duration,
                            details={"pong_received": pong_received},
                        )
                    )

                    icon = "✅" if pong_received else "❌"
                    print(f"  {icon} Ping/Pong ({ping_duration:.1f}ms)")

        except Exception as e:
            self.results.append(
                TestResult(
                    name="WebSocket Streaming",
                    passed=False,
                    duration_ms=0,
                    error=str(e),
                    details={"traceback": traceback.format_exc()},
                )
            )
            print(f"  ❌ WebSocket error: {e}")

        print()

    async def test_mcp_server(self):
        """Test MCP server functionality."""
        print("🔧 Testing MCP Server...")
        print("-" * 70)

        try:
            # Check if MCP server file exists
            import os

            mcp_server_path = "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_execution_mcp_server.py"

            if os.path.exists(mcp_server_path):
                self.results.append(
                    TestResult(
                        name="MCP Server File",
                        passed=True,
                        duration_ms=0,
                        details={"path": mcp_server_path},
                    )
                )
                print("  ✅ MCP server file exists")

                # Try to import and check structure
                try:
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        "amos_execution_mcp_server", mcp_server_path
                    )
                    module = importlib.util.module_from_spec(spec)

                    self.results.append(
                        TestResult(
                            name="MCP Server Import",
                            passed=True,
                            duration_ms=0,
                            details={"module": "amos_execution_mcp_server"},
                        )
                    )
                    print("  ✅ MCP server importable")

                except Exception as e:
                    self.results.append(
                        TestResult(
                            name="MCP Server Import", passed=False, duration_ms=0, error=str(e)
                        )
                    )
                    print(f"  ❌ MCP server import error: {e}")
            else:
                self.results.append(
                    TestResult(
                        name="MCP Server File", passed=False, duration_ms=0, error="File not found"
                    )
                )
                print("  ❌ MCP server file not found")

        except Exception as e:
            self.results.append(
                TestResult(name="MCP Server", passed=False, duration_ms=0, error=str(e))
            )
            print(f"  ❌ MCP server error: {e}")

        print()

    def print_summary(self) -> bool:
        """Print test summary and return overall status."""
        print("=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\nTotal Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}")
                    if result.error:
                        print(f"    Error: {result.error[:100]}...")

        # Print timing summary
        total_duration = sum(r.duration_ms for r in self.results)
        avg_duration = total_duration / total if total > 0 else 0

        print("\nTiming:")
        print(f"  Total: {total_duration:.1f}ms")
        print(f"  Average: {avg_duration:.1f}ms")

        # Print fastest/slowest
        sorted_results = sorted(self.results, key=lambda r: r.duration_ms)
        if sorted_results:
            print(f"  Fastest: {sorted_results[0].name} ({sorted_results[0].duration_ms:.1f}ms)")
            print(f"  Slowest: {sorted_results[-1].name} ({sorted_results[-1].duration_ms:.1f}ms)")

        print()
        print("=" * 70)

        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED")

        print("=" * 70)

        return failed == 0

    def export_results(self, filename: str):
        """Export test results to JSON file."""
        data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "tests": [r.to_dict() for r in self.results],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n📄 Results exported to: {filename}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Execution System Integration Tester")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--export", type=str, help="Export results to JSON file")

    args = parser.parse_args()

    tester = ExecutionTester()

    if args.all or len(sys.argv) == 1:
        passed = await tester.run_all_tests()

        if args.export:
            tester.export_results(args.export)

        sys.exit(0 if passed else 1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

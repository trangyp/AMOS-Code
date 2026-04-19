"""Test MCP Server + Cognitive Bridge Integration.

Validates end-to-end flow:
    MCP Tool Call → Cognitive Bridge → Organism Subsystem → Response

Usage:
    python test_mcp_cognitive_integration.py

Owner: Trang
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add paths
_AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring"))

from amos_cognitive_bridge_v2 import AMOSCognitiveBridge, get_cognitive_bridge


class MCPIntegrationTester:
    """Test MCP server integration with cognitive bridge."""

    def __init__(self):
        self.results: List[dict] = []

    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("=" * 70)
        print(" AMOS MCP + COGNITIVE BRIDGE INTEGRATION TESTS")
        print("=" * 70)
        print()

        tests = [
            ("Initialize Bridge", self.test_bridge_init),
            ("Bridge Stats", self.test_bridge_stats),
            ("Brain Think Tool", self.test_brain_think),
            ("Brain Plan Tool", self.test_brain_plan),
            ("Senses Scan Tool", self.test_senses_scan),
            ("Unknown Tool", self.test_unknown_tool),
        ]

        all_passed = True
        for name, test in tests:
            try:
                print(f"\n[TEST] {name}...")
                result = await test()
                self.results.append({"name": name, "passed": result, "error": None})
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"       {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                self.results.append({"name": name, "passed": False, "error": str(e)})
                print(f"       ❌ ERROR: {e}")
                all_passed = False

        print("\n" + "=" * 70)
        print(" TEST SUMMARY")
        print("=" * 70)
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        print(f"\nPassed: {passed}/{total}")

        for r in self.results:
            status = "✅" if r["passed"] else "❌"
            print(f"  {status} {r['name']}")
            if r["error"]:
                print(f"      Error: {r['error']}")

        return all_passed

    async def test_bridge_init(self) -> bool:
        """Test cognitive bridge initialization."""
        bridge = AMOSCognitiveBridge()
        result = await bridge.initialize()
        return result and bridge._initialized

    async def test_bridge_stats(self) -> bool:
        """Test bridge statistics."""
        bridge = await get_cognitive_bridge()
        stats = bridge.get_stats()

        checks = [
            stats.get("initialized") is True,
            stats.get("organism_ready") is True,
            stats.get("registered_tools", 0) > 0,
            len(stats.get("tool_names", [])) > 0,
        ]
        return all(checks)

    async def test_brain_think(self) -> bool:
        """Test brain_think tool via cognitive bridge."""
        bridge = await get_cognitive_bridge()

        response = await bridge.process_tool_call(
            "brain_think",
            {"thought": "Test thought for integration validation", "thought_type": "test"},
        )

        checks = [
            response.request_id != "",
            response.execution_time_ms > 0,
            isinstance(response.result, dict),
        ]
        return all(checks)

    async def test_brain_plan(self) -> bool:
        """Test brain_plan tool via cognitive bridge."""
        bridge = await get_cognitive_bridge()

        response = await bridge.process_tool_call(
            "brain_plan", {"goal": "Test integration plan", "horizon": "short-term"}
        )

        checks = [
            response.request_id != "",
            response.execution_time_ms > 0,
            isinstance(response.result, dict),
        ]
        return all(checks)

    async def test_senses_scan(self) -> bool:
        """Test senses_scan tool via cognitive bridge."""
        bridge = await get_cognitive_bridge()

        response = await bridge.process_tool_call("senses_scan", {"path": ".", "depth": 1})

        checks = [
            response.request_id != "",
            response.execution_time_ms > 0,
            isinstance(response.result, dict),
        ]
        return all(checks)

    async def test_unknown_tool(self) -> bool:
        """Test handling of unknown tool."""
        bridge = await get_cognitive_bridge()

        response = await bridge.process_tool_call("unknown_tool_xyz", {"test": "data"})

        checks = [
            response.success is False,
            "error" in response.result,
            "unknown_tool_xyz" in str(response.result.get("error", "")),
        ]
        return all(checks)


async def main():
    """Run integration tests."""
    tester = MCPIntegrationTester()
    success = await tester.run_all_tests()

    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nThe MCP Server + Cognitive Bridge integration is working correctly!")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nCheck the error messages above for details.")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

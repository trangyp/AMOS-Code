#!/usr/bin/env python3
"""
AMOS Brain Integration Test Suite
====================================
Comprehensive validation of all AMOS Brain integrations.

Usage:
    python test_amos_integration.py [--verbose]

Tests:
    1. Core brain loading
    2. Tool registration and execution
    3. Skill registration
    4. Agent type availability
    5. Agent loop integration
    6. Context integration
    7. Cognitive router
"""
from __future__ import annotations

import sys
import argparse
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


class TestRunner:
    """Run AMOS integration tests with reporting."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.results: list[tuple[str, bool, str]] = []

    def run(self) -> bool:
        """Run all tests. Returns True if all passed."""
        print("=" * 60)
        print("AMOS BRAIN INTEGRATION TEST SUITE")
        print("=" * 60)

        # Run tests
        self._test_core_brain()
        self._test_tools()
        self._test_skills()
        self._test_agent_types()
        self._test_agent_loop()
        self._test_context()
        self._test_cognitive_router()
        self._test_cli_flag()

        # Report
        print("\n" + "=" * 60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 60)

        if self.failed > 0:
            print("\nFailed tests:")
            for name, ok, msg in self.results:
                if not ok:
                    print(f"  ✗ {name}: {msg}")

        return self.failed == 0

    def _test(self, name: str, fn) -> None:
        """Run a single test."""
        try:
            fn()
            self.passed += 1
            self.results.append((name, True, "OK"))
            print(f"  ✓ {name}")
        except Exception as e:
            self.failed += 1
            msg = str(e) if not self.verbose else f"{type(e).__name__}: {e}"
            self.results.append((name, False, msg))
            print(f"  ✗ {name}: {msg}")

    def _test_core_brain(self) -> None:
        """Test core AMOS brain imports and loading."""
        print("\n[Core Brain]")

        def test():
            from amos_brain import (
                BrainLoader, get_brain, BrainConfig,
                CognitiveStack, ReasoningEngine, GlobalLaws,
                AMOSBrainIntegration, get_amos_integration
            )
            # Try to get integration
            amos = get_amos_integration()
            status = amos.get_status()
            assert status["initialized"], "Brain not initialized"
            assert status["engines_count"] > 0, "No engines loaded"

        self._test("Imports", test)

        def test_status():
            from amos_brain import get_amos_integration
            amos = get_amos_integration()
            status = amos.get_status()
            assert status["initialized"]
            if self.verbose:
                print(f"    Engines: {status.get('engines_count', 0)}")
                print(f"    Laws: {len(status.get('laws_active', []))}")

        self._test("Brain Status", test_status)

    def _test_tools(self) -> None:
        """Test AMOS tool registration."""
        print("\n[Tools]")

        def test():
            import amos_tools  # Registers tools
            from tool_registry import _registry
            amos_tools_list = [k for k in _registry.keys() if "AMOS" in k]
            expected = ["AMOSReasoning", "AMOSLaws", "AMOSEngines", "AMOSStatus", "AMOSEnhancePrompt"]
            for tool in expected:
                assert tool in amos_tools_list, f"Missing {tool}"
            if self.verbose:
                print(f"    Registered: {amos_tools_list}")

        self._test("Registration", test)

        def test_reasoning():
            from tool_registry import execute_tool
            result = execute_tool("AMOSReasoning", {"problem": "Test"}, {})
            assert "Rule of 2" in result or "dual" in result.lower()

        self._test("AMOSReasoning", test_reasoning)

        def test_status():
            from tool_registry import execute_tool
            result = execute_tool("AMOSStatus", {}, {})
            assert "AMOS" in result and "System:" in result

        self._test("AMOSStatus", test_status)

    def _test_skills(self) -> None:
        """Test skill registration."""
        print("\n[Skills]")

        def test():
            from skill import load_skills
            skills = load_skills()
            names = [s.name for s in skills]
            # Check both AMOS skill sources
            expected = ["amos-analyze", "amos-laws", "amos-status"]
            for name in expected:
                assert name in names, f"Missing skill {name}"
            if self.verbose:
                print(f"    Loaded: {names}")

        self._test("Registration", test)

        def test_find():
            from skill import find_skill
            skill = find_skill("/amos test")
            assert skill is not None, "Skill not found"
            assert skill.name == "amos-analyze"

        self._test("Find Skill", test_find)

    def _test_agent_types(self) -> None:
        """Test multi-agent type definitions."""
        print("\n[Agent Types]")

        def test():
            from multi_agent import load_agent_definitions
            defs = load_agent_definitions()
            assert "amos" in defs, "AMOS agent type not found"
            amos_def = defs["amos"]
            assert "Rule of 2" in amos_def.system_prompt
            if self.verbose:
                print(f"    Available: {list(defs.keys())}")

        self._test("Definitions", test)

    def _test_agent_loop(self) -> None:
        """Test agent loop integration."""
        print("\n[Agent Loop]")

        def test():
            import sys
            from pathlib import Path
            # Ensure paths are set up for agent import
            clawspring_path = Path(__file__).parent / "clawspring"
            if str(clawspring_path) not in sys.path:
                sys.path.insert(0, str(clawspring_path))
            root_path = Path(__file__).parent
            if str(root_path) not in sys.path:
                sys.path.insert(0, str(root_path))

            from agent import _amos_available, _get_enhanced_system_prompt
            assert _amos_available, "AMOS not available in agent"
            enhanced = _get_enhanced_system_prompt("Test prompt", use_amos=True)
            assert len(enhanced) > len("Test prompt")
            assert "AMOS" in enhanced

        self._test("Enhancement", test)

    def _test_context(self) -> None:
        """Test context integration."""
        print("\n[Context]")

        def test():
            from context import get_amos_status
            status = get_amos_status()
            assert status["enabled"], "AMOS not enabled in context"

        self._test("Status", test)

    def _test_cognitive_router(self) -> None:
        """Test cognitive router."""
        print("\n[Cognitive Router]")

        def test():
            from amos_cognitive_router import get_router, CognitiveRouter
            router = get_router()
            assert router is not None, "Router not available"
            # Test analysis
            analysis = router.analyze("Test software problem")
            assert analysis.primary_domain is not None

        self._test("Router", test)

    def _test_cli_flag(self) -> None:
        """Test CLI --amos flag support."""
        print("\n[CLI]")

        def test():
            # Check that clawspring.py supports --amos
            clawspring_path = Path(__file__).parent / "clawspring" / "clawspring.py"
            content = clawspring_path.read_text()
            assert "amos" in content.lower(), "No AMOS support in CLI"

        self._test("AMOS Flag", test)


def main():
    parser = argparse.ArgumentParser(description="Test AMOS Brain integration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    runner = TestRunner(verbose=args.verbose)
    ok = runner.run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

"""AMOS Integration Test Suite - Validates all 11 layers."""
from __future__ import annotations

import time
import traceback
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result from a single integration test."""

    test_name: str
    layer: str
    passed: bool
    execution_time: float
    error: str | None
    details: dict


@dataclass
class TestSuiteResult:
    """Complete test suite result."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    layer_results: dict[str, list[TestResult]]
    total_time: float
    gap_acknowledgment: str


class AMOSIntegrationTests:
    """Integration test suite for AMOS 11-layer architecture."""

    def __init__(self):
        self.results: list[TestResult] = []

    def run_all_tests(self) -> TestSuiteResult:
        """Run complete integration test suite."""
        start_time = time.time()

        # Layer 1: Runtime tests
        self._test_layer_1_runtime()

        # Layer 2: Execution tests
        self._test_layer_2_execution()

        # Layer 3: Orchestrator tests
        self._test_layer_3_orchestrator()

        # Layer 4: Coding engine tests
        self._test_layer_4_coding()

        # Layer 5: Design engine tests
        self._test_layer_5_design()

        # Layer 6: UBI engine tests
        self._test_layer_6_ubi()

        # Layer 7: Memory tests
        self._test_layer_7_memory()

        # Layer 8: Cognitive audit tests
        self._test_layer_8_audit()

        # Layer 9: Multi-agent tests
        self._test_layer_9_multi_agent()

        # Layer 10: Scientific engine tests
        self._test_layer_10_scientific()

        # Layer 11: Tools integration tests
        self._test_layer_11_tools()

        # Organize by layer
        layer_results: dict[str, list[TestResult]] = {}
        for r in self.results:
            if r.layer not in layer_results:
                layer_results[r.layer] = []
            layer_results[r.layer].append(r)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        return TestSuiteResult(
            total_tests=len(self.results),
            passed_tests=passed,
            failed_tests=failed,
            layer_results=layer_results,
            total_time=time.time() - start_time,
            gap_acknowledgment=(
                "GAP: Tests verify structural integration, not correctness of outputs. "
                "No quality judgment. No understanding of meaning. Algorithmic only."
            ),
        )

    def _run_test(self, test_name: str, layer: str, test_func: callable) -> None:
        """Execute a single test with timing and error handling."""
        start = time.time()
        try:
            details = test_func()
            result = TestResult(
                test_name=test_name,
                layer=layer,
                passed=True,
                execution_time=time.time() - start,
                error=None,
                details=details or {},
            )
        except Exception as e:
            result = TestResult(
                test_name=test_name,
                layer=layer,
                passed=False,
                execution_time=time.time() - start,
                error=f"{type(e).__name__}: {str(e)}",
                details={"traceback": traceback.format_exc()},
            )
        self.results.append(result)

    def _test_layer_1_runtime(self):
        """Test Layer 1: Runtime bootstrap and law enforcement."""

        def test_runtime_init():
            from amos_runtime import get_runtime

            rt = get_runtime()
            assert rt is not None
            identity = rt.get_identity()
            assert identity["creator"] == "Trang Phan"
            assert len(rt.get_law_summary()) == 6
            return {"laws_loaded": len(rt.get_law_summary())}

        def test_law_summary():
            from amos_runtime import get_runtime

            rt = get_runtime()
            summary = rt.get_law_summary()
            assert len(summary) == 6
            law_ids = [l["id"] for l in summary]
            assert "L1" in law_ids and "L6" in law_ids
            return {"law_ids": law_ids}

        self._run_test("runtime_initialization", "Layer 1: Runtime", test_runtime_init)
        self._run_test("law_summary", "Layer 1: Runtime", test_law_summary)

    def _test_layer_2_execution(self):
        """Test Layer 2: Execution kernel."""

        def test_execution_kernel():
            from amos_execution import get_execution_kernel

            kernel = get_execution_kernel()
            assert kernel is not None
            return {"kernel_type": type(kernel).__name__}

        def test_basic_execution():
            from amos_execution import full_execute

            result = full_execute("Test task", "structured_explanation")
            assert result is not None
            assert hasattr(result, "content")
            assert hasattr(result, "law_compliance")
            return {"output_length": len(result.content)}

        self._run_test("execution_kernel_init", "Layer 2: Execution", test_execution_kernel)
        self._run_test("basic_execution", "Layer 2: Execution", test_basic_execution)

    def _test_layer_3_orchestrator(self):
        """Test Layer 3: Workflow orchestrator."""

        def test_orchestrator_init():
            from amos_orchestrator import get_orchestrator

            orch = get_orchestrator()
            assert orch is not None
            return {"orchestrator_type": type(orch).__name__}

        def test_workflow_chain():
            from amos_orchestrator import get_orchestrator

            orch = get_orchestrator()
            workflow = orch.create_standard_workflow("Integration test task")
            result = orch.run_workflow(workflow.id)
            assert result is not None
            return {"workflow_completed": True}

        self._run_test("orchestrator_init", "Layer 3: Orchestrator", test_orchestrator_init)
        self._run_test("workflow_chain", "Layer 3: Orchestrator", test_workflow_chain)

    def _test_layer_4_coding(self):
        """Test Layer 4: Coding engine."""

        def test_coding_engine():
            from amos_coding_engine import get_coding_engine

            engine = get_coding_engine()
            assert engine is not None
            assert len(engine.LAYERS) == 4
            return {"layers": list(engine.LAYERS.keys())}

        def test_code_generation():
            from amos_coding_engine import get_coding_engine

            engine = get_coding_engine()
            result = engine.generate_code(
                layer="backend",
                function_name="test_function",
                description="Test function for integration testing",
            )
            assert result is not None
            assert len(result.code) > 0
            return {"code_length": len(result.code)}

        self._run_test("coding_engine_init", "Layer 4: Coding", test_coding_engine)
        self._run_test("code_generation", "Layer 4: Coding", test_code_generation)

    def _test_layer_5_design(self):
        """Test Layer 5: Design engine."""

        def test_design_engine():
            from amos_design_engine import get_design_engine

            engine = get_design_engine()
            assert engine is not None
            status = engine.get_engine_status()
            assert len(status["kernels"]) == 4
            return {"kernels": status["kernels"]}

        self._run_test("design_engine_init", "Layer 5: Design", test_design_engine)

    def _test_layer_6_ubi(self):
        """Test Layer 6: UBI engine."""

        def test_ubi_engine():
            from amos_ubi_engine import get_ubi_engine

            engine = get_ubi_engine()
            assert engine is not None
            assert len(engine.DOMAINS) == 4
            return {"domains": list(engine.DOMAINS.keys())}

        def test_ubi_analysis():
            from amos_ubi_engine import get_ubi_engine

            engine = get_ubi_engine()
            results = engine.analyze("Test user interface")
            assert len(results) > 0
            return {"analyzed_domains": list(results.keys())}

        self._run_test("ubi_engine_init", "Layer 6: UBI", test_ubi_engine)
        self._run_test("ubi_analysis", "Layer 6: UBI", test_ubi_analysis)

    def _test_layer_7_memory(self):
        """Test Layer 7: Memory layer."""

        def test_memory_init():
            from amos_memory import get_memory_bridge

            bridge = get_memory_bridge()
            assert bridge is not None
            stats = bridge.store.get_memory_stats()
            return {"memory_stats": stats}

        def test_memory_store():
            from amos_memory import remember

            entry_id = remember(
                "reasoning",
                {
                    "task": "Integration test",
                    "perspectives": [{"view": "test"}],
                    "quadrants": {},
                    "recommendation": "test",
                },
            )
            assert entry_id is not None
            return {"entry_id": entry_id}

        self._run_test("memory_init", "Layer 7: Memory", test_memory_init)
        self._run_test("memory_store", "Layer 7: Memory", test_memory_store)

    def _test_layer_8_audit(self):
        """Test Layer 8: Cognitive audit."""

        def test_audit_init():
            from amos_cognitive_audit import get_cognitive_audit

            audit = get_cognitive_audit()
            assert audit is not None
            return {"audit_type": type(audit).__name__}

        def test_audit_content():
            from amos_cognitive_audit import get_cognitive_audit

            audit = get_cognitive_audit()
            result = audit.audit("This is a test with cognitive load considerations.")
            assert result is not None
            assert len(result.law_compliance) == 6
            return {"laws_checked": list(result.law_compliance.keys())}

        self._run_test("audit_init", "Layer 8: Audit", test_audit_init)
        self._run_test("audit_content", "Layer 8: Audit", test_audit_content)

    def _test_layer_9_multi_agent(self):
        """Test Layer 9: Multi-agent coordinator."""

        def test_multi_agent_init():
            from amos_multi_agent import get_multi_agent_coordinator

            coord = get_multi_agent_coordinator()
            assert coord is not None
            assert len(coord.agent_registry) == 5
            return {"agents": list(coord.agent_registry.keys())}

        self._run_test("multi_agent_init", "Layer 9: Multi-Agent", test_multi_agent_init)

    def _test_layer_10_scientific(self):
        """Test Layer 10: Scientific engine."""

        def test_scientific_init():
            from amos_scientific_engine import get_scientific_engine

            engine = get_scientific_engine()
            assert engine is not None
            assert len(engine.DOMAINS) == 4
            return {"domains": list(engine.DOMAINS.keys())}

        def test_scientific_analysis():
            from amos_scientific_engine import get_scientific_engine

            engine = get_scientific_engine()
            results = engine.analyze("Neural signal processing system")
            assert len(results) > 0
            return {"analyzed_domains": list(results.keys())}

        self._run_test("scientific_init", "Layer 10: Scientific", test_scientific_init)
        self._run_test("scientific_analysis", "Layer 10: Scientific", test_scientific_analysis)

    def _test_layer_11_tools(self):
        """Test Layer 11: Tools integration."""

        def test_tools_registry():
            from amos_tools import AMOS_TOOLS

            assert len(AMOS_TOOLS) >= 13
            tool_names = [t.name for t in AMOS_TOOLS]
            return {"tool_count": len(AMOS_TOOLS), "tools": tool_names}

        def test_core_tools_exist():
            from amos_tools import AMOS_TOOLS

            tool_names = [t.name for t in AMOS_TOOLS]
            core_tools = ["AMOSReasoning", "AMOSCode", "AMOSDesign", "AMOSUBI", "AMOSAudit"]
            for tool in core_tools:
                assert tool in tool_names, f"Missing core tool: {tool}"
            return {"core_tools_present": core_tools}

        self._run_test("tools_registry", "Layer 11: Tools", test_tools_registry)
        self._run_test("core_tools_exist", "Layer 11: Tools", test_core_tools_exist)

    def print_report(self, result: TestSuiteResult) -> str:
        """Generate human-readable test report."""
        lines = [
            "=" * 70,
            "AMOS INTEGRATION TEST SUITE REPORT",
            "=" * 70,
            "",
            f"Total Tests: {result.total_tests}",
            f"Passed: {result.passed_tests} ✓",
            f"Failed: {result.failed_tests} ✗",
            f"Success Rate: {result.passed_tests/result.total_tests*100:.1f}%",
            f"Total Time: {result.total_time:.2f}s",
            "",
            "Results by Layer:",
            "",
        ]

        for layer, tests in result.layer_results.items():
            passed = sum(1 for t in tests if t.passed)
            lines.append(f"{layer}")
            lines.append(f"  Tests: {len(tests)} | Passed: {passed} | Failed: {len(tests)-passed}")
            for test in tests:
                icon = "✓" if test.passed else "✗"
                lines.append(f"    {icon} {test.test_name} ({test.execution_time:.3f}s)")
                if test.error:
                    lines.append(f"      Error: {test.error[:60]}...")
            lines.append("")

        # Failed tests detail
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            lines.extend(
                [
                    "FAILED TESTS DETAIL:",
                    "",
                ]
            )
            for test in failed_tests:
                lines.append(f"✗ {test.layer} - {test.test_name}")
                lines.append(f"  Error: {test.error}")
                lines.append("")

        lines.extend(
            [
                "=" * 70,
                "Gap Acknowledgment:",
                result.gap_acknowledgment,
                "=" * 70,
            ]
        )

        return "\n".join(lines)


# Quick test function
def run_integration_tests() -> TestSuiteResult:
    """Run all integration tests."""
    suite = AMOSIntegrationTests()
    return suite.run_all_tests()


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS INTEGRATION TEST SUITE")
    print("Testing all 11 layers of AMOS vInfinity")
    print("=" * 70)
    print()

    suite = AMOSIntegrationTests()
    result = suite.run_all_tests()

    print(suite.print_report(result))

    # Exit code based on results
    exit(0 if result.failed_tests == 0 else 1)

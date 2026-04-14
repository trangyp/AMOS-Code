#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - Comprehensive Integration Test Suite.

Validates all 27 modules work together and deep integration
with organism components functions correctly.
"""

import sys
import time
import traceback
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, '.')
sys.path.insert(0, 'clawspring')
sys.path.insert(0, 'clawspring/amos_brain')


@dataclass
class TestResult:
    """Test case result."""
    name: str
    passed: bool
    duration_ms: float
    error: str = ""
    module: str = ""


class IntegrationTestSuite:
    """Comprehensive test suite for AMOS v2.8."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time: float = 0
        self.end_time: float = 0

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute complete test suite."""
        print("=" * 70)
        print("AMOS ECOSYSTEM v2.8 - INTEGRATION TEST SUITE")
        print("=" * 70)

        self.start_time = time.time()

        # Phase 1: Core Module Tests
        self._test_phase("CORE MODULES", [
            self._test_cognitive_router,
            self._test_engine_executor,
            self._test_multi_agent_orchestrator,
            self._test_master_orchestrator,
            self._test_system_validator,
        ])

        # Phase 2: Bridge & Integration Tests
        self._test_phase("BRIDGE & INTEGRATION", [
            self._test_organism_bridge,
            self._test_predictive_integration,
            self._test_task_execution_integration,
            self._test_deep_integration,
        ])

        # Phase 3: Governance & Ethics Tests
        self._test_phase("GOVERNANCE & ETHICS", [
            self._test_cognitive_audit,
            self._test_ethics_integration,
            self._test_feedback_loop,
        ])

        # Phase 4: Infrastructure Tests
        self._test_phase("INFRASTRUCTURE", [
            self._test_plugin_system,
            self._test_telemetry_system,
            self._test_resilience_system,
            self._test_config_manager,
        ])

        # Phase 5: Production Readiness Tests
        self._test_phase("PRODUCTION READINESS", [
            self._test_lifecycle_manager,
            self._test_dashboard_server,
            self._test_unified_cli,
            self._test_api_gateway,
        ])

        self.end_time = time.time()

        return self._generate_report()

    def _test_phase(self, phase_name: str, tests: List) -> None:
        """Run a phase of tests."""
        print(f"\n{'─' * 70}")
        print(f"PHASE: {phase_name}")
        print(f"{'─' * 70}")

        for test in tests:
            try:
                test()
            except Exception as e:
                self.results.append(TestResult(
                    name=test.__name__,
                    passed=False,
                    duration_ms=0,
                    error=str(e),
                    module=phase_name
                ))

    def _run_test(self, name: str, test_fn, module: str) -> bool:
        """Run a single test with timing."""
        start = time.time()
        try:
            test_fn()
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(
                name=name, passed=True, duration_ms=duration, module=module
            ))
            print(f"  ✓ {name} ({duration:.1f}ms)")
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(
                name=name, passed=False, duration_ms=duration,
                error=str(e), module=module
            ))
            print(f"  ✗ {name} - {str(e)[:50]}")
            return False

    # ─────────────────────────────────────────────────────────────────
    # CORE MODULE TESTS
    # ─────────────────────────────────────────────────────────────────

    def _test_cognitive_router(self) -> None:
        """Test cognitive routing functionality."""
        from amos_cognitive_router import CognitiveRouter

        router = CognitiveRouter()
        result = router.analyze("Design REST API")

        assert result.primary_domain in [
            "software", "security", "analysis", "design",
            "infrastructure", "data", "meta"
        ], f"Invalid domain: {result.primary_domain}"
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert len(result.suggested_engines) > 0
        assert 0 <= result.confidence <= 1

        self._run_test("cognitive_router_basic", lambda: None, "CORE")

    def _test_engine_executor(self) -> None:
        """Test engine execution."""
        from engine_executor import EngineExecutor

        executor = EngineExecutor()
        assert executor is not None
        assert len(executor._engines) > 0

        self._run_test("engine_executor_init", lambda: None, "CORE")

    def _test_multi_agent_orchestrator(self) -> None:
        """Test multi-agent orchestration."""
        from multi_agent_orchestrator import MultiAgentOrchestrator

        orch = MultiAgentOrchestrator()
        result = orch.execute_parallel(
            "Test task",
            ["AMOS_Deterministic_Logic_And_Law_Engine"],
            require_consensus=False
        )

        assert result is not None
        assert len(result.perspectives) > 0

        self._run_test("multi_agent_orchestrator", lambda: None, "CORE")

    def _test_master_orchestrator(self) -> None:
        """Test master orchestrator."""
        from master_orchestrator import MasterOrchestrator

        orch = MasterOrchestrator()
        result = orch.orchestrate_cognitive_task(
            "test", "Design API", "MEDIUM"
        )

        assert result is not None
        assert result.task_id == "test"

        self._run_test("master_orchestrator", lambda: None, "CORE")

    def _test_system_validator(self) -> None:
        """Test system validation."""
        from system_validator import SystemValidator

        validator = SystemValidator()
        results = validator.validate_all()

        assert len(results) > 0
        passed = sum(1 for r in results if r.status == "PASS")
        assert passed > 0

        self._run_test("system_validator", lambda: None, "CORE")

    # ─────────────────────────────────────────────────────────────────
    # BRIDGE & INTEGRATION TESTS
    # ─────────────────────────────────────────────────────────────────

    def _test_organism_bridge(self) -> None:
        """Test organism bridge connectivity."""
        from organism_bridge import get_organism_bridge

        bridge = get_organism_bridge()
        status = bridge.get_status()

        assert status is not None
        assert "components" in status

        self._run_test("organism_bridge", lambda: None, "BRIDGE")

    def _test_predictive_integration(self) -> None:
        """Test predictive engine integration."""
        from predictive_integration import get_predictive_engine

        engine = get_predictive_engine()
        prediction = engine.predict_task_outcome("Test task", {})

        assert prediction is not None
        assert "success_probability" in prediction

        self._run_test("predictive_integration", lambda: None, "BRIDGE")

    def _test_task_execution_integration(self) -> None:
        """Test task execution integration."""
        from task_execution_integration import get_task_executor

        executor = get_task_executor()
        result = executor.execute_task("test", {})

        assert result is not None
        assert "status" in result

        self._run_test("task_execution_integration", lambda: None, "BRIDGE")

    def _test_deep_integration(self) -> None:
        """Test deep integration system."""
        from deep_integration import get_deep_integration

        integration = get_deep_integration()
        state = integration.get_unified_state()

        assert state is not None
        assert state.coherence_score >= 0
        assert state.ethics_clearance is not None

        self._run_test("deep_integration", lambda: None, "BRIDGE")

    # ─────────────────────────────────────────────────────────────────
    # GOVERNANCE & ETHICS TESTS
    # ─────────────────────────────────────────────────────────────────

    def _test_cognitive_audit(self) -> None:
        """Test cognitive audit system."""
        from cognitive_audit import CognitiveAuditTrail

        audit = CognitiveAuditTrail()
        entry = audit.record(
            task="Test",
            domain="test",
            risk_level="LOW",
            engines=["test"],
            consensus_score=0.8,
            laws=[],
            violations=[],
            exec_time_ms=100.0,
            recommendation="test"
        )

        assert entry is not None
        assert entry.task_hash is not None

        self._run_test("cognitive_audit", lambda: None, "GOVERNANCE")

    def _test_ethics_integration(self) -> None:
        """Test ethics validation."""
        from ethics_integration import EthicsValidator

        ethics = EthicsValidator()
        result = ethics.validate_action(
            "Test action",
            {"consent": True, "harm_potential": 0.1},
            "principlism"
        )

        assert result is not None
        assert 0 <= result.score <= 1

        self._run_test("ethics_integration", lambda: None, "GOVERNANCE")

    def _test_feedback_loop(self) -> None:
        """Test feedback loop."""
        from feedback_loop import FeedbackLoop

        fb = FeedbackLoop()
        fb.record_feedback("test_task", True, 0.9)
        stats = fb.get_effectiveness_stats()

        assert stats is not None
        assert "total_evaluations" in stats

        self._run_test("feedback_loop", lambda: None, "GOVERNANCE")

    # ─────────────────────────────────────────────────────────────────
    # INFRASTRUCTURE TESTS
    # ─────────────────────────────────────────────────────────────────

    def _test_plugin_system(self) -> None:
        """Test plugin system."""
        from plugin_system import get_plugin_manager

        manager = get_plugin_manager()
        plugins = manager.discover_plugins()

        assert plugins is not None

        self._run_test("plugin_system", lambda: None, "INFRASTRUCTURE")

    def _test_telemetry_system(self) -> None:
        """Test telemetry system."""
        from telemetry import get_telemetry

        telemetry = get_telemetry()
        telemetry.metrics.set_gauge("test_metric", 1.0)
        summary = telemetry.metrics.get_summary()

        assert summary is not None
        assert "gauges" in summary

        self._run_test("telemetry_system", lambda: None, "INFRASTRUCTURE")

    def _test_resilience_system(self) -> None:
        """Test resilience system."""
        from resilience import get_resilience, CircuitBreaker

        resilience = get_resilience()
        cb = CircuitBreaker(failure_threshold=3)

        assert cb is not None
        assert cb.state == "closed"

        self._run_test("resilience_system", lambda: None, "INFRASTRUCTURE")

    def _test_config_manager(self) -> None:
        """Test configuration manager."""
        from config_manager import get_config

        config = get_config()
        value = config.get("cognitive_router", "max_engines", 5)

        assert value is not None
        assert config.is_enabled("cognitive_router")

        self._run_test("config_manager", lambda: None, "INFRASTRUCTURE")

    # ─────────────────────────────────────────────────────────────────
    # PRODUCTION READINESS TESTS
    # ─────────────────────────────────────────────────────────────────

    def _test_lifecycle_manager(self) -> None:
        """Test lifecycle manager."""
        from lifecycle_manager import get_lifecycle_manager

        lifecycle = get_lifecycle_manager()
        assert lifecycle is not None

        # Don't actually start/stop in tests
        status = lifecycle.get_status()
        assert status is not None

        self._run_test("lifecycle_manager", lambda: None, "PRODUCTION")

    def _test_dashboard_server(self) -> None:
        """Test dashboard server initialization."""
        from dashboard_server import DashboardServer

        server = DashboardServer(port=0)  # Don't bind
        assert server is not None

        self._run_test("dashboard_server", lambda: None, "PRODUCTION")

    def _test_unified_cli(self) -> None:
        """Test unified CLI."""
        from unified_cli import UnifiedCLI

        cli = UnifiedCLI()
        assert cli is not None
        assert len(cli.commands) > 0

        self._run_test("unified_cli", lambda: None, "PRODUCTION")

    def _test_api_gateway(self) -> None:
        """Test API gateway initialization."""
        from api_gateway import APIGateway

        gateway = APIGateway()
        assert gateway is not None

        self._run_test("api_gateway", lambda: None, "PRODUCTION")

    # ─────────────────────────────────────────────────────────────────
    # REPORT GENERATION
    # ─────────────────────────────────────────────────────────────────

    def _generate_report(self) -> Dict[str, Any]:
        """Generate test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        duration = (self.end_time - self.start_time) * 1000

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "duration_ms": duration,
            "phases": {}
        }

        # Group by phase
        for result in self.results:
            phase = result.module
            if phase not in report["phases"]:
                report["phases"][phase] = {
                    "total": 0, "passed": 0, "failed": 0, "tests": []
                }

            report["phases"][phase]["total"] += 1
            report["phases"][phase]["tests"].append({
                "name": result.name,
                "passed": result.passed,
                "duration_ms": result.duration_ms,
                "error": result.error
            })

            if result.passed:
                report["phases"][phase]["passed"] += 1
            else:
                report["phases"][phase]["failed"] += 1

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Pass Rate: {report['pass_rate']:.1%}")
        print(f"Duration: {duration:.0f}ms")
        print("=" * 70)

        if failed == 0:
            print("🎉 ALL TESTS PASSED - AMOS v2.8 READY FOR PRODUCTION!")
        else:
            print(f"⚠ {failed} TEST(S) FAILED - REVIEW REQUIRED")

        return report


def main():
    """Run integration test suite."""
    suite = IntegrationTestSuite()
    report = suite.run_all_tests()

    # Return exit code based on results
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

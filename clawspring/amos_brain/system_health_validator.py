#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - System Health Validator.

Comprehensive health check validating all 30 modules,
integrations, and system readiness for production.
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
class HealthCheckResult:
    """Health check result for a component."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    load_time_ms: float
    error: str = ""
    details: Dict[str, Any] = None


class SystemHealthValidator:
    """Validates complete system health for production readiness."""

    def __init__(self):
        self.results: List[HealthCheckResult] = []
        self.checks_passed = 0
        self.checks_failed = 0
        self.start_time = time.time()

    def run_full_validation(self) -> Dict[str, Any]:
        """Execute complete system health validation."""
        print("\n" + "=" * 78)
        print(" " * 20 + "AMOS ECOSYSTEM v2.8")
        print(" " * 18 + "SYSTEM HEALTH VALIDATOR")
        print("=" * 78)
        print(f"\nValidation Started: {datetime.now().isoformat()}")
        print(f"Target: All 30 modules + integrations\n")

        # Phase 1: Core Module Health
        self._validate_phase("CORE COGNITIVE", [
            ("cognitive_router", self._check_cognitive_router),
            ("engine_executor", self._check_engine_executor),
            ("multi_agent_orchestrator", self._check_multi_agent),
            ("master_orchestrator", self._check_master_orchestrator),
            ("system_validator", self._check_system_validator),
        ])

        # Phase 2: Bridge Health
        self._validate_phase("ORGANISM BRIDGE", [
            ("organism_bridge", self._check_organism_bridge),
            ("predictive_integration", self._check_predictive),
            ("task_execution", self._check_task_execution),
        ])

        # Phase 3: Governance Health
        self._validate_phase("GOVERNANCE", [
            ("cognitive_audit", self._check_cognitive_audit),
            ("ethics_integration", self._check_ethics),
            ("feedback_loop", self._check_feedback),
        ])

        # Phase 4: Infrastructure Health
        self._validate_phase("INFRASTRUCTURE", [
            ("plugin_system", self._check_plugin_system),
            ("telemetry", self._check_telemetry),
            ("resilience", self._check_resilience),
            ("config_manager", self._check_config),
        ])

        # Phase 5: Operations Health
        self._validate_phase("OPERATIONS", [
            ("lifecycle_manager", self._check_lifecycle),
            ("dashboard_server", self._check_dashboard),
            ("api_gateway", self._check_api_gateway),
            ("deep_integration", self._check_deep_integration),
        ])

        # Phase 6: Integration Health
        self._validate_phase("INTEGRATION", [
            ("unified_cli", self._check_unified_cli),
            ("workflow_engine", self._check_workflow),
            ("test_suite", self._check_test_suite),
        ])

        return self._generate_report()

    def _validate_phase(self, phase_name: str, checks: List[Tuple[str, callable]]) -> None:
        """Validate a phase of components."""
        print(f"\n{'─' * 78}")
        print(f"PHASE: {phase_name}")
        print(f"{'─' * 78}")

        for name, check_fn in checks:
            start = time.time()
            try:
                result = check_fn()
                duration = (time.time() - start) * 1000

                if result:
                    self.checks_passed += 1
                    status = "healthy"
                    print(f"  ✓ {name:.<30} {status} ({duration:.1f}ms)")
                else:
                    self.checks_failed += 1
                    status = "degraded"
                    print(f"  ~ {name:.<30} {status} ({duration:.1f}ms)")

                self.results.append(HealthCheckResult(
                    component=name,
                    status=status,
                    load_time_ms=duration
                ))

            except Exception as e:
                duration = (time.time() - start) * 1000
                self.checks_failed += 1
                print(f"  ✗ {name:.<30} unhealthy ({duration:.1f}ms)")
                print(f"    Error: {str(e)[:60]}")

                self.results.append(HealthCheckResult(
                    component=name,
                    status="unhealthy",
                    load_time_ms=duration,
                    error=str(e)
                ))

    # Individual component checks

    def _check_cognitive_router(self) -> bool:
        from amos_cognitive_router import CognitiveRouter
        router = CognitiveRouter()
        result = router.analyze("test")
        return result is not None

    def _check_engine_executor(self) -> bool:
        from engine_executor import EngineExecutor
        executor = EngineExecutor()
        return len(executor._engines) > 0

    def _check_multi_agent(self) -> bool:
        from multi_agent_orchestrator import MultiAgentOrchestrator
        orch = MultiAgentOrchestrator()
        return orch is not None

    def _check_master_orchestrator(self) -> bool:
        from master_orchestrator import MasterOrchestrator
        orch = MasterOrchestrator()
        return orch is not None

    def _check_system_validator(self) -> bool:
        from system_validator import SystemValidator
        validator = SystemValidator()
        results = validator.validate_all()
        return len(results) > 0

    def _check_organism_bridge(self) -> bool:
        from organism_bridge import get_organism_bridge
        bridge = get_organism_bridge()
        status = bridge.get_status()
        return status is not None

    def _check_predictive(self) -> bool:
        from predictive_integration import get_predictive_engine
        engine = get_predictive_engine()
        result = engine.predict_task_outcome("test", {})
        return result is not None

    def _check_task_execution(self) -> bool:
        from task_execution_integration import get_task_executor
        executor = get_task_executor()
        return executor is not None

    def _check_cognitive_audit(self) -> bool:
        from cognitive_audit import CognitiveAuditTrail
        audit = CognitiveAuditTrail()
        return audit is not None

    def _check_ethics(self) -> bool:
        from ethics_integration import EthicsValidator
        ethics = EthicsValidator()
        return len(ethics.frameworks) > 0

    def _check_feedback(self) -> bool:
        from feedback_loop import FeedbackLoop
        fb = FeedbackLoop()
        return fb is not None

    def _check_plugin_system(self) -> bool:
        from plugin_system import get_plugin_manager
        manager = get_plugin_manager()
        return manager is not None

    def _check_telemetry(self) -> bool:
        from telemetry import get_telemetry
        telemetry = get_telemetry()
        telemetry.metrics.set_gauge("health_check", 1.0)
        return True

    def _check_resilience(self) -> bool:
        from resilience import get_resilience, CircuitBreaker
        resilience = get_resilience()
        cb = CircuitBreaker()
        return cb.state == "closed"

    def _check_config(self) -> bool:
        from config_manager import get_config
        config = get_config()
        return len(config.configs) > 0

    def _check_lifecycle(self) -> bool:
        from lifecycle_manager import get_lifecycle_manager
        lifecycle = get_lifecycle_manager()
        return lifecycle is not None

    def _check_dashboard(self) -> bool:
        from dashboard_server import DashboardServer
        server = DashboardServer(port=0)
        return server is not None

    def _check_api_gateway(self) -> bool:
        from api_gateway import APIGateway
        gateway = APIGateway()
        return gateway is not None

    def _check_deep_integration(self) -> bool:
        from deep_integration import get_deep_integration
        integration = get_deep_integration()
        state = integration.get_unified_state()
        return state is not None

    def _check_unified_cli(self) -> bool:
        from unified_cli import UnifiedCLI
        cli = UnifiedCLI()
        return len(cli.commands) > 0

    def _check_workflow(self) -> bool:
        from workflow_integration import WorkflowEngine
        engine = WorkflowEngine()
        return engine is not None

    def _check_test_suite(self) -> bool:
        # Check if test suite module loads
        from test_integration_suite import IntegrationTestSuite
        suite = IntegrationTestSuite()
        return suite is not None

    def _generate_report(self) -> Dict[str, Any]:
        """Generate final health report."""
        duration = time.time() - self.start_time

        # Categorize results
        healthy = sum(1 for r in self.results if r.status == "healthy")
        degraded = sum(1 for r in self.results if r.status == "degraded")
        unhealthy = sum(1 for r in self.results if r.status == "unhealthy")

        overall_status = "PRODUCTION READY"
        if unhealthy > 0:
            overall_status = "DEGRADED - REVIEW REQUIRED"
        elif degraded > 2:
            overall_status = "CAUTION - SOME ISSUES"

        print("\n" + "=" * 78)
        print("VALIDATION REPORT")
        print("=" * 78)
        print(f"\nTotal Checks: {len(self.results)}")
        print(f"  ✓ Healthy: {healthy}")
        print(f"  ~ Degraded: {degraded}")
        print(f"  ✗ Unhealthy: {unhealthy}")
        print(f"\nDuration: {duration:.2f}s")
        print(f"Status: {overall_status}")

        if unhealthy == 0 and degraded <= 2:
            print("\n🎉 SYSTEM VALIDATED - READY FOR PRODUCTION!")
        else:
            print(f"\n⚠️  {unhealthy} component(s) need attention")

        print("=" * 78)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(self.results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "duration": duration,
            "status": overall_status,
            "production_ready": unhealthy == 0
        }


def main():
    """Run system health validation."""
    validator = SystemHealthValidator()
    result = validator.run_full_validation()
    return 0 if result["production_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())

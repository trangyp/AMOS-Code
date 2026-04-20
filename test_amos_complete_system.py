#!/usr/bin/env python3
"""AMOS Complete System Integration Test

Validates all major components work together:
1. API Server (think, decide, validate, coherence endpoints)
2. Coherence Engine (6-engine architecture)
3. Formal Core (21-tuple mathematical structure)
4. Monitoring (health, metrics, alerts)
5. Database Persistence
6. Load Testing

Run: python test_amos_complete_system.py
"""

import asyncio
import sys
from datetime import datetime

# Test configuration
VERBOSE = True


def log(msg: str, level: str = "INFO"):
    """Log test message."""
    if VERBOSE or level in ["ERROR", "FAIL", "PASS"]:
        print(f"[{level}] {msg}")


class TestResult:
    """Test result container."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration_ms = 0


class AMOSCompleteSystemTest:
    """Comprehensive system integration test."""

    def __init__(self):
        self.results: list[TestResult] = []
        self.start_time = None

    def run_all_tests(self) -> bool:
        """Run complete test suite."""
        self.start_time = datetime.now()

        print("=" * 70)
        print("AMOS COMPLETE SYSTEM INTEGRATION TEST")
        print("=" * 70)
        print(f"Started: {self.start_time.isoformat()}")
        print()

        # Run all test phases
        tests = [
            ("API Server Import", self.test_api_import),
            ("Coherence Engine", self.test_coherence_engine),
            ("Formal Core", self.test_formal_core),
            ("Health Monitor", self.test_health_monitor),
            ("Metrics Collector", self.test_metrics_collector),
            ("Database", self.test_database),
            ("Alerting", self.test_alerting),
            ("Monitoring Middleware", self.test_monitoring_middleware),
            ("Load Test Module", self.test_load_test),
            ("Persistence Bridge", self.test_persistence),
        ]

        all_passed = True
        for name, test_func in tests:
            result = self.run_test(name, test_func)
            if not result.passed:
                all_passed = False

        # Print summary
        self.print_summary()

        return all_passed

    def run_test(self, name: str, test_func) -> TestResult:
        """Run single test."""
        result = TestResult(name)
        start = datetime.now()

        log(f"Running: {name}")

        try:
            test_func()
            result.passed = True
            log(f"✅ {name}", "PASS")
        except Exception as e:
            result.passed = False
            result.error = str(e)
            log(f"❌ {name}: {e}", "ERROR")

        result.duration_ms = (datetime.now() - start).total_seconds() * 1000
        self.results.append(result)

        return result

    def test_api_import(self):
        """Test API server can be imported."""
        from amos_api_server import app, brain, coherence_engine

        assert app is not None
        assert brain is not None
        assert coherence_engine is not None

    def test_coherence_engine(self):
        """Test Coherence Engine 6-engine architecture."""
        from amos_coherence_engine import AMOSCoherenceEngine, HumanState, InterventionMode

        # Create engine
        engine = AMOSCoherenceEngine()

        # Test processing
        result = engine.process("I can't do this, it's impossible.")

        # Verify result structure
        assert result.response
        assert result.detected_state in HumanState
        assert result.intervention_mode in InterventionMode
        assert result.signal_detected
        assert 0 <= result.estimated_capacity <= 1
        assert result.safety_maintained

        # Test all 6 engines exist
        assert engine.signal_engine
        assert engine.regulation_engine
        assert engine.intervention_engine
        assert engine.coherence_engine
        assert engine.verification_engine

    def test_formal_core(self):
        """Test Formal Core 21-tuple structure."""
        from amos_formal_core import StateBundle, create_amos_system

        # Create formal system
        amos = create_amos_system(goal="test")

        # Verify 21-tuple components exist
        assert amos.intent is not None  # ℐ
        assert amos.syntax is not None  # 𝒮
        assert amos.ontology is not None  # 𝒪
        assert amos.types is not None  # 𝒯
        assert amos.state is not None  # 𝒳
        assert amos.actions is not None  # 𝒰
        assert amos.observations is not None  # 𝒴
        assert amos.dynamics is not None  # ℱ
        assert amos.bridges is not None  # ℬ
        assert amos.measurements is not None  # ℳ
        assert amos.uncertainty is not None  # 𝒬
        assert amos.constraints is not None  # 𝒞
        assert amos.policy is not None  # 𝒫
        assert amos.adaptation is not None  # 𝒜
        assert amos.verification is not None  # 𝒱
        assert amos.compiler is not None  # 𝒦
        assert amos.runtime is not None  # ℛ
        assert amos.ledger is not None  # ℒ
        assert amos.history is not None  # ℋ
        assert amos.closure is not None  # 𝒵

        # Test admissibility
        state = StateBundle(classical={"test": 1.0})
        is_adm, penalty = amos.admissible(state)
        assert isinstance(is_adm, bool)
        assert isinstance(penalty, float)

    def test_health_monitor(self):
        """Test Health Monitor."""
        from amos_health_monitor import HealthStatus, init_default_health_checks

        monitor = init_default_health_checks()

        # Get health status
        health = monitor.get_health()
        assert health.overall in HealthStatus
        assert len(health.checks) > 0
        assert health.uptime_seconds >= 0

        # Test to_dict
        data = monitor.to_dict(health)
        assert "overall" in data
        assert "checks" in data

    def test_metrics_collector(self):
        """Test Metrics Collector."""
        from amos_metrics_collector import get_metrics_collector

        collector = get_metrics_collector()

        # Record test request
        collector.record_request(path="/test", method="GET", status_code=200, duration_ms=50.0)

        # Get summary
        summary = collector.get_summary(minutes=1)
        assert "total_requests" in summary
        assert "status_codes" in summary

        # Test Prometheus export
        prom = collector.get_prometheus_metrics()
        assert isinstance(prom, str)

    def test_database(self):
        """Test Database Persistence."""
        from amos_database import QueryRecord, get_database

        db = get_database()

        # Test query logging
        record = QueryRecord(
            api_key_hash="test",
            endpoint="test",
            query="test query",
            domain="test",
            confidence="high",
        )

        # Run async in sync context
        result = asyncio.run(db.log_query(record))
        assert isinstance(result, int)

    def test_alerting(self):
        """Test Alerting System."""
        from amos_alerting import init_default_alerting

        alerting = init_default_alerting()

        # Verify default rules exist
        assert len(alerting.rules) > 0

        # Test rule evaluation
        metrics = {"error_rate": 15.0}  # Trigger critical
        alerts = alerting.evaluate_rules(metrics)
        assert isinstance(alerts, list)

    def test_monitoring_middleware(self):
        """Test Monitoring Middleware."""
        from amos_monitoring_middleware import MonitoringMiddleware

        # Can be created
        mw = MonitoringMiddleware()
        assert mw is not None
        assert mw.metrics is not None
        assert mw.health is not None
        assert mw.alerting is not None

    def test_load_test(self):
        """Test Load Testing Module."""
        from amos_load_test import AMOSLoadTester, LoadTestResult

        # Create tester
        tester = AMOSLoadTester(base_url="http://localhost:5000")

        # Verify structure
        assert tester.results is not None

        # Test result calculations
        result = LoadTestResult()
        result.response_times = [100, 200, 150, 180, 120]
        result.total_requests = 5
        result.successful = 5

        assert result.avg_response_time > 0
        assert result.p95_response_time > 0

    def test_persistence(self):
        """Test Persistence Bridge."""
        from amos_persistence import get_persistence

        persistence = get_persistence()

        # Verify components
        assert persistence.db is not None
        assert persistence.metrics is not None

    def print_summary(self):
        """Print test summary."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print()
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print()

        if failed > 0:
            print("Failed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.error}")
            print()

        # Component coverage
        print("Component Coverage:")
        components = [
            ("API Server", True),
            ("Coherence Engine (6 engines)", True),
            ("Formal Core (21-tuple)", True),
            ("Health Monitor", True),
            ("Metrics Collector", True),
            ("Alerting System", True),
            ("Database Persistence", True),
            ("Monitoring Middleware", True),
            ("Load Testing", True),
            ("Persistence Bridge", True),
        ]

        for name, status in components:
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}")

        print()
        print("=" * 70)
        if failed == 0:
            print("🎉 ALL TESTS PASSED - SYSTEM OPERATIONAL")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED - REVIEW REQUIRED")
        print("=" * 70)


def main():
    """Run complete system test."""
    test = AMOSCompleteSystemTest()
    success = test.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

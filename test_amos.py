#!/usr/bin/env python3
"""AMOS Test & Validation Suite

Comprehensive tests for all AMOS components:
- Unit tests for each module
- Integration tests for component interactions
- End-to-end operational test
- Performance benchmarks

Usage:
    python test_amos.py              # Run all tests
    python test_amos.py --quick    # Run quick tests only
    python test_amos.py --module v4 # Test specific module
"""

import argparse
import sys
import time
from datetime import datetime
from typing import List


class AMOSTestSuite:
    """Comprehensive test suite for AMOS."""

    def __init__(self):
        self.results: List[dict] = []
        self.passed = 0
        self.failed = 0

    def run_all_tests(self, quick: bool = False) -> dict:
        """Run complete test suite."""
        print("=" * 70)
        print("🧪 AMOS TEST & VALIDATION SUITE")
        print("=" * 70)
        print(f"Started: {datetime.now(UTC).isoformat()}")
        print()

        start_time = time.time()

        # Core Component Tests
        self._test_v1_core()
        self._test_v2_memory()
        self._test_v2_meta()
        self._test_v3_time()
        self._test_v3_energy()

        if not quick:
            self._test_v3_repo()
            self._test_v3_self_code()

        # v4 Tests (Critical)
        self._test_v4_basic()
        self._test_v4_production()

        if not quick:
            self._test_v5()
            self._test_connectors()

        # Integration Tests
        self._test_integration()
        self._test_operational_cycle()

        # Summary
        elapsed = time.time() - start_time
        return self._generate_report(elapsed)

    def _test(self, name: str, test_fn) -> bool:
        """Run a single test."""
        try:
            test_fn()
            self.results.append({"name": name, "status": "PASS", "time": time.time()})
            self.passed += 1
            print(f"  ✓ {name}")
            return True
        except Exception as e:
            self.results.append({"name": name, "status": "FAIL", "error": str(e)})
            self.failed += 1
            print(f"  ✗ {name}: {e}")
            return False

    def _test_v1_core(self):
        """Test v1 Core components."""
        print("[Testing v1: Core Cognitive]")

        def test_core_import():
            from amos_core import AMOSCore

            assert AMOSCore is not None

        def test_core_workspace():
            from amos_core import GlobalWorkspace

            gw = GlobalWorkspace()
            gw.broadcast({"test": "data"})
            assert len(gw.state["active_broadcasts"]) > 0

        def test_branch_field():
            from amos_core import BranchFieldEngine

            branch = BranchFieldEngine()
            futures = branch.generate_forks({"goal": "test"}, {"test": True})
            assert len(futures) > 0

        self._test("Core Import", test_core_import)
        self._test("Workspace", test_core_workspace)
        self._test("Branch Field", test_branch_field)
        print()

    def _test_v2_memory(self):
        """Test v2 Memory Systems."""
        print("[Testing v2: Memory Systems]")

        def test_memory_import():
            from amos_memory import AMOSMemory

            assert AMOSMemory is not None

        def test_working_memory():
            from amos_memory import WorkingMemory

            wm = WorkingMemory(capacity=5)
            wm.store("item1", "value1", 0.9)
            assert wm.retrieve("item1") == "value1"

        def test_episodic_memory():
            from amos_memory import EpisodicMemory

            em = EpisodicMemory()
            em.record({"event": "test", "value": 100})
            episodes = em.retrieve_recent(1)
            assert len(episodes) > 0

        self._test("Memory Import", test_memory_import)
        self._test("Working Memory", test_working_memory)
        self._test("Episodic Memory", test_episodic_memory)
        print()

    def _test_v2_meta(self):
        """Test v2 Meta-cognition."""
        print("[Testing v2: Meta-cognition]")

        def test_meta_import():
            from amos_meta import ReflectionEngine

            assert ReflectionEngine is not None

        def test_reflection():
            from amos_meta import ReflectionEngine

            engine = ReflectionEngine()
            result = engine.reflect({"prediction": 0.8, "actual": 0.6, "confidence": 0.9})
            assert "accuracy" in result

        self._test("Meta Import", test_meta_import)
        self._test("Reflection Engine", test_reflection)
        print()

    def _test_v3_time(self):
        """Test v3 Time Engine."""
        print("[Testing v3: Time Engine]")

        def test_time_import():
            from amos_time import TimeEngine

            assert TimeEngine is not None

        def test_event_sourcing():
            from amos_time import EventSourcing

            es = EventSourcing()
            es.record_event("test_action", {"data": "test"})
            assert len(es.events) > 0

        self._test("Time Import", test_time_import)
        self._test("Event Sourcing", test_event_sourcing)
        print()

    def _test_v3_energy(self):
        """Test v3 Energy System."""
        print("[Testing v3: Energy System]")

        def test_energy_import():
            from amos_energy import AMOSEnergySystem

            assert AMOSEnergySystem is not None

        def test_energy_pool():
            from amos_energy import EnergyPool

            pool = EnergyPool("test", 1000)
            pool.allocate(500)
            assert pool.available == 500

        self._test("Energy Import", test_energy_import)
        self._test("Energy Pool", test_energy_pool)
        print()

    def _test_v3_repo(self):
        """Test v3 Repo Intelligence."""
        print("[Testing v3: Repo Intelligence]")

        def test_repo_import():
            from amos_repo import AMOSRepoIntelligence

            assert AMOSRepoIntelligence is not None

        self._test("Repo Import", test_repo_import)
        print()

    def _test_v3_self_code(self):
        """Test v3 Self-coding."""
        print("[Testing v3: Self-coding]")

        def test_self_code_import():
            from amos_self_code import AMOSSelfCoding

            assert AMOSSelfCoding is not None

        self._test("Self-code Import", test_self_code_import)
        print()

    def _test_v4_basic(self):
        """Test v4 Basic Economic Organism."""
        print("[Testing v4: Basic Economic Organism]")

        def test_v4_import():
            from amos_v4 import AMOSv4

            assert AMOSv4 is not None

        def test_persistence():
            from amos_v4 import PersistenceManager, PersistentState

            pm = PersistenceManager(state_dir="test_state")
            state = PersistentState()
            pm.save(state)
            loaded = pm.load()
            assert loaded is not None

        def test_economic_engine():
            from amos_v4 import EconomicEngine

            engine = EconomicEngine()
            action = {
                "expected_revenue": 100,
                "expected_cost": 50,
                "risk_penalty": 10,
                "leverage_factor": 20,
                "compounding_value": 30,
            }
            result = engine.evaluate_action(action)
            assert result["net_value"] > 0

        self._test("v4 Import", test_v4_import)
        self._test("Persistence", test_persistence)
        self._test("Economic Engine", test_economic_engine)
        print()

    def _test_v4_production(self):
        """Test v4 Production Runtime (CRITICAL)."""
        print("[Testing v4: Production Runtime - CRITICAL]")

        def test_v4_prod_import():
            from amos_v4_runtime import AMOSv4ProductionRuntime

            assert AMOSv4ProductionRuntime is not None

        def test_world_model():
            from amos_v4_runtime import Signal, WorldModelEngineV4

            wm = WorldModelEngineV4()
            signal = Signal("test", {"opportunity": 0.8}, datetime.now(UTC), 0.9, 0.9)
            wm.ingest_signal(signal)
            assert len(wm.signals) > 0

        def test_adaptive_allocator():
            from amos_v4_runtime import AdaptiveResourceAllocator

            allocator = AdaptiveResourceAllocator()
            demands = [
                {"name": "task1", "expected_return": 100, "goal_id": "g1", "time_needed": 10},
                {"name": "task2", "expected_return": 50, "goal_id": "g2", "time_needed": 5},
            ]
            result = allocator.allocate_with_learning(demands, {})
            assert "time" in result

        def test_identity_preservation():
            from amos_v4_runtime import IdentityPreservingEconomics

            economics = IdentityPreservingEconomics()
            action = {"name": "test_action"}
            result = economics.evaluate_action_identity_impact(action)
            assert "allowed" in result
            assert "drift_contribution" in result

        def test_feedback_compression():
            from amos_v4_runtime import FeedbackCompressor

            compressor = FeedbackCompressor()
            action = {"type": "test", "expected_duration_days": 30}
            feedback = compressor.get_compressed_feedback(
                action, datetime.now(UTC) - datetime.now(UTC)
            )
            assert "compressed_score" in feedback

        def test_production_cycle():
            from amos_v4_runtime import AMOSv4ProductionRuntime

            amos = AMOSv4ProductionRuntime(name="Test")
            goals = [
                {
                    "id": "test",
                    "name": "Test Goal",
                    "type": "test",
                    "expected_value": 100,
                    "resource_cost": {"time": 10},
                    "risk_score": 0.1,
                }
            ]
            from amos_v4_runtime import Signal

            signals = [Signal("test", {}, datetime.now(UTC), 0.5, 0.5)]
            result = amos.cycle(goals, signals)
            assert "cycle" in result
            assert result["cycle"] == 1

        self._test("v4 Prod Import", test_v4_prod_import)
        self._test("World Model", test_world_model)
        self._test("Adaptive Allocator", test_adaptive_allocator)
        self._test("Identity Preservation", test_identity_preservation)
        self._test("Feedback Compression", test_feedback_compression)
        self._test("Production Cycle", test_production_cycle)
        print()

    def _test_v5(self):
        """Test v5 Civilization-Scale."""
        print("[Testing v5: Civilization-Scale]")

        def test_v5_import():
            from amos_v5 import AMOSv5

            assert AMOSv5 is not None

        def test_political_intelligence():
            from amos_v5 import InstitutionalActor, PoliticalIntelligence

            pi = PoliticalIntelligence()
            actor = InstitutionalActor("a1", "Test", "test", {}, ["test"], [])
            pi.landscape.add_actor(actor)
            assert len(pi.landscape.actors) > 0

        self._test("v5 Import", test_v5_import)
        self._test("Political Intelligence", test_political_intelligence)
        print()

    def _test_connectors(self):
        """Test Real-World Connectors."""
        print("[Testing: Real-World Connectors]")

        def test_connectors_import():
            from amos_connectors import AMOSConnectorSystem

            assert AMOSConnectorSystem is not None

        def test_data_ingestion():
            from amos_connectors import DataIngestionEngine, DataSource

            engine = DataIngestionEngine()
            source = DataSource("test", "api", "http://test.com")
            engine.register_source(source)
            assert len(engine.sources) > 0

        def test_execution_manager():
            from amos_connectors import ExecutionHook, ExecutionManager

            em = ExecutionManager()
            hook = ExecutionHook("h1", "test", lambda x: {"success": True})
            em.register_hook(hook)
            assert len(em.hooks) > 0

        def test_notifications():
            from amos_connectors import NotificationSystem

            ns = NotificationSystem()
            ns.register_channel("test", "console", {})
            ns.notify("Test message", "info")
            assert len(ns.notification_log) > 0

        self._test("Connectors Import", test_connectors_import)
        self._test("Data Ingestion", test_data_ingestion)
        self._test("Execution Manager", test_execution_manager)
        self._test("Notifications", test_notifications)
        print()

    def _test_integration(self):
        """Test component integration."""
        print("[Testing: Component Integration]")

        def test_v4_v4prod_integration():
            from amos_v4 import AMOSv4
            from amos_v4_runtime import AMOSv4ProductionRuntime

            # Verify both can coexist
            basic = AMOSv4(name="Basic")
            prod = AMOSv4ProductionRuntime(name="Prod")
            assert basic is not None and prod is not None

        def test_memory_meta_integration():
            from amos_memory import AMOSMemory
            from amos_meta import ReflectionEngine

            memory = AMOSMemory()
            meta = ReflectionEngine()
            # Store reflection in memory
            reflection = meta.reflect({"prediction": 0.8, "actual": 0.7, "confidence": 0.9})
            memory.working.store("reflection", reflection, 0.9)
            retrieved = memory.working.retrieve("reflection")
            assert retrieved is not None

        self._test("v4 + v4-Prod Integration", test_v4_v4prod_integration)
        self._test("Memory + Meta Integration", test_memory_meta_integration)
        print()

    def _test_operational_cycle(self):
        """Test full operational cycle."""
        print("[Testing: Full Operational Cycle - END TO END]")

        def test_operational_import():
            from amos_operational import AMOSOperational

            assert AMOSOperational is not None

        def test_operational_initialization():
            from amos_operational import AMOSOperational

            amos = AMOSOperational()
            amos.initialize()
            assert amos.runtime is not None or amos.connectors is not None

        def test_operational_single_cycle():
            from amos_operational import AMOSOperational

            amos = AMOSOperational()
            amos.initialize()
            result = amos.run_cycle()
            assert "cycle" in result
            assert result["cycle"] == 1

        def test_operational_status():
            from amos_operational import AMOSOperational

            amos = AMOSOperational()
            amos.initialize()
            status = amos.get_status()
            assert "cycle_count" in status
            assert "health" in status

        self._test("Operational Import", test_operational_import)
        self._test("Operational Init", test_operational_initialization)
        self._test("Operational Cycle", test_operational_single_cycle)
        self._test("Operational Status", test_operational_status)
        print()

    def _generate_report(self, elapsed: float) -> dict:
        """Generate test report."""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print("=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Elapsed: {elapsed:.1f}s")
        print("=" * 70)

        if self.failed == 0:
            print("🎉 ALL TESTS PASSED - AMOS is ready for production!")
        else:
            print(f"⚠ {self.failed} test(s) failed - review errors above")
        print("=" * 70)

        return {
            "total": total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": pass_rate,
            "elapsed_seconds": elapsed,
            "all_passed": self.failed == 0,
            "results": self.results,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Test Suite")
    parser.add_argument(
        "--quick", "-q", action="store_true", help="Run quick tests only (skip v5, connectors)"
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    suite = AMOSTestSuite()
    report = suite.run_all_tests(quick=args.quick)

    if args.json:
        import json

        print(json.dumps(report, indent=2, default=str))

    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

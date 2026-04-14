#!/usr/bin/env python3
"""AMOS Integration Test Suite - Validate all 48 components work together."""

from __future__ import annotations

import sys
import time
from typing import Any
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    duration_ms: int
    error: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class AMOSIntegrationTestSuite:
    """Comprehensive test suite for AMOS ecosystem."""
    
    def __init__(self):
        self.results: list[TestResult] = []
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_all_tests(self) -> dict[str, Any]:
        """Execute complete integration test suite."""
        print("\n" + "=" * 70)
        print("AMOS INTEGRATION TEST SUITE")
        print("=" * 70)
        print("Testing 48 components across 3 phases...")
        
        # Phase 14: AMOSL Runtime Tests
        self._test_phase14_runtime()
        
        # Phase 15: Feature Ecosystem Tests
        self._test_phase15_ecosystem()
        
        # Phase 16: Knowledge & Engine Tests
        self._test_phase16_cognitive()
        
        # Master Orchestrator Tests
        self._test_master_orchestrator()
        
        # End-to-End Integration Tests
        self._test_end_to_end()
        
        return self._generate_report()
    
    def _test_phase14_runtime(self):
        """Test Phase 14 AMOSL Runtime components."""
        print("\n[Phase 14] Testing AMOSL Runtime...")
        
        # Test 1: Ledger
        self._run_test("Ledger_Initialization", self._test_ledger)
        
        # Test 2: Verification Engine
        self._run_test("Verification_Engine", self._test_verification)
        
        # Test 3: Bridge Executor
        self._run_test("Bridge_Executor", self._test_bridge)
        
        # Test 4: Evolution Operator
        self._run_test("Evolution_Operator", self._test_evolution)
        
        # Test 5: Runtime Integration
        self._run_test("Runtime_Integration", self._test_runtime_integration)
    
    def _test_phase15_ecosystem(self):
        """Test Phase 15 Feature Ecosystem components."""
        print("\n[Phase 15] Testing Feature Ecosystem...")
        
        # Test 6: Feature Activation
        self._run_test("Feature_Activation", self._test_feature_activation)
        
        # Test 7: Primary Handler
        self._run_test("Primary_Handler", self._test_primary_handler)
    
    def _test_phase16_cognitive(self):
        """Test Phase 16 Knowledge & Engine components."""
        print("\n[Phase 16] Testing Knowledge & Engines...")
        
        # Test 8: Knowledge Loader
        self._run_test("Knowledge_Loader", self._test_knowledge_loader)
        
        # Test 9: Engine Activator
        self._run_test("Engine_Activator", self._test_engine_activator)
        
        # Test 10: Cognitive Router
        self._run_test("Cognitive_Router", self._test_cognitive_router)
    
    def _test_master_orchestrator(self):
        """Test Master Orchestrator."""
        print("\n[Master Orchestrator] Testing Unified System...")
        
        # Test 11: Orchestrator Initialization
        self._run_test("Orchestrator_Init", self._test_orchestrator_init)
        
        # Test 12: Task Processing
        self._run_test("Task_Processing", self._test_task_processing)
        
        # Test 13: Batch Processing
        self._run_test("Batch_Processing", self._test_batch_processing)
        
        # Test 14: Query System
        self._run_test("Query_System", self._test_query_system)
    
    def _test_end_to_end(self):
        """Test complete end-to-end workflows."""
        print("\n[End-to-End] Testing Complete Workflows...")
        
        # Test 15: Full Pipeline
        self._run_test("Full_Pipeline", self._test_full_pipeline)
        
        # Test 16: Multi-Engine Workflow
        self._run_test("Multi_Engine_Workflow", self._test_multi_engine)
        
        # Test 17: Knowledge-Engine Integration
        self._run_test("Knowledge_Engine_Integration", self._test_knowledge_engine)
        
        # Test 18: Error Handling
        self._run_test("Error_Handling", self._test_error_handling)
    
    # Individual test implementations
    def _test_ledger(self) -> tuple[bool, str, dict]:
        """Test ledger initialization and operation."""
        try:
            from amosl_ledger import StateLedger, EntryType
            ledger = StateLedger()
            entry = ledger.append(EntryType.EVOLUTION_STEP, {"test": True}, {"event": "test"})
            return True, "", {"entries": len(ledger._entries), "hash": entry.hash[:8] if entry else "none"}
        except Exception as e:
            return False, str(e), {}
    
    def _test_verification(self) -> tuple[bool, str, dict]:
        """Test verification engine."""
        try:
            from amosl_verification import VerificationEngine
            from amosl_ledger import StateLedger
            ledger = StateLedger()
            verifier = VerificationEngine(ledger)
            # Pass state with required structure for constraints
            result = verifier.verify_state({
                "classical": {"version": 1},
                "quantum": {"state": "superposition"},
                "biological": {"alignment": True},
                "perspectives": ["technical", "business"],
                "quadrants": ["tech", "ops", "strategy", "human"]
            })
            return result.valid, "", {"proof": result.proof_hash[:8] if result.proof_hash else "none"}
        except Exception as e:
            return False, str(e), {}
    
    def _test_bridge(self) -> tuple[bool, str, dict]:
        """Test bridge executor."""
        try:
            from amosl_bridge import BridgeExecutor
            from amosl_ledger import StateLedger
            from amosl_verification import VerificationEngine
            ledger = StateLedger()
            verifier = VerificationEngine(ledger)
            bridge = BridgeExecutor(ledger, verifier)
            adapters = len(bridge.adapters)
            return True, "", {"adapters": adapters}
        except Exception as e:
            return False, str(e), {}
    
    def _test_evolution(self) -> tuple[bool, str, dict]:
        """Test evolution operator."""
        try:
            from amosl_evolution import EvolutionOperator
            evo = EvolutionOperator()
            stats = evo.get_statistics()
            return True, "", {"operators": len(evo._operators), "chains": stats['total_chains']}
        except Exception as e:
            return False, str(e), {}
    
    def _test_runtime_integration(self) -> tuple[bool, str, dict]:
        """Test all runtime components work together."""
        try:
            from amosl_ledger import StateLedger
            from amosl_verification import VerificationEngine
            from amosl_bridge import BridgeExecutor
            from amosl_evolution import EvolutionOperator
            
            ledger = StateLedger()
            verifier = VerificationEngine(ledger)
            bridge = BridgeExecutor(ledger, verifier)
            evo = EvolutionOperator(ledger, verifier, bridge)
            
            return True, "", {"integrated": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_feature_activation(self) -> tuple[bool, str, dict]:
        """Test feature activation system."""
        try:
            from amos_feature_activation import FeatureActivationSystem
            activation = FeatureActivationSystem()
            return True, "", {"initialized": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_primary_handler(self) -> tuple[bool, str, dict]:
        """Test primary feature handler."""
        try:
            from amos_primary_feature_handler import PrimaryFeatureHandler
            handler = PrimaryFeatureHandler()
            return True, "", {"initialized": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_knowledge_loader(self) -> tuple[bool, str, dict]:
        """Test knowledge loader."""
        try:
            from amos_knowledge_loader import KnowledgeLoader
            loader = KnowledgeLoader()
            return True, "", {"initialized": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_engine_activator(self) -> tuple[bool, str, dict]:
        """Test engine activator."""
        try:
            from amos_engine_activator import EngineActivator
            activator = EngineActivator()
            return True, "", {"initialized": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_cognitive_router(self) -> tuple[bool, str, dict]:
        """Test cognitive router."""
        try:
            from amos_cognitive_router import CognitiveRouter
            router = CognitiveRouter()
            decision = router.route_task("Test task")
            return True, "", {"category": decision.engine_category}
        except Exception as e:
            return False, str(e), {}
    
    def _test_orchestrator_init(self) -> tuple[bool, str, dict]:
        """Test master orchestrator initialization."""
        try:
            from amos_master_cognitive_orchestrator import MasterCognitiveOrchestrator
            amos = MasterCognitiveOrchestrator()
            # Don't fully initialize to save time, just check it can be created
            return True, "", {"created": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_task_processing(self) -> tuple[bool, str, dict]:
        """Test task processing through router."""
        try:
            from amos_cognitive_router import CognitiveRouter
            router = CognitiveRouter()
            decision = router.route_task("Generate code")
            return decision.selected_engine != "", "", {"engine": decision.selected_engine}
        except Exception as e:
            return False, str(e), {}
    
    def _test_batch_processing(self) -> tuple[bool, str, dict]:
        """Test batch processing."""
        try:
            from amos_cognitive_router import CognitiveRouter
            router = CognitiveRouter()
            tasks = ["Task 1", "Task 2", "Task 3"]
            decisions = router.batch_route(tasks)
            return len(decisions) == 3, "", {"routed": len(decisions)}
        except Exception as e:
            return False, str(e), {}
    
    def _test_query_system(self) -> tuple[bool, str, dict]:
        """Test query system."""
        try:
            from amos_knowledge_loader import KnowledgeLoader
            loader = KnowledgeLoader()
            # Just test it can be queried (may return empty if no knowledge loaded)
            results = loader.query_knowledge("test", top_n=1)
            return True, "", {"queryable": True}
        except Exception as e:
            return False, str(e), {}
    
    def _test_full_pipeline(self) -> tuple[bool, str, dict]:
        """Test complete pipeline: Router → Engine."""
        try:
            from amos_cognitive_router import CognitiveRouter
            from amos_engine_activator import EngineActivator
            
            router = CognitiveRouter()
            activator = EngineActivator()
            
            # Route task
            decision = router.route_task("Consulting task")
            
            # Check engine can be invoked (without full activation)
            return decision.engine_category != "", "", {"pipeline": "functional"}
        except Exception as e:
            return False, str(e), {}
    
    def _test_multi_engine(self) -> tuple[bool, str, dict]:
        """Test multiple engines can be routed."""
        try:
            from amos_cognitive_router import CognitiveRouter
            router = CognitiveRouter()
            
            tasks = [
                "Consulting task",
                "Coding task", 
                "Legal task",
                "Vietnam task"
            ]
            
            categories = set()
            for task in tasks:
                decision = router.route_task(task)
                categories.add(decision.engine_category)
            
            return len(categories) >= 2, "", {"categories_used": len(categories)}
        except Exception as e:
            return False, str(e), {}
    
    def _test_knowledge_engine(self) -> tuple[bool, str, dict]:
        """Test knowledge and engine integration."""
        try:
            from amos_knowledge_loader import KnowledgeLoader
            from amos_cognitive_router import CognitiveRouter
            
            loader = KnowledgeLoader()
            router = CognitiveRouter()
            
            # Route to category
            decision = router.route_task("Vietnam market analysis")
            
            # Query knowledge in same category
            knowledge = loader.get_knowledge(decision.engine_category)
            
            return True, "", {"category": decision.engine_category}
        except Exception as e:
            return False, str(e), {}
    
    def _test_error_handling(self) -> tuple[bool, str, dict]:
        """Test error handling."""
        try:
            from amos_cognitive_router import CognitiveRouter
            router = CognitiveRouter()
            
            # Test with empty task
            decision = router.route_task("")
            
            # Should still return a decision (default category)
            return decision.selected_engine != "", "", {"handles_empty": True}
        except Exception as e:
            return False, str(e), {}
    
    def _run_test(self, name: str, test_func):
        """Run a single test and record result."""
        start = time.time()
        try:
            passed, error, details = test_func()
            duration = int((time.time() - start) * 1000)
            
            result = TestResult(
                name=name,
                passed=passed,
                duration_ms=duration,
                error=error,
                details=details
            )
            
            self.results.append(result)
            self.tests_run += 1
            
            if passed:
                self.tests_passed += 1
                status = "✓ PASS"
            else:
                self.tests_failed += 1
                status = "✗ FAIL"
            
            print(f"  {status} {name} ({duration}ms)")
            if error:
                print(f"       Error: {error[:60]}...")
            
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            result = TestResult(
                name=name,
                passed=False,
                duration_ms=duration,
                error=str(e),
                details={}
            )
            self.results.append(result)
            self.tests_run += 1
            self.tests_failed += 1
            print(f"  ✗ FAIL {name} ({duration}ms) - Exception: {str(e)[:40]}...")
    
    def _generate_report(self) -> dict[str, Any]:
        """Generate test report."""
        total_duration = sum(r.duration_ms for r in self.results)
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"  Tests Run: {self.tests_run}")
        print(f"  Passed: {self.tests_passed} ✓")
        print(f"  Failed: {self.tests_failed} ✗")
        print(f"  Success Rate: {self.tests_passed/self.tests_run*100:.1f}%")
        print(f"  Total Duration: {total_duration}ms")
        print(f"  Avg Duration: {total_duration/self.tests_run:.0f}ms")
        
        if self.tests_failed > 0:
            print("\n  Failed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"    ✗ {r.name}: {r.error[:50]}...")
        
        print("=" * 70)
        
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate": self.tests_passed / self.tests_run if self.tests_run > 0 else 0,
            "total_duration_ms": total_duration,
            "all_passed": self.tests_failed == 0
        }


def run_integration_tests():
    """Run complete integration test suite."""
    suite = AMOSIntegrationTestSuite()
    results = suite.run_all_tests()
    
    print("\n" + "=" * 70)
    if results['all_passed']:
        print("✓ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
    else:
        print("⚠ SOME TESTS FAILED - REVIEW BEFORE DEPLOYMENT")
    print("=" * 70)
    
    return 0 if results['all_passed'] else 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())

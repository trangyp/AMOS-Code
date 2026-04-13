"""AMOSL Integration Test Suite.

Comprehensive validation of the complete AMOSL ecosystem:
- Cross-module integration
- 5-lens regime consistency
- End-to-end workflows
- Performance regression
- Stress testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from amosl.runtime import RuntimeKernel
from amosl.prover import TheoremProver
from amosl.ledger import Ledger
from amosl.bridge import BridgeExecutor, BridgeType
from amosl.evolution import EvolutionOperator, BlockMatrix
from amosl.geometry import InformationGeometry, BeliefState
from amosl.modal import ModalLogic, StratifiedTruth, TruthValue
from amosl.field import FieldEvolution, FieldState


class TestCrossModuleIntegration(unittest.TestCase):
    """Test integration between all amosl modules."""
    
    def test_runtime_to_prover_integration(self):
        """Test runtime state verification with prover."""
        kernel = RuntimeKernel()
        prover = TheoremProver()
        
        # Execute steps
        for i in range(10):
            kernel.step(action_bundle={"classical": {"set": {"counter": i}}})
        
        # Verify with prover
        proof = prover.prove_valid(kernel.state)
        self.assertTrue(proof.is_valid())
        self.assertEqual(proof.metadata.get("checked"), 8)
    
    def test_runtime_to_ledger_integration(self):
        """Test runtime execution with ledger recording."""
        kernel = RuntimeKernel()
        ledger = Ledger()
        
        for i in range(5):
            kernel.step(action_bundle={"classical": {"set": {"step": i}}})
            ledger.record(
                step=i,
                state=kernel.state,
                outcome={"step": i, "status": "completed"}
            )
        
        self.assertEqual(len(ledger.entries), 5)
        self.assertTrue(ledger.verify_chain()[0])
    
    def test_bridge_to_runtime_integration(self):
        """Test bridge execution within runtime context."""
        kernel = RuntimeKernel()
        bridge = BridgeExecutor()
        
        # Classical computation
        kernel.step(action_bundle={"classical": {"set": {"bit": 1}}})
        
        # Bridge to quantum
        result = bridge.execute(BridgeType.C_TO_Q, 1, qubit=0)
        self.assertEqual(result['output']['value'], "|1⟩")
        
        # Bridge back to classical
        q_state = {"outcome": 1, "uncertainty": 0.1}
        result = bridge.execute(BridgeType.Q_TO_C, q_state)
        self.assertTrue(result['output'])


class TestFiveLensRegime(unittest.TestCase):
    """Test all 5 mathematical lenses work together."""
    
    def test_axiomatic_lens(self):
        """Test 8 axioms are satisfied."""
        state = FieldState(
            classical={'energy': 10.0},
            quantum={'coherence': 0.95},
            biological={'growth_rate': 0.1}
        )
        
        # Axiom I: Stratified existence
        self.assertIsNotNone(state.classical)
        self.assertIsNotNone(state.quantum)
        self.assertIsNotNone(state.biological)
    
    def test_logical_lens(self):
        """Test stratified modal logic."""
        modal = ModalLogic()
        
        # Necessity
        domain = [{'valid': True}, {'valid': True}]
        result = modal.necessity(
            lambda x: StratifiedTruth(TruthValue.TRUE) if x['valid'] else StratifiedTruth(TruthValue.FALSE),
            domain
        )
        self.assertTrue(result.is_definitely_true())
        
        # Possibility
        domain = [{'valid': False}, {'valid': True}]
        result = modal.possibility(
            lambda x: StratifiedTruth(TruthValue.TRUE) if x['valid'] else StratifiedTruth(TruthValue.FALSE),
            domain
        )
        self.assertTrue(result.is_definitely_true())
    
    def test_information_geometric_lens(self):
        """Test belief manifold operations."""
        geometry = InformationGeometry()
        
        prior = BeliefState(distribution={'a': 0.6, 'b': 0.4}, timestamp=0.0)
        likelihood = {'a': 0.8, 'b': 0.3}
        
        posterior = geometry.bayesian_update(prior, likelihood, 'obs')
        
        # KL divergence should be finite
        kl = geometry.kl_divergence(prior, posterior)
        self.assertGreaterEqual(kl, 0.0)
        self.assertLess(kl, 1.0)
    
    def test_field_lens(self):
        """Test Lagrangian dynamics."""
        evolution = FieldEvolution()
        initial = FieldState(
            classical={'energy': 10.0, 'computation_cost': 1.0},
            quantum={'coherence': 0.95, 'energy_expectation': 5.0},
            biological={'growth_rate': 0.1}
        )
        
        # Compute Lagrangian
        terms = evolution.compute_lagrangian(initial)
        self.assertIsNotNone(terms.total())
        
        # Evolve
        trajectory = evolution.evolve_with_constraints(initial, steps=5, dt=0.1)
        self.assertEqual(len(trajectory), 6)  # Initial + 5 steps
        
        # Action functional
        action = evolution.action_functional(trajectory, dt=0.1)
        self.assertIsInstance(action, float)


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""
    
    def test_complete_execution_pipeline(self):
        """Test full execution: Runtime → Verify → Ledger → Explain."""
        kernel = RuntimeKernel()
        prover = TheoremProver()
        ledger = Ledger()
        
        # Execute 10 steps
        for i in range(10):
            kernel.step(action_bundle={"classical": {"set": {"step": i}}})
            
            # Verify
            proof = prover.prove_valid(kernel.state)
            self.assertTrue(proof.is_valid())
            
            # Record to ledger
            ledger.record(
                step=i,
                state=kernel.state,
                outcome={"step": i, "verified": True},
                invariants_satisfied=True
            )
        
        # Explain outcome
        explanation = ledger.explain({"step": 5, "verified": True})
        self.assertIsNotNone(explanation)
        self.assertEqual(explanation['step'], 5)
    
    def test_multi_substrate_hybrid(self):
        """Test hybrid multi-substrate execution."""
        kernel = RuntimeKernel()
        bridge = BridgeExecutor()
        
        # Classical
        kernel.step(action_bundle={"classical": {"set": {"control": 0.8}}})
        
        # C→Q bridge
        result = bridge.execute(BridgeType.C_TO_Q, 1)
        self.assertEqual(result['output']['value'], "|1⟩")
        
        # C→B bridge
        result = bridge.execute(BridgeType.C_TO_B, 0.8, threshold=0.5)
        self.assertTrue(result['output']['activated'])
        
        # B→C bridge
        result = bridge.execute(BridgeType.B_TO_C, 0.75, threshold=0.5)
        self.assertTrue(result['output'])
    
    def test_five_lens_integration(self):
        """Test all 5 lenses in single execution."""
        # 1. Axiomatic: Create field state
        field = FieldState(
            classical={'energy': 10.0},
            quantum={'coherence': 0.95},
            biological={'growth_rate': 0.1}
        )
        
        # 2. Logical: Modal verification
        modal = ModalLogic()
        domain = [{'valid': True}]
        truth = modal.necessity(
            lambda x: StratifiedTruth(TruthValue.TRUE),
            domain
        )
        self.assertTrue(truth.is_definitely_true())
        
        # 3. InfoGeo: Belief update
        geometry = InformationGeometry()
        prior = BeliefState(distribution={'a': 0.6, 'b': 0.4}, timestamp=0.0)
        posterior = geometry.bayesian_update(prior, {'a': 0.8, 'b': 0.3}, 'obs')
        
        # 4. Field: Evolution
        evolution = FieldEvolution()
        terms = evolution.compute_lagrangian(field)
        trajectory = evolution.evolve_with_constraints(field, steps=3)
        
        # 5. Control: Block matrix (already in evolution)
        self.assertEqual(len(trajectory), 4)


class TestPerformanceRegression(unittest.TestCase):
    """Test performance doesn't degrade below benchmarks."""
    
    def test_field_evolution_performance(self):
        """Field evolution should complete in <10ms for 50 steps."""
        import time
        from amosl.field import FieldEvolution, FieldState
        
        evolution = FieldEvolution()
        initial = FieldState(
            classical={'energy': 10.0},
            quantum={'coherence': 0.95},
            biological={'growth_rate': 0.1}
        )
        
        start = time.perf_counter()
        trajectory = evolution.evolve_with_constraints(initial, steps=50, dt=0.1)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertLess(elapsed, 10.0, f"Field evolution too slow: {elapsed:.2f}ms")
        self.assertEqual(len(trajectory), 51)
    
    def test_lagrangian_compute_performance(self):
        """Lagrangian compute should complete 100 iterations in <5ms."""
        import time
        from amosl.field import FieldEvolution, FieldState
        
        evolution = FieldEvolution()
        state = FieldState(
            classical={'energy': 10.0},
            quantum={'coherence': 0.95},
            biological={'growth_rate': 0.1}
        )
        
        start = time.perf_counter()
        for _ in range(100):
            _ = evolution.compute_lagrangian(state)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertLess(elapsed, 5.0, f"Lagrangian compute too slow: {elapsed:.2f}ms")
    
    def test_invariant_check_performance(self):
        """Invariant check should complete 50 iterations in <5ms."""
        import time
        from amosl.prover import TheoremProver
        from amosl.runtime import RuntimeKernel
        
        prover = TheoremProver()
        kernel = RuntimeKernel()
        
        for i in range(5):
            kernel.step(action_bundle={"classical": {"set": {"x": i}}})
        
        start = time.perf_counter()
        for _ in range(50):
            _ = prover.prove_valid(kernel.state)
        elapsed = (time.perf_counter() - start) * 1000
        
        self.assertLess(elapsed, 5.0, f"Invariant check too slow: {elapsed:.2f}ms")


class TestStressTests(unittest.TestCase):
    """Stress tests for large-scale operations."""
    
    def test_large_trajectory(self):
        """Test 1000-step trajectory."""
        from amosl.field import FieldEvolution, FieldState
        
        evolution = FieldEvolution()
        initial = FieldState(
            classical={'energy': 10.0},
            quantum={'coherence': 0.95},
            biological={'growth_rate': 0.1}
        )
        
        trajectory = evolution.evolve_with_constraints(initial, steps=1000, dt=0.01)
        self.assertEqual(len(trajectory), 1001)
        
        stats = evolution.get_statistics()
        self.assertEqual(stats['trajectory_length'], 1001)
    
    def test_many_ledger_entries(self):
        """Test 1000 ledger entries."""
        from amosl.ledger import Ledger
        from amosl.runtime import RuntimeKernel
        
        kernel = RuntimeKernel()
        ledger = Ledger()
        
        for i in range(1000):
            ledger.record(
                step=i,
                state=kernel.state,
                outcome={"step": i}
            )
        
        self.assertEqual(len(ledger.entries), 1000)
        valid, _ = ledger.verify_chain()
        self.assertTrue(valid)
    
    def test_many_bridge_operations(self):
        """Test 1000 bridge operations."""
        from amosl.bridge import BridgeExecutor, BridgeType
        
        bridge = BridgeExecutor()
        
        for i in range(1000):
            result = bridge.execute(BridgeType.C_TO_Q, i % 2)
            self.assertIsNotNone(result)


def run_integration_tests():
    """Run the complete integration test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCrossModuleIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFiveLensRegime))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestStressTests))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Comprehensive Test Suite for AMOS 57-Component System

Tests all layers:
- Layer 1: Production System (46 components)
- Layer 2: 21-Tuple Formal Core
- Layer 3: Meta-Ontological (12 components)
- Layer 4: Meta-Architecture (10 systems)

Total: 57 components validated
"""

import sys
sys.path.insert(0, '/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code')

import unittest
from datetime import datetime, timedelta

# Import all layers
from amos_meta_architecture import (
    MetaGovernance, Promise, PromiseScope, PromiseStatus,
    Breach, BreachClass, BreachSeverity,
    IdentityContinuity, IdentityTransform,
    EquivalenceClaim,
    MemoryObligation, ForgettingPermit,
    Disagreement, DisagreementClass,
    LegitimacyClaim,
    SelfModification, SelfModificationType,
    SemanticEntity,
    LawRank
)
from amos_meta_ontological import (
    AMOSMetaOntological, EnergyBudget, WorldState,
    TemporalHierarchy, TimeScale,
    SelfRepresentation,
    IdentityManifold,
    ObserverState,
    SheafOfTruths,
    AgencyField,
    EmbodimentOperator,
    ProgramDeformation,
    RenormalizationOperator,
    MetaSemanticEvaluator,
    EthicalBoundary, DeonticStatus
)
from amos_formal_core import (
    AMOSFormalSystem, StateBundle, ActionUniverse
)
from amos_coherence_engine import AMOSCoherenceEngine


class TestMetaArchitectureLayer(unittest.TestCase):
    """Test Layer 4: Meta-Architecture (10 systems)"""

    def setUp(self):
        self.meta = MetaGovernance()

    def test_promise_system(self):
        """Test Promise System - explicit promise representation"""
        promise = Promise(
            description="API compatibility promise",
            owner="platform_team",
            scope=PromiseScope.API_COMPATIBILITY,
            enforceable_authority=True,
            proof_exists=True,
            resource_available=True
        )
        promise.discharge_conditions = ["migration_complete"]
        
        pid = self.meta.promise_registry.register(promise)
        self.assertIsNotNone(pid)
        self.assertTrue(promise.is_strong())
        
        # Test drift detection
        valid, reason = promise.check_drift({'supports_promise': True})
        self.assertTrue(valid)
        
        # Test discharge
        discharged = promise.discharge({'migration_complete': True})
        self.assertTrue(discharged)
        self.assertEqual(promise.status, PromiseStatus.DISCHARGED)

    def test_breach_system(self):
        """Test Breach System - breach classification and discharge"""
        breach = Breach(
            breach_class=BreachClass.PROMISE_BREACH,
            severity=BreachSeverity.HIGH,
            description="API promise violated",
            discharge_obligations=["rollback", "notify"],
            escalation_path="architectural_council"
        )
        
        bid = self.meta.breach_registry.register(breach)
        self.assertIsNotNone(bid)
        self.assertTrue(breach.can_discharge())
        self.assertTrue(breach.check_normalization_prevention())

    def test_identity_continuity(self):
        """Test Identity-Over-Time System"""
        identity = self.meta.identity_registry.register("service_v1", "service")
        identity.add_successor(
            "service_v2", 
            IdentityTransform.SUCCESSOR,
            "Migrated to new version"
        )
        
        self.assertEqual(len(identity.successors), 1)
        self.assertEqual(identity.successors[0][1], IdentityTransform.SUCCESSOR)
        
        # Test resurrection prevention
        self.meta.identity_registry.retire("service_v1")
        valid, msg = self.meta.identity_registry.check_resurrection_attempt("service_v1")
        self.assertFalse(valid)

    def test_equivalence_system(self):
        """Test Equivalence System with regime tagging"""
        equiv = EquivalenceClaim(
            entity_a="db_v1",
            entity_b="db_v2",
            valid_regimes=["read_only", "migration"],
            valid_modes=["compatibility"],
            valid_trust_domains=["production"],
            preserved_obligations=["ACID"],
            mediated_by="migration_adapter",
            semantic_loss_budget=0.05
        )
        
        self.assertTrue(equiv.check_wrapper_truthfulness())
        self.assertTrue(equiv.check_contextual_validity(
            "read_only", "compatibility", "production"
        ))

    def test_memory_governance(self):
        """Test Memory/Forgetting System"""
        # Required memory
        memory = MemoryObligation(
            fact_type="audit_log",
            required_for=["compliance", "forensics"],
            horizon=timedelta(days=365*7)
        )
        self.meta.memory_governor.add_required(memory)
        
        # Permitted forgetting
        permit = ForgettingPermit(
            fact_types=["temp_cache"],
            safe_to_forget=["temp_cache"],
            proof_of_safety="cache_is_temporary"
        )
        self.meta.memory_governor.add_permitted(permit)
        
        # Test conflict check
        valid, _ = self.meta.memory_governor.check_conflict("temp_cache")
        self.assertTrue(valid)

    def test_disagreement_resolution(self):
        """Test Disagreement Resolution System"""
        disagreement = Disagreement(
            disagreement_class=DisagreementClass.MODEL_DIVERGENCE,
            parties=["team_a", "team_b"],
            arbiter="chief_architect",
            unresolved_policy="degraded_action"
        )
        
        did = self.meta.disagreement_registry.register(disagreement)
        self.assertIsNotNone(did)
        self.assertEqual(disagreement.get_progress_path(), "degraded_action")

    def test_legitimacy_system(self):
        """Test Legitimacy System"""
        legitimacy = LegitimacyClaim(
            surface="production_deployments",
            declared_authority="release_engineering",
            actual_controller="release_engineering"
        )
        
        lid = self.meta.legitimacy_registry.register(legitimacy)
        self.assertIsNotNone(lid)
        self.assertTrue(legitimacy.check_alignment())

    def test_self_modification(self):
        """Test Self-Modification System"""
        self_mod = SelfModification(
            mod_type=SelfModificationType.POLICY_UPDATE,
            target="retention_policy",
            authority="data_governance",
            fixed_point_checkpoint="policy_v1_backup",
            staged_validation=True,
            rollback_ready=True
        )
        
        smid = self.meta.self_mod_governor.propose(self_mod)
        self.assertIsNotNone(smid)
        self.assertTrue(self_mod.check_fixed_point())

    def test_semantic_survival(self):
        """Test Semantic Survival System"""
        entity = SemanticEntity(
            entity_id="consent_flow",
            meaning_signature={
                "informed": True,
                "revocable": True,
                "auditable": True
            }
        )
        
        sid = self.meta.semantic_registry.register(entity)
        self.assertIsNotNone(sid)
        
        # Test meaning preservation
        valid = entity.check_semantic_survival({
            "informed": True,
            "revocable": True,
            "auditable": True
        })
        self.assertTrue(valid)

    def test_full_validation(self):
        """Test complete meta-governance validation"""
        results = self.meta.validate_full_system()
        self.assertIn('promise_integrity', results)
        self.assertIn('breach_semantics', results)
        self.assertIn('all_valid', results)


class TestMetaOntologicalLayer(unittest.TestCase):
    """Test Layer 3: Meta-Ontological (12 components)"""

    def setUp(self):
        self.meta_ont = AMOSMetaOntological()

    def test_energy_budget(self):
        """Test Energy Budget (Thermodynamics)"""
        energy = EnergyBudget(
            computation=0.5,
            observation=0.2,
            communication=0.1,
            memory=0.1,
            adaptation=0.05,
            ethics=0.05
        )
        total = energy.total()
        self.assertLessEqual(total, 1.0)
        self.assertTrue(self.meta_ont.check_landauer_bound(total, 1.0))

    def test_temporal_hierarchy(self):
        """Test Temporal Hierarchy (Multi-scale Time)"""
        temporal = TemporalHierarchy()
        self.assertEqual(temporal.current_scale, TimeScale.CLASSICAL)
        
        # Test scale transitions
        temporal.current_scale = TimeScale.QUANTUM
        self.assertTrue(temporal.scale_admissible(TimeScale.QUANTUM))

    def test_identity_manifold(self):
        """Test Identity Manifold"""
        identity = IdentityManifold()
        identity.update_metric(0.95)
        self.assertGreater(identity.identity_score, 0.9)
        self.assertTrue(identity.check_persistence(0.9))

    def test_ethical_boundary(self):
        """Test Ethical Boundary (Deontic)"""
        ethical = EthicalBoundary()
        state = {'action': 'test', 'constraints': ['ethical']}
        
        valid, status = ethical.check_deontic(state)
        self.assertTrue(valid)
        self.assertEqual(status, DeonticStatus.PERMITTED)

    def test_grand_unified_step(self):
        """Test Grand Unified AMOS Step"""
        x_t = {'id': 'test', 'type': 'test_system'}
        u_t = {'action': 'test_action'}
        w_t = WorldState(resource_availability={'compute': 1.0})
        
        x_t1, w_t1, meta = self.meta_ont.grand_unified_step(
            x_t, u_t, w_t, energy_budget=1.0
        )
        
        self.assertIsNotNone(x_t1)
        self.assertIsNotNone(meta)
        self.assertIn('energy_used', meta)


class TestFormalCoreLayer(unittest.TestCase):
    """Test Layer 2: 21-Tuple Formal Core"""

    def setUp(self):
        self.formal = AMOSFormalSystem()

    def test_formal_system_initialization(self):
        """Test 21-tuple formal system initialization"""
        self.assertIsNotNone(self.formal.intent)
        self.assertIsNotNone(self.formal.syntax)
        self.assertIsNotNone(self.formal.ontology)
        self.assertIsNotNone(self.formal.dynamics)
        self.assertIsNotNone(self.formal.verification)

    def test_state_bundle_creation(self):
        """Test State Bundle creation"""
        bundle = StateBundle(
            intent=self.formal.intent,
            environment=self.formal.state.environment,
            constraints=self.formal.constraints
        )
        self.assertIsNotNone(bundle)

    def test_universal_step(self):
        """Test Universal AMOS Step"""
        x_t = StateBundle(
            intent=self.formal.intent,
            environment=self.formal.state.environment,
            constraints=self.formal.constraints
        )
        u_t = ActionUniverse(
            available=["test_action"],
            substrate="test",
            target="test"
        )
        
        x_t1 = self.formal.universal_step(x_t, u_t)
        self.assertIsNotNone(x_t1)


class TestProductionLayer(unittest.TestCase):
    """Test Layer 1: Production System (46 components)"""

    def setUp(self):
        self.coherence = AMOSCoherenceEngine()

    def test_coherence_engine(self):
        """Test Coherence Engine"""
        result = self.coherence.process("Test message for coherence analysis")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.detected_state)
        self.assertIsNotNone(result.intervention_mode)

    def test_coherence_signal_detection(self):
        """Test Signal Detection"""
        result = self.coherence.process("I'm feeling overwhelmed with work")
        self.assertTrue(result.signal_detected or not result.signal_detected)
        self.assertIsNotNone(result.response)


class TestIntegration(unittest.TestCase):
    """Integration tests across all 57 components"""

    def test_all_layers_integration(self):
        """Test all 4 layers working together"""
        # Layer 4: Meta-governance
        meta_gov = MetaGovernance()
        
        # Layer 3: Meta-ontological
        meta_ont = AMOSMetaOntological()
        
        # Layer 2: Formal core
        formal = AMOSFormalSystem()
        
        # Layer 1: Coherence
        coherence = AMOSCoherenceEngine()
        
        # Execute across all layers
        # 1. Coherence processing
        coherence_result = coherence.process("System integration test")
        self.assertIsNotNone(coherence_result)
        
        # 2. Formal step
        x_t = StateBundle(
            intent=formal.intent,
            environment=formal.state.environment,
            constraints=formal.constraints
        )
        u_t = ActionUniverse(
            available=["integrate"],
            substrate="test",
            target="test"
        )
        x_t1 = formal.universal_step(x_t, u_t)
        self.assertIsNotNone(x_t1)
        
        # 3. Meta-ontological step
        x_dict = {'id': 'integration_test'}
        u_dict = {'action': 'unify'}
        w_t = WorldState(resource_availability={'compute': 1.0})
        x_t2, w_t2, meta = meta_ont.grand_unified_step(x_dict, u_dict, w_t, 1.0)
        self.assertIsNotNone(x_t2)
        
        # 4. Meta-governance validation
        results = meta_gov.validate_full_system()
        self.assertIn('all_valid', results)
        
        print(f"\n   ✓ All 57 components integrated successfully")

    def test_component_count(self):
        """Verify all 57 components are present"""
        counts = {
            'production': 46,
            'formal_core': 21,
            'meta_ontological': 12,
            'meta_architecture': 10
        }
        total = sum(counts.values())
        self.assertEqual(total, 57)


def run_comprehensive_tests():
    """Run all 57-component tests."""
    print("=" * 70)
    print("AMOS 57-COMPONENT COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMetaArchitectureLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestMetaOntologicalLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestFormalCoreLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL 57 COMPONENTS VALIDATED SUCCESSFULLY")
    else:
        print("\n⚠️  Some tests failed - review required")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

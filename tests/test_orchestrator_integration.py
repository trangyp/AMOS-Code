#!/usr/bin/env python3
"""AMOS Orchestrator Integration Test
=====================================

Validates the complete 15-subsystem orchestration cycle.
Tests all handlers, bridges, and integrations.

Usage:
  python tests/test_orchestrator_integration.py
  python -m pytest tests/test_orchestrator_integration.py -v
"""

import sys
import unittest
from pathlib import Path


class TestPrimaryLoopCompleteness(unittest.TestCase):
    """Test that all 15 subsystems are in PRIMARY_LOOP."""

    def test_all_subsystems_present(self):
        """Verify all expected subsystems are registered."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import HANDLER_MAP, PRIMARY_LOOP

        expected_subsystems = [
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_SKELETON",
            "08_WORLD_MODEL",
            "09_SOCIAL_ENGINE",
            "10_LIFE_ENGINE",
            "11_LEGAL_BRAIN",
            "12_QUANTUM_LAYER",
            "13_FACTORY",
            "13_MEMORY_ARCHIVAL",
            "15_KNOWLEDGE_CORE",
            "06_MUSCLE",
            "07_METABOLISM",
        ]

        missing = [s for s in expected_subsystems if s not in PRIMARY_LOOP]
        extra = [s for s in PRIMARY_LOOP if s not in expected_subsystems]

        print(f"\n  Expected: {len(expected_subsystems)} subsystems")
        print(f"  In loop: {len(PRIMARY_LOOP)} subsystems")
        print(f"  Handlers: {len(HANDLER_MAP)} registered")

        self.assertEqual(len(missing), 0, f"Missing subsystems: {missing}")
        if extra:
            print(f"  ! Extra subsystems: {extra}")
        print("  ✓ All subsystems present")


class TestHandlerMapCoverage(unittest.TestCase):
    """Test that all subsystems have handlers."""

    def test_all_handlers_registered(self):
        """Verify handlers exist for all subsystems."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import HANDLER_MAP, PRIMARY_LOOP

        missing_handlers = [s for s in PRIMARY_LOOP if s not in HANDLER_MAP]
        self.assertEqual(len(missing_handlers), 0, f"Missing handlers: {missing_handlers}")
        print(f"  ✓ All {len(PRIMARY_LOOP)} subsystems have handlers")

    def test_critical_handlers_exist(self):
        """Verify critical handlers are registered."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import HANDLER_MAP

        critical_handlers = [
            "01_BRAIN",
            "06_MUSCLE",
            "03_IMMUNE",
            "13_MEMORY_ARCHIVAL",
            "15_KNOWLEDGE_CORE",
        ]

        for handler in critical_handlers:
            self.assertIn(handler, HANDLER_MAP, f"{handler} handler not registered")
            print(f"    ✓ {handler} handler registered")


class TestBrainHandler(unittest.TestCase):
    """Test BrainHandler with bridge integrations."""

    def test_brain_handler_operational(self):
        """Verify BrainHandler is operational with bridges."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import BrainHandler

        handler = BrainHandler("01_BRAIN", {"kernel_refs": []})

        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "pending_tasks": []}

        result = handler.process(context)

        print(f"  Status: {result.status}")
        print(f"  Actions: {len(result.actions)}")
        print(f"  Cognitive engines: {result.outputs.get('cognitive_engines_loaded', 0)}")
        print(f"  Bridge operational: {result.outputs.get('bridge_operational', False)}")
        print(f"  Tasks routed: {result.outputs.get('tasks_routed', 0)}")

        self.assertEqual(result.status, "active", "Brain handler not active")
        print("  ✓ Brain handler operational")


class TestMuscleHandler(unittest.TestCase):
    """Test MuscleHandler with Brain-Muscle Bridge."""

    def test_muscle_handler_operational(self):
        """Verify MuscleHandler is operational."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import MuscleHandler

        handler = MuscleHandler("06_MUSCLE", {})

        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "pending_tasks": []}

        result = handler.process(context)

        print(f"  Status: {result.status}")
        print(f"  Bridge operational: {result.outputs.get('bridge_operational', False)}")
        print(f"  Optimization enabled: {result.outputs.get('optimization_enabled', False)}")
        print(f"  Execution plan steps: {result.outputs.get('execution_plan_steps', 0)}")

        self.assertEqual(result.status, "active", "Muscle handler not active")
        print("  ✓ Muscle handler operational")


class TestMemoryArchivalHandler(unittest.TestCase):
    """Test MemoryArchivalHandler integration."""

    def test_memory_archival_operational(self):
        """Verify MemoryArchivalHandler is operational."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import MemoryArchivalHandler

        handler = MemoryArchivalHandler("13_MEMORY_ARCHIVAL", {})

        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "cycle_results": []}

        result = handler.process(context)

        print(f"  Status: {result.status}")
        print(f"  Actions: {len(result.actions)}")
        print(f"  Archived count: {result.outputs.get('archived_count', 0)}")

        self.assertEqual(result.status, "active", "Memory archival not active")
        print("  ✓ Memory archival operational")


class TestKnowledgeCoreHandler(unittest.TestCase):
    """Test KnowledgeCoreHandler integration."""

    def test_knowledge_core_operational(self):
        """Verify KnowledgeCoreHandler is operational."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import KnowledgeCoreHandler

        handler = KnowledgeCoreHandler("15_KNOWLEDGE_CORE", {})

        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root}

        result = handler.process(context)

        print(f"  Status: {result.status}")
        print(f"  Features discovered: {result.outputs.get('features_discovered', 0)}")
        print(f"  Engines cataloged: {result.outputs.get('engines_cataloged', 0)}")
        print(f"  Knowledge packs: {result.outputs.get('knowledge_packs_indexed', 0)}")

        self.assertEqual(result.status, "active", "Knowledge core not active")
        print("  ✓ Knowledge core operational")


class TestOrchestratorCycle(unittest.TestCase):
    """Test full orchestrator cycle."""

    def test_orchestrator_cycle_successful(self):
        """Verify orchestrator completes cycle with active subsystems."""
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import AmosMasterOrchestrator

        orchestrator = AmosMasterOrchestrator()

        # Initialize the orchestrator
        initialized = orchestrator.initialize()
        self.assertTrue(initialized, "Orchestrator failed to initialize")

        print("  Orchestrator initialized")
        print(f"  Subsystems: {len(orchestrator.state.active_subsystems)}")

        # Run one cycle
        results = orchestrator.run_cycle()

        print("  Cycle completed")
        print(f"  Cycle count: {orchestrator.state.cycle_count}")
        print(f"  Subsystem results: {len(results)}")

        # Check results
        active_count = sum(1 for r in results if r.status == "active")

        print(f"  Active subsystems: {active_count}/{len(results)}")

        self.assertGreaterEqual(active_count, 10, f"Only {active_count} subsystems active")
        print("  ✓ Orchestrator cycle successful")


def main():
    """Run all orchestrator integration tests using unittest."""
    print("=" * 60)
    print("AMOS ORCHESTRATOR INTEGRATION TEST SUITE")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestPrimaryLoopCompleteness,
        TestHandlerMapCoverage,
        TestBrainHandler,
        TestMuscleHandler,
        TestMemoryArchivalHandler,
        TestKnowledgeCoreHandler,
        TestOrchestratorCycle,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

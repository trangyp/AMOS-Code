#!/usr/bin/env python3
"""
AMOS Orchestrator Integration Test
=====================================

Validates the complete 15-subsystem orchestration cycle.
Tests all handlers, bridges, and integrations.

Usage:
  python tests/test_orchestrator_integration.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_primary_loop_completeness():
    """Test that all 15 subsystems are in PRIMARY_LOOP."""
    from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import PRIMARY_LOOP, HANDLER_MAP
    
    print("\n[TEST] Primary Loop Completeness")
    print("-" * 50)
    
    expected_subsystems = [
        "01_BRAIN", "02_SENSES", "03_IMMUNE", "04_BLOOD", "05_SKELETON",
        "08_WORLD_MODEL", "09_SOCIAL_ENGINE", "10_LIFE_ENGINE",
        "11_LEGAL_BRAIN", "12_QUANTUM_LAYER", "13_FACTORY",
        "13_MEMORY_ARCHIVAL", "15_KNOWLEDGE_CORE", "06_MUSCLE", "07_METABOLISM"
    ]
    
    missing = [s for s in expected_subsystems if s not in PRIMARY_LOOP]
    extra = [s for s in PRIMARY_LOOP if s not in expected_subsystems]
    
    print(f"  Expected: {len(expected_subsystems)} subsystems")
    print(f"  In loop: {len(PRIMARY_LOOP)} subsystems")
    print(f"  Handlers: {len(HANDLER_MAP)} registered")
    
    if missing:
        print(f"  ✗ Missing: {missing}")
        return False
    if extra:
        print(f"  ! Extra: {extra}")
    
    print(f"  ✓ All subsystems present")
    return True


def test_handler_map_coverage():
    """Test that all subsystems have handlers."""
    from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import HANDLER_MAP, PRIMARY_LOOP
    
    print("\n[TEST] Handler Map Coverage")
    print("-" * 50)
    
    missing_handlers = [s for s in PRIMARY_LOOP if s not in HANDLER_MAP]
    
    if missing_handlers:
        print(f"  ✗ Missing handlers: {missing_handlers}")
        return False
    
    print(f"  ✓ All {len(PRIMARY_LOOP)} subsystems have handlers")
    
    # Check specific handlers exist
    critical_handlers = [
        "01_BRAIN", "06_MUSCLE", "03_IMMUNE", 
        "13_MEMORY_ARCHIVAL", "15_KNOWLEDGE_CORE"
    ]
    
    for handler in critical_handlers:
        if handler in HANDLER_MAP:
            print(f"    ✓ {handler} handler registered")
        else:
            print(f"    ✗ {handler} handler MISSING")
            return False
    
    return True


def test_brain_handler_with_bridges():
    """Test BrainHandler with bridge integrations."""
    print("\n[TEST] Brain Handler with Bridges")
    print("-" * 50)
    
    try:
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import BrainHandler
        
        handler = BrainHandler("01_BRAIN", {"kernel_refs": []})
        
        # Check bridge initialization capability
        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "pending_tasks": []}
        
        result = handler.process(context)
        
        print(f"  Status: {result.status}")
        print(f"  Actions: {len(result.actions)}")
        print(f"  Cognitive engines: {result.outputs.get('cognitive_engines_loaded', 0)}")
        print(f"  Bridge operational: {result.outputs.get('bridge_operational', False)}")
        print(f"  Tasks routed: {result.outputs.get('tasks_routed', 0)}")
        
        if result.status == "active":
            print("  ✓ Brain handler operational")
            return True
        else:
            print("  ✗ Brain handler not active")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_muscle_handler_with_bridge():
    """Test MuscleHandler with Brain-Muscle Bridge."""
    print("\n[TEST] Muscle Handler with Brain-Muscle Bridge")
    print("-" * 50)
    
    try:
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import MuscleHandler
        
        handler = MuscleHandler("06_MUSCLE", {})
        
        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "pending_tasks": []}
        
        result = handler.process(context)
        
        print(f"  Status: {result.status}")
        print(f"  Bridge operational: {result.outputs.get('bridge_operational', False)}")
        print(f"  Optimization enabled: {result.outputs.get('optimization_enabled', False)}")
        print(f"  Execution plan steps: {result.outputs.get('execution_plan_steps', 0)}")
        
        if result.status == "active":
            print("  ✓ Muscle handler operational")
            return True
        else:
            print("  ✗ Muscle handler not active")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_memory_archival_handler():
    """Test MemoryArchivalHandler integration."""
    print("\n[TEST] Memory Archival Handler")
    print("-" * 50)
    
    try:
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import MemoryArchivalHandler
        
        handler = MemoryArchivalHandler("13_MEMORY_ARCHIVAL", {})
        
        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root, "cycle_results": []}
        
        result = handler.process(context)
        
        print(f"  Status: {result.status}")
        print(f"  Actions: {len(result.actions)}")
        print(f"  Archived count: {result.outputs.get('archived_count', 0)}")
        
        if result.status == "active":
            print("  ✓ Memory archival operational")
            return True
        else:
            print("  ✗ Memory archival not active")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_knowledge_core_handler():
    """Test KnowledgeCoreHandler integration."""
    print("\n[TEST] Knowledge Core Handler")
    print("-" * 50)
    
    try:
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import KnowledgeCoreHandler
        
        handler = KnowledgeCoreHandler("15_KNOWLEDGE_CORE", {})
        
        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        context = {"organism_root": organism_root}
        
        result = handler.process(context)
        
        print(f"  Status: {result.status}")
        print(f"  Features discovered: {result.outputs.get('features_discovered', 0)}")
        print(f"  Engines cataloged: {result.outputs.get('engines_cataloged', 0)}")
        print(f"  Knowledge packs: {result.outputs.get('knowledge_packs_indexed', 0)}")
        
        if result.status == "active":
            print("  ✓ Knowledge core operational")
            return True
        else:
            print("  ✗ Knowledge core not active")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_orchestrator_cycle():
    """Test full orchestrator cycle."""
    print("\n[TEST] Full Orchestrator Cycle")
    print("-" * 50)
    
    try:
        from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import AMOSOrchestrator
        
        organism_root = Path(__file__).parent.parent / "AMOS_ORGANISM_OS"
        orchestrator = AMOSOrchestrator(organism_root)
        
        print(f"  Orchestrator initialized")
        print(f"  Subsystems: {len(orchestrator.subsystems)}")
        
        # Run one cycle
        context = orchestrator.cycle()
        
        print(f"  Cycle completed")
        print(f"  Cycle count: {context.get('cycle_count', 0)}")
        print(f"  Subsystem results: {len(context.get('results', []))}")
        
        # Check results
        results = context.get('results', [])
        active_count = sum(1 for r in results if r.get('status') == 'active')
        
        print(f"  Active subsystems: {active_count}/{len(results)}")
        
        if active_count >= 10:  # At least 10 should be active
            print("  ✓ Orchestrator cycle successful")
            return True
        else:
            print(f"  ! Only {active_count} subsystems active")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all orchestrator integration tests."""
    print("=" * 60)
    print("AMOS ORCHESTRATOR INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Primary Loop Completeness", test_primary_loop_completeness),
        ("Handler Map Coverage", test_handler_map_coverage),
        ("Brain Handler with Bridges", test_brain_handler_with_bridges),
        ("Muscle Handler with Bridge", test_muscle_handler_with_bridge),
        ("Memory Archival Handler", test_memory_archival_handler),
        ("Knowledge Core Handler", test_knowledge_core_handler),
        ("Full Orchestrator Cycle", test_orchestrator_cycle),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name}: EXCEPTION - {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✓ PASS" if p else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED - Orchestrator fully operational!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

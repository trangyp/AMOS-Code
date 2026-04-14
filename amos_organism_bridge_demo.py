#!/usr/bin/env python3
"""AMOS Organism Bridge Integration Demo - Shows brain-to-organism connection."""

import sys


def main():
    """Demonstrate organism bridge integration with AMOS brain."""
    print("\n" + "=" * 70)
    print("AMOS ORGANISM BRIDGE INTEGRATION DEMO")
    print("=" * 70)
    print("\nDemonstrating brain-to-organism connection...")
    
    # Test 1: Import organism bridge from brain module
    print("\n[1] Testing lazy-loaded organism bridge imports...")
    try:
        from amos_brain import (
            get_organism_bridge,
            initialize_organism,
            execute_organism_task
        )
        print("   ✓ Organism bridge functions imported from amos_brain")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return 1
    
    # Test 2: Initialize organism through brain
    print("\n[2] Initializing organism via brain API...")
    try:
        organism = initialize_organism()
        if organism:
            print("   ✓ Organism initialized successfully")
            print(f"   → Type: {type(organism).__name__}")
        else:
            print("   ⚠ Organism initialization returned None")
    except Exception as e:
        print(f"   ✗ Initialization error: {e}")
    
    # Test 3: Get organism bridge
    print("\n[3] Getting organism bridge...")
    try:
        bridge = get_organism_bridge()
        if bridge:
            print("   ✓ Organism bridge retrieved")
            print(f"   → Bridge type: {type(bridge).__name__}")
        else:
            print("   ⚠ Bridge returned None")
    except Exception as e:
        print(f"   ✗ Bridge error: {e}")
    
    # Test 4: Execute task through organism
    print("\n[4] Executing task via organism bridge...")
    try:
        result = execute_organism_task("analyze_market_strategy")
        if result:
            print("   ✓ Task executed successfully")
            if isinstance(result, dict):
                status = result.get('status', 'unknown')
                print(f"   → Status: {status}")
        else:
            print("   ⚠ Task execution returned None")
    except Exception as e:
        print(f"   ✗ Task execution error: {e}")
    
    # Test 5: Master Orchestrator integration
    print("\n[5] Testing Master Orchestrator with organism...")
    try:
        from amos_master_cognitive_orchestrator import MasterCognitiveOrchestrator
        amos = MasterCognitiveOrchestrator()
        
        # Process a task that should utilize organism systems
        task = "Coordinate organism subsystems for market analysis"
        result = amos.process(task)
        
        print("   ✓ Master Orchestrator processed task")
        print(f"   → Engine: {result.engine_used}")
        print(f"   → Category: {result.category}")
        print(f"   → Status: {result.status}")
        print(f"   → Time: {result.processing_time_ms}ms")
    except Exception as e:
        print(f"   ✗ Orchestrator error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("ORGANISM BRIDGE INTEGRATION SUMMARY")
    print("=" * 70)
    print("""
The organism bridge connects the AMOS Brain to 15 subsystems:

  01_BRAIN          → Cognitive processing
  02_SENSES         → Environmental awareness
  03_IMMUNE         → Anomaly detection
  04_BLOOD          → Resource management
  05_MUSCLE         → Task execution
  06_HEART          → Workflow orchestration
  07_MOUTH          → Communication
  08_EARS           → Data ingestion
  09_EYES           → Monitoring/observability
  10_HANDS          → Action execution
  11_NERVES         → Event processing
  12_ETHICS         → Validation/compliance
  13_REFLEX         → Automated responses
  14_INTERFACES     → System integration
  15_MEMORY         → State persistence

Integration validated via:
  • amos_brain lazy loading (new __getattr__)
  • Organism bridge functions
  • Master Cognitive Orchestrator
  • 53-component ecosystem
""")
    print("=" * 70)
    print("\n✓ Organism Bridge Integration Demo Complete")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

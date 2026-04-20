#!/usr/bin/env python3
"""AMOS ONE-CLICK ORCHESTRATOR
==========================

Master entry point for the AMOS 7-System Organism.
Single command to initialize, run, and benchmark the entire system.

Owner: Trang
Version: 1.0.0
Python: 3.9+

Usage:
    python AMOS_ONECLICK_ORCHESTRATOR.py

This performs:
    1. Registry loading
    2. Full system initialization
    3. Primary loop execution
    4. Speed benchmarking
    5. State persistence
"""

import json
import sys
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC

# Import AMOS components
from AMOS_MASTER_ORCHESTRATOR import (
    LOGS_DIR,
    MEMORY_DIR,
    ORGANISM_ROOT,
    AmosMasterOrchestrator,
)
from AMOS_SPEED_ENGINE import AmosSpeedEngine


def run_full_pipeline() -> int:
    """Execute the complete AMOS pipeline."""
    print("\n" + "=" * 70)
    print("AMOS 7-SYSTEM ORGANISM - ONE CLICK ORCHESTRATOR")
    print("=" * 70)
    print(f"Timestamp: {datetime.now(UTC).isoformat()}Z")
    print(f"Organism Root: {ORGANISM_ROOT}")
    print("=" * 70)

    # ========================================================================
    # PHASE 1: Initialize Master Orchestrator
    # ========================================================================
    print("\n[PHASE 1] Initializing Master Orchestrator...")

    orchestrator = AmosMasterOrchestrator()
    if not orchestrator.initialize():
        print("[ERROR] Initialization failed!")
        return 1

    status = orchestrator.get_status()
    print(f"[OK] Loaded {len(status['active_subsystems'])} active subsystems")

    # ========================================================================
    # PHASE 2: Execute Primary Cognitive Loop
    # ========================================================================
    print("\n[PHASE 2] Executing Primary Cognitive Loop...")

    results = orchestrator.run_cycle()
    print(f"[OK] Processed {len(results)} subsystems in primary loop")

    # ========================================================================
    # PHASE 3: Speed Benchmarking
    # ========================================================================
    print("\n[PHASE 3] Running Speed Benchmarks...")

    speed_engine = AmosSpeedEngine(ORGANISM_ROOT)
    speed_engine.benchmark_registry_load()
    profile = speed_engine.generate_profile()
    speed_path = speed_engine.save_profile()

    print(f"[OK] Speed profile generated: {profile.overall_score}/100")
    print(f"[OK] Speed profile saved: {speed_path}")

    # ========================================================================
    # PHASE 4: State Persistence
    # ========================================================================
    print("\n[PHASE 4] Persisting System State...")

    final_status = orchestrator.get_status()

    # Save comprehensive state
    state_record = {
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "pipeline": "one_click_orchestrator",
        "version": "1.0.0",
        "status": final_status,
        "speed_profile": {
            "score": profile.overall_score,
            "benchmarks_run": len(profile.benchmarks),
        },
        "subsystems_processed": len(results),
    }

    state_path = MEMORY_DIR / "pipeline_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state_record, f, indent=2)

    print(f"[OK] State saved to: {state_path}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"Cycles Completed:     {final_status['cycle_count']}")
    print(f"Active Subsystems:    {len(final_status['active_subsystems'])}")
    print(f"Cycle Time:           {final_status['last_cycle_time']:.3f}s")
    print(f"Speed Score:          {profile.overall_score}/100")
    print(f"Errors:               {final_status['error_count']}")
    print("=" * 70)

    print("\n[AMOS] Organism is operational.")
    print(f"[AMOS] Logs: {LOGS_DIR}")
    print(f"[AMOS] Memory: {MEMORY_DIR}")

    return 0


def main() -> int:
    """Main entry point with error handling."""
    try:
        return run_full_pipeline()
    except KeyboardInterrupt:
        print("\n[AMOS] Interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n[AMOS] [FATAL ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

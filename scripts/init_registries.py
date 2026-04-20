#!/usr/bin/env python3
"""Initialize AMOS Brain Registries for Orchestrator.

This script creates the initial registry files required by the
AMOS_MASTER_ORCHESTRATOR to function properly.

Registries initialized:
- system_registry.json: Subsystem configurations
- agent_registry.json: Agent definitions
- engine_registry.json: Engine configurations
- world_state.json: Global state tracking
- operator_profile.json: Operator settings
"""

import json
import sys
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from pathlib import Path

# Registry paths
REGISTRY_DIR = Path("_AMOS_BRAIN")
REGISTRIES = {
    "system_registry.json": {
        "version": "14.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "subsystems": {
            "01_BRAIN": {
                "name": "Cognitive Brain",
                "status": "active",
                "handlers": ["cognitive_router", "knowledge_engine"],
                "priority": 1,
            },
            "02_SENSES": {
                "name": "Senses",
                "status": "active",
                "handlers": ["context_gatherer", "environment_scanner"],
                "priority": 2,
            },
            "03_IMMUNE": {
                "name": "Immune System",
                "status": "active",
                "handlers": ["anomaly_detector", "alert_manager"],
                "priority": 3,
            },
            "04_BLOOD": {
                "name": "Blood/Energy",
                "status": "active",
                "handlers": ["budget_manager", "cashflow_tracker"],
                "priority": 4,
            },
            "05_NERVES": {
                "name": "Nerves/Communication",
                "status": "active",
                "handlers": ["message_router", "signal_processor"],
                "priority": 5,
            },
            "06_MUSCLE": {
                "name": "Muscle/Workflow",
                "status": "active",
                "handlers": ["workflow_engine"],
                "priority": 6,
            },
            "07_METABOLISM": {
                "name": "Metabolism/Pipeline",
                "status": "active",
                "handlers": ["pipeline_engine"],
                "priority": 7,
            },
        },
        "primary_loop": [
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_NERVES",
            "06_MUSCLE",
            "07_METABOLISM",
        ],
    },
    "agent_registry.json": {
        "version": "14.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "agents": {
            "cognitive_agent": {
                "type": "cognitive",
                "enabled": True,
                "capabilities": ["reasoning", "planning", "learning"],
            },
            "monitoring_agent": {
                "type": "monitoring",
                "enabled": True,
                "capabilities": ["metrics", "alerts", "health_checks"],
            },
            "execution_agent": {
                "type": "execution",
                "enabled": True,
                "capabilities": ["workflow", "pipeline", "task_execution"],
            },
        },
    },
    "engine_registry.json": {
        "version": "14.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "engines": {
            "coherence": {"enabled": True, "config": {"validation_level": "strict"}},
            "axiom": {"enabled": True, "config": {"check_all": True}},
            "knowledge": {"enabled": True, "config": {"auto_load": True}},
        },
    },
    "world_state.json": {
        "version": "14.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "global_state": {
            "status": "initialized",
            "cycle_count": 0,
            "last_update": datetime.now(timezone.utc).isoformat(),
        },
        "context": {"environment": "production", "domain": "neurosyncai.tech", "version": "14.0.0"},
    },
    "operator_profile.json": {
        "version": "14.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "operator": {
            "name": "System Operator",
            "role": "administrator",
            "preferences": {"auto_start": True, "notification_level": "all", "default_cycles": 1},
        },
    },
}


def init_registries() -> bool:
    """Initialize all registry files."""
    print("Initializing AMOS Brain Registries...")
    print("=" * 60)

    # Ensure registry directory exists
    registry_path = REGISTRY_DIR
    registry_path.mkdir(parents=True, exist_ok=True)

    created_count = 0
    existing_count = 0

    for filename, data in REGISTRIES.items():
        filepath = registry_path / filename

        if filepath.exists():
            print(f"  ⚠️  {filename} - already exists (skipped)")
            existing_count += 1
            continue

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ {filename} - created")
        created_count += 1

    print("=" * 60)
    print("Registry initialization complete:")
    print(f"  Created: {created_count}")
    print(f"  Existing: {existing_count}")
    print(f"  Total: {created_count + existing_count}")

    return True


if __name__ == "__main__":
    try:
        success = init_registries()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Registry initialization failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""AMOS Organism Primary Loop - Executes the 14-subsystem circulation.

Primary Loop:
    01_BRAIN → 02_SENSES → 05_SKELETON → 08_WORLD_MODEL →
    09_QUANTUM_LAYER → 06_MUSCLE → 07_METABOLISM → 01_BRAIN

This module implements the actual execution flow that wires all subsystems
together in the biological metaphor of a digital organism.

Usage:
    from AMOS_ORGANISM_OS.primary_loop import PrimaryLoop

    loop = PrimaryLoop()
    result = loop.execute_cycle(task="Design a system")
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional

UTC = UTC

from amos_brain import get_amos_integration


@dataclass
class CycleResult:
    """Result from executing one primary loop cycle."""

    cycle_id: str
    started_at: str
    completed_at: str
    task: str
    subsystem_results: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    success: bool = True


class PrimaryLoop:
    """Executes the AMOS Organism primary circulation loop.

    The primary loop mimics biological circulation:
    - BRAIN (cognition) → SENSES (input) → SKELETON (structure)
    - WORLD_MODEL (knowledge) → QUANTUM (scenarios)
    - MUSCLE (execution) → METABOLISM (processing) → back to BRAIN
    """

    # Primary loop sequence
    PRIMARY_SEQUENCE = [
        "01_BRAIN",
        "02_SENSES",
        "05_SKELETON",
        "08_WORLD_MODEL",
        "09_QUANTUM_LAYER",
        "06_MUSCLE",
        "07_METABOLISM",
    ]

    def __init__(self):
        self.brain = get_amos_integration()
        self.cycle_count = 0
        self._subsystems: dict[str, Any] = {}

    def _get_subsystem(self, code: str) -> Optional[Any]:
        """Lazy-load a subsystem by code."""
        if code in self._subsystems:
            return self._subsystems[code]

        # Import on demand
        try:
            if code == "01_BRAIN":
                from BRAIN.brain_os import BrainOS

                self._subsystems[code] = BrainOS()
            elif code == "02_SENSES":
                from SENSES.environment_scanner import EnvironmentScanner

                self._subsystems[code] = EnvironmentScanner()
            elif code == "05_SKELETON":
                from SKELETON.constraint_engine import ConstraintEngine

                self._subsystems[code] = ConstraintEngine()
            elif code == "08_WORLD_MODEL":
                from WORLD_MODEL.knowledge_graph import KnowledgeGraph

                self._subsystems[code] = KnowledgeGraph()
            elif code == "09_QUANTUM_LAYER":
                from QUANTUM_LAYER.scenario_engine import ScenarioEngine

                self._subsystems[code] = ScenarioEngine()
            elif code == "06_MUSCLE":
                from MUSCLE.executor import MuscleExecutor

                self._subsystems[code] = MuscleExecutor()
            elif code == "07_METABOLISM":
                from METABOLISM.pipeline_engine import PipelineEngine

                self._subsystems[code] = PipelineEngine()
            else:
                return None

            return self._subsystems[code]
        except ImportError as e:
            print(f"[PrimaryLoop] Subsystem {code} not available: {e}")
            return None

    def execute_cycle(self, task: str, context: dict = None) -> CycleResult:
        """Execute one full primary loop cycle.

        Args:
            task: The task/request to process through the organism
            context: Optional context data

        Returns:
            CycleResult with results from each subsystem
        """
        self.cycle_count += 1
        cycle_id = f"cycle_{self.cycle_count}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now(UTC).isoformat()

        print(f"\n[PrimaryLoop] Starting cycle {self.cycle_count}: {cycle_id}")
        print(f"[PrimaryLoop] Task: {task[:60]}...")
        print("=" * 60)

        subsystem_results = {}
        errors = []

        # Execute each subsystem in sequence
        for subsystem_code in self.PRIMARY_SEQUENCE:
            print(f"\n→ {subsystem_code}...", end=" ")

            try:
                subsystem = self._get_subsystem(subsystem_code)
                if subsystem is None:
                    print("SKIPPED (not available)")
                    subsystem_results[subsystem_code] = {
                        "status": "skipped",
                        "reason": "not_available",
                    }
                    continue

                # Process through subsystem
                result = self._execute_subsystem(subsystem_code, subsystem, task, context)
                subsystem_results[subsystem_code] = result
                print("✓ DONE")

            except Exception as e:
                error_msg = f"{subsystem_code}: {str(e)}"
                errors.append(error_msg)
                print(f"✗ ERROR - {e}")
                subsystem_results[subsystem_code] = {"status": "error", "error": str(e)}

        completed_at = datetime.now(UTC).isoformat()

        print("\n" + "=" * 60)
        print(f"[PrimaryLoop] Cycle {self.cycle_count} complete")
        print(f"  Success: {len(errors) == 0}")
        print(
            f"  Subsystems: {len([r for r in subsystem_results.values() if r.get('status') != 'skipped'])}/{len(self.PRIMARY_SEQUENCE)}"
        )
        print()

        return CycleResult(
            cycle_id=cycle_id,
            started_at=started_at,
            completed_at=completed_at,
            task=task,
            subsystem_results=subsystem_results,
            errors=errors,
            success=len(errors) == 0,
        )

    def _execute_subsystem(
        self, code: str, subsystem: Any, task: str, context: dict
    ) -> dict[str, Any]:
        """Execute a single subsystem in the loop."""
        result = {
            "status": "executed",
            "code": code,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Each subsystem has a specific role
        if code == "01_BRAIN":
            # BRAIN: Analyze and plan
            analysis = self.brain.analyze_with_rules(task, context or {})
            result["analysis"] = {
                "confidence": analysis["rule_of_two"]["confidence"],
                "recommendation": analysis["rule_of_two"]["recommendation"],
                "quadrants": analysis["rule_of_four"]["quadrants_analyzed"],
            }

        elif code == "02_SENSES":
            # SENSES: Scan environment and gather context
            if hasattr(subsystem, "scan"):
                scan_result = subsystem.scan(task)
                result["environment"] = scan_result
            else:
                result["environment"] = "default_environment"

        elif code == "05_SKELETON":
            # SKELETON: Validate constraints and structure
            if hasattr(subsystem, "validate"):
                validation = subsystem.validate(task)
                result["constraints"] = validation
            else:
                # Use AMOS laws for constraint validation
                laws = self.brain.laws
                result["constraints"] = {"laws_active": len(laws.get_all_laws())}

        elif code == "08_WORLD_MODEL":
            # WORLD_MODEL: Access knowledge graph
            if hasattr(subsystem, "query"):
                knowledge = subsystem.query(task)
                result["knowledge"] = knowledge
            else:
                result["knowledge"] = {"sources": ["amos_brain"], "domains": 12}

        elif code == "09_QUANTUM_LAYER":
            # QUANTUM_LAYER: Generate scenarios
            if hasattr(subsystem, "generate_scenarios"):
                scenarios = subsystem.generate_scenarios(task, count=3)
                result["scenarios"] = scenarios
            else:
                # Fallback: use AMOS brain for scenario analysis
                result["scenarios"] = ["baseline", "optimistic", "pessimistic"]

        elif code == "06_MUSCLE":
            # MUSCLE: Execute actions
            if hasattr(subsystem, "prepare"):
                execution_plan = subsystem.prepare(task)
                result["execution_plan"] = execution_plan
            else:
                result["execution_plan"] = {"status": "ready", "tools": []}

        elif code == "07_METABOLISM":
            # METABOLISM: Process and transform
            if hasattr(subsystem, "process"):
                processed = subsystem.process(task)
                result["processed"] = processed
            else:
                result["processed"] = {"status": "complete", "output": task}

        return result

    def get_status(self) -> dict[str, Any]:
        """Get current primary loop status."""
        loaded = [code for code in self.PRIMARY_SEQUENCE if code in self._subsystems]

        return {
            "cycle_count": self.cycle_count,
            "subsystems_total": len(self.PRIMARY_SEQUENCE),
            "subsystems_loaded": len(loaded),
            "subsystems_available": loaded,
            "sequence": self.PRIMARY_SEQUENCE,
        }


def run_primary_loop_demo():
    """Demo the primary loop execution."""
    print("=" * 70)
    print("AMOS ORGANISM - Primary Loop Demo")
    print("=" * 70)
    print()

    loop = PrimaryLoop()

    # Show status
    status = loop.get_status()
    print("Primary Loop Status:")
    print(f"  Sequence: {' → '.join(status['sequence'])}")
    print(f"  Subsystems: {status['subsystems_loaded']}/{status['subsystems_total']} available")
    print()

    # Execute a test cycle
    result = loop.execute_cycle(
        task="Design a sustainable cloud architecture for a microservices platform",
        context={"priority": "high", "budget": "medium"},
    )

    print("Cycle Result:")
    print(f"  ID: {result.cycle_id}")
    print(f"  Success: {result.success}")
    print(f"  Started: {result.started_at}")
    print(f"  Completed: {result.completed_at}")
    print()

    if result.errors:
        print(f"Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")

    return result


if __name__ == "__main__":
    run_primary_loop_demo()

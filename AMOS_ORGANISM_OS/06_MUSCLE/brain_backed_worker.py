#!/usr/bin/env python3
"""AMOS Brain-Backed Worker (06_MUSCLE)
=====================================

Enhanced worker engine that queries the 17MB brain before executing tasks.
Provides intelligent, knowledge-backed task execution.

Owner: Trang
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amos_worker_engine import AmosWorkerEngine, WorkerResult
from brain_worker_bridge import BrainWorkerBridge


class BrainBackedWorker(AmosWorkerEngine):
    """Worker engine enhanced with brain knowledge integration.
    Queries the 17MB brain before executing tasks.
    """

    def __init__(self, organism_root: Path) -> None:
        super().__init__(organism_root)
        self.brain_bridge = BrainWorkerBridge(organism_root)
        self._brain_enabled = True

    def execute_with_brain(self, plan: Dict[str, Any], context: dict = None) -> WorkerResult:
        """Execute a plan with brain knowledge enrichment."""
        print("\n[BRAIN-BACKED] Enriching plan with brain knowledge...")

        # Enrich plan with brain knowledge
        enriched_plan = self.brain_bridge.enrich_plan_with_brain(plan)

        # Show knowledge summary
        knowledge_count = sum(
            1
            for s in enriched_plan.get("steps", [])
            if s.get("brain_knowledge", {}).get("results_count", 0) > 0
        )
        print(f"[BRAIN-BACKED] Enriched {knowledge_count} steps with brain knowledge")

        # Execute enriched plan
        result = self.execute_plan(enriched_plan, context)

        # Add brain metadata
        if result.success:
            result.metadata["brain_enriched"] = True
            result.metadata["knowledge_sources"] = enriched_plan.get("knowledge_sources", [])

        return result

    def generate_with_brain(self, prompt: str, target_file: str = None) -> WorkerResult:
        """Generate code with brain knowledge."""
        print(f"\n[BRAIN-BACKED] Querying brain for: '{prompt[:50]}...'")

        # Query brain for relevant knowledge
        brain_result = self.brain_bridge.query_brain_for_task(prompt)

        if brain_result["results_count"] > 0:
            print(f"[BRAIN-BACKED] Found {brain_result['results_count']} relevant patterns")

            # Use brain knowledge to enhance generation
            top_result = brain_result["top_results"][0]
            print(f"[BRAIN-BACKED] Using guidance from: {top_result['engine']}")

        # Create enhanced plan
        plan = {
            "steps": [
                {
                    "action": "generate_code",
                    "prompt": prompt,
                    "target_file": target_file,
                    "brain_context": brain_result,
                }
            ]
        }

        return self.execute_with_brain(plan)

    def analyze_with_brain(self, topic: str) -> WorkerResult:
        """Analyze topic with brain knowledge."""
        print(f"\n[BRAIN-BACKED] Deep analysis of: '{topic}'")

        # Query brain
        brain_result = self.brain_bridge.query_brain_for_task(topic, max_results=10)

        # Use cognitive runtime if available
        if self.runtime:
            cognitive_result = self.runtime.think(topic, "diagnostic_analysis")

            # Combine with brain knowledge
            combined = {"cognitive_analysis": cognitive_result, "brain_knowledge": brain_result}

            output = json.dumps(combined, indent=2)
        else:
            output = json.dumps(brain_result, indent=2)

        return WorkerResult(
            success=True,
            output=output,
            artifacts=[],
            metadata={"brain_results": brain_result["results_count"], "brain_enriched": True},
        )

    def audit_with_brain(self, target: str, check_brain_alignment: bool = True) -> WorkerResult:
        """Audit with brain validation."""
        print(f"\n[BRAIN-BACKED] Auditing: '{target[:50]}...'")

        # Standard audit via runtime
        if self.runtime:
            audit_result = self.runtime.think(target, "audit_and_critique")
        else:
            audit_result = {"status": "runtime_unavailable"}

        # Check brain alignment if requested
        if check_brain_alignment:
            validation = self.brain_bridge.validate_against_brain(target, "audit")
            audit_result["brain_validation"] = validation

        return WorkerResult(
            success=True,
            output=json.dumps(audit_result, indent=2),
            artifacts=[],
            metadata={"brain_validated": check_brain_alignment},
        )


def main() -> int:
    """CLI for brain-backed worker."""
    print("=" * 60)
    print("AMOS Brain-Backed Worker (06_MUSCLE)")
    print("=" * 60)

    organism_root = Path(__file__).parent.parent
    worker = BrainBackedWorker(organism_root)

    # Test brain query
    print("\n[TEST] Brain-backed analysis...")
    result = worker.analyze_with_brain("cognitive architecture design")

    print(f"\nSuccess: {result.success}")
    print(f"Brain results: {result.metadata.get('brain_results', 0)}")

    # Show sample of output
    output_lines = result.output.split("\n")[:20]
    print("\nOutput preview:")
    for line in output_lines:
        print(line)

    if len(result.output.split("\n")) > 20:
        print("...")

    return 0


if __name__ == "__main__":
    sys.exit(main())

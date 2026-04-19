#!/usr/bin/env python3
"""AMOS Cost-Aware Worker (04_BLOOD Integration)
==============================================

Worker engine enhanced with cost tracking via BLOOD subsystem.
Every task gets budget checked and cost recorded.

Owner: Trang
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "06_MUSCLE"))
sys.path.insert(0, str(Path(__file__).parent))


from amos_worker_engine import AmosWorkerEngine, WorkerResult
from financial_engine import FinancialEngine


class CostAwareWorker(AmosWorkerEngine):
    """Worker with cost awareness via BLOOD subsystem.
    Tracks resource costs for every task.
    """

    def __init__(self, organism_root: Path) -> None:
        super().__init__(organism_root)
        self.blood = FinancialEngine(organism_root)

    def execute_with_budget(
        self, plan: dict[str, Any], context: Optional[dict] = None, budget_category: str = "compute"
    ) -> WorkerResult:
        """Execute plan with cost tracking."""
        # Check budget before execution
        budget_status = self.blood.get_budget_status(budget_category)
        if budget_status and budget_status["remaining"] <= 0:
            return WorkerResult(
                success=False,
                output=f"Budget exhausted for {budget_category}",
                artifacts=[],
                metadata={"budget_exhausted": True, "category": budget_category},
            )

        # Estimate costs
        steps = plan.get("steps", [])
        total_estimate = 0.0
        for step in steps:
            complexity = step.get("complexity", "medium")
            estimate = self.blood.estimate_task_cost(complexity=complexity, duration_minutes=5.0)
            total_estimate += estimate["estimated_cost"]

        # Check if estimate fits budget
        if budget_status:
            if total_estimate > budget_status["remaining"]:
                return WorkerResult(
                    success=False,
                    output=f"Estimated cost ${total_estimate:.4f} exceeds budget",
                    artifacts=[],
                    metadata={
                        "over_budget": True,
                        "estimate": total_estimate,
                        "remaining": budget_status["remaining"],
                    },
                )

        # Allocate resources
        task_id = plan.get("task_id", "unknown_task")
        allocation = self.blood.allocate_resources(
            task_id=task_id,
            cpu_units=len(steps) * 1.0,
            memory_mb=len(steps) * 512.0,
            priority=plan.get("priority", 5),
        )

        print(f"[BLOOD] Allocated: ${allocation.cost_estimate:.4f} est")

        # Execute the plan
        result = self.execute_plan(plan, context)

        # Record actual cost
        actual_cost = self.blood.release_resources(task_id)
        if actual_cost:
            print(f"[BLOOD] Recorded actual cost: ${actual_cost:.4f}")

        # Add cost metadata
        result.metadata["cost_estimate"] = allocation.cost_estimate
        result.metadata["actual_cost"] = actual_cost
        result.metadata["budget_category"] = budget_category

        return result

    def get_financial_status(self) -> dict[str, Any]:
        """Get financial status from BLOOD."""
        return self.blood.get_status()


def main() -> int:
    """CLI for cost-aware worker."""
    print("=" * 50)
    print("AMOS Cost-Aware Worker (04_BLOOD)")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    worker = CostAwareWorker(organism_root)

    # Test plan
    plan = {
        "task_id": "cost_test_001",
        "priority": 5,
        "steps": [
            {
                "action": "write_file",
                "target_file": "test_output/cost_test.txt",
                "content": "Cost-aware test output",
                "complexity": "low",
            }
        ],
    }

    print("\nExecuting cost-aware plan...")
    result = worker.execute_with_budget(plan, budget_category="compute")

    print(f"\nSuccess: {result.success}")
    print(f"Cost estimate: ${result.metadata.get('cost_estimate', 0):.4f}")
    print(f"Actual cost: ${result.metadata.get('actual_cost', 0):.4f}")

    # Show financial status
    print("\nFinancial Status:")
    status = worker.get_financial_status()
    print(f"  Active allocations: {status['active_allocations']}")
    print(f"  Total transactions: {status['total_transactions']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

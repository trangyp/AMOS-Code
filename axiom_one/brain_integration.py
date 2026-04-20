#!/usr/bin/env python3
"""AXIOM One Brain Integration - Cognitive Execution Layer

Integrates AMOS Brain (SuperBrain, CognitiveEngine, KernelRouter) with AXIOM One ExecutionSlots.

This provides:
- Brain-powered task decomposition (Planner uses CognitiveEngine)
- Intelligent routing to AMOS engines via KernelRouter
- Law-compliant execution through ActionGate
- Real-time verification via repo_doctor

Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .execution_slot import ExecutionSlot, SlotMode, SlotStatus
from .ledger import Ledger
from .swarm import AgentRole, SubTask, TaskDAG
from .twin import Twin


@dataclass
class BrainExecutionConfig:
    """Configuration for brain-powered execution."""

    repo_path: Path = field(default_factory=Path.cwd)
    enable_cognitive_planning: bool = True
    enable_law_compliance: bool = True
    enable_repo_doctor: bool = True
    max_parallel_workers: int = 4


class BrainPoweredOrchestrator:
    """
    AXIOM One orchestrator with AMOS Brain integration.

    Combines:
    - ExecutionSlot primitives (reproducible, verifiable)
    - AMOS Brain cognitive capabilities (decomposition, routing)
    - SuperBrain execution (LAW 0 compliant)
    - repo_doctor verification (invariant checking)
    """

    def __init__(self, config: Optional[BrainExecutionConfig] = None):
        self.config = config or BrainExecutionConfig()
        self._slots: dict[str, ExecutionSlot] = {}
        self._twin = Twin(self.config.repo_path)
        self._ledger = Ledger()

        # Lazy-loaded brain components
        self._brain = None
        self._cognitive_engine = None
        self._kernel_router = None
        self._repo_doctor = None

    def _get_brain(self):
        """Lazy-load SuperBrain."""
        if self._brain is None:
            from amos_brain import get_super_brain

            self._brain = get_super_brain()
        return self._brain

    def _get_cognitive_engine(self):
        """Lazy-load CognitiveEngine."""
        if self._cognitive_engine is None:
            from amos_brain.cognitive_engine import get_cognitive_engine

            self._cognitive_engine = get_cognitive_engine()
        return self._cognitive_engine

    def _get_kernel_router(self):
        """Lazy-load KernelRouter."""
        if self._kernel_router is None:
            from amos_brain import KernelRouter
            from amos_brain.loader import get_brain

            brain = get_brain()
            self._kernel_router = KernelRouter(brain)
        return self._kernel_router

    def _get_repo_doctor(self):
        """Lazy-load repo_doctor."""
        if self._repo_doctor is None:
            try:
                from repo_doctor import RepoDoctor

                self._repo_doctor = RepoDoctor(self.config.repo_path)
            except ImportError:
                pass
        return self._repo_doctor

    def execute_intelligent(
        self,
        objective: str,
        mode: SlotMode = SlotMode.LOCAL,
        context: Optional[dict[str, Any]] = None,
    ) -> ExecutionSlot:
        """
        Execute with full brain integration.

        Args:
            objective: Task description
            mode: Execution mode (LOCAL/MANAGED/ORCHESTRATION)
            context: Additional execution context

        Returns:
            ExecutionSlot with full audit trail
        """
        # 1. Capture pre-state via Twin
        pre_state = self._twin.capture_state("pre_execution")

        # 2. Create execution slot
        slot = ExecutionSlot.create_local(
            objective=objective,
            repo_path=self.config.repo_path,
        )
        slot.mode = mode
        slot.status = SlotStatus.RUNNING
        self._slots[slot.slot_id] = slot

        slot.log_event("execution_started", mode=mode.value, objective=objective)

        try:
            # 3. Cognitive Planning (if enabled)
            if self.config.enable_cognitive_planning and mode == SlotMode.ORCHESTRATION:
                dag = self._plan_with_brain(objective, slot)
                slot.log_event("planning_complete", tasks=len(dag.tasks))

            # 4. Route to appropriate engines via KernelRouter
            router = self._get_kernel_router()
            engines = router.route(objective)
            slot.log_event("routing_complete", engines=[e["id"] for e in engines])

            # 5. Execute via SuperBrain (LAW 0 compliant)
            brain = self._get_brain()
            if brain and hasattr(brain, "execute_task"):
                result = brain.execute_task(objective, context)
                slot.log_event("brain_execution", success=result.get("success", False))

                if not result.get("success", False):
                    slot.status = SlotStatus.FAILED
                    slot.failure_reason = result.get("error", "Unknown error")
                else:
                    slot.status = SlotStatus.COMPLETED

            # 6. repo_doctor verification (if enabled)
            if self.config.enable_repo_doctor:
                self._verify_with_repo_doctor(slot)

        except Exception as e:
            slot.status = SlotStatus.FAILED
            slot.failure_reason = str(e)
            slot.log_event("execution_error", error=str(e))

        # 7. Capture post-state
        post_state = self._twin.capture_state("post_execution")

        # 8. Create ledger receipt
        receipt = self._ledger.create_receipt(
            slot_id=slot.slot_id,
            objective=slot.objective,
            actions=[{"type": "brain_execution", "objective": objective}],
        )
        slot.verification_bundle = {
            "receipt_id": receipt.receipt_id,
            "timestamp": receipt.timestamp,
            "pre_state": pre_state.compute_signature() if pre_state else None,
            "post_state": post_state.compute_signature() if post_state else None,
        }

        return slot

    def _plan_with_brain(self, objective: str, parent_slot: ExecutionSlot) -> TaskDAG:
        """Use CognitiveEngine to decompose task into DAG."""
        cognitive = self._get_cognitive_engine()

        # Get cognitive analysis
        result = cognitive.process(
            query=f"Decompose this task into subtasks: {objective}",
            domain="software",
            context={"objective": objective},
        )

        # Parse result into DAG
        dag = TaskDAG()

        # Add planner task
        dag.add_task(
            SubTask(
                task_id="planner",
                description=f"Plan: {objective}",
                role=AgentRole.PLANNER,
            )
        )

        # Parse cognitive output for subtasks (simplified)
        lines = result.content.split("\n")
        task_id = 0
        for line in lines:
            if line.strip().startswith(("-", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                task_id += 1
                dag.add_task(
                    SubTask(
                        task_id=f"worker_{task_id}",
                        description=line.strip().lstrip("- 123456789."),
                        role=AgentRole.WORKER,
                        dependencies=["planner"],
                    )
                )

        # Add verification
        if task_id > 0:
            dag.add_task(
                SubTask(
                    task_id="verifier",
                    description="Verify all work",
                    role=AgentRole.VERIFIER,
                    dependencies=[f"worker_{i}" for i in range(1, task_id + 1)],
                )
            )

        return dag

    def _verify_with_repo_doctor(self, slot: ExecutionSlot) -> dict[str, Any]:
        """Run repo_doctor verification on slot."""
        doctor = self._get_repo_doctor()
        if not doctor:
            return {"verified": False, "error": "repo_doctor not available"}

        try:
            # Run invariant checks
            result = doctor.check_invariants()
            slot.log_event("repo_doctor_verification", passed=result.get("passed", False))
            return result
        except Exception as e:
            slot.log_event("repo_doctor_error", error=str(e))
            return {"verified": False, "error": str(e)}

    def get_slot(self, slot_id: str) -> Optional[ExecutionSlot]:
        """Get slot by ID."""
        return self._slots.get(slot_id)

    def list_active_slots(self) -> list[ExecutionSlot]:
        """List all active slots."""
        return [
            slot
            for slot in self._slots.values()
            if slot.status in (SlotStatus.ALLOCATED, SlotStatus.RUNNING, SlotStatus.PAUSED)
        ]


def main():
    """CLI for brain-powered orchestration."""
    import argparse

    parser = argparse.ArgumentParser(description="AXIOM One Brain Integration")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--mode", choices=["local", "managed", "orch"], default="local")
    parser.add_argument("--execute", required=True, help="Objective to execute")

    args = parser.parse_args()

    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
    }

    config = BrainExecutionConfig(repo_path=args.repo)
    orchestrator = BrainPoweredOrchestrator(config)

    slot = orchestrator.execute_intelligent(objective=args.execute, mode=mode_map[args.mode])

    print(f"Slot ID: {slot.slot_id}")
    print(f"Status: {slot.status.value}")
    print(f"Events: {len(slot.event_log)}")
    if slot.verification_bundle:
        print(f"Receipt: {slot.verification_bundle.get('receipt_id')}")


if __name__ == "__main__":
    main()

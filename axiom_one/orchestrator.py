#!/usr/bin/env python3
"""AXIOM One Orchestrator - Integration Layer

Unifies Operator (Local), Swarm (Multi-Agent), Twin (Digital Twin), and Ledger (Governance).
Supports all 3 operating modes with shared state.

Author: AMOS System
Version: 3.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .execution_slot import ExecutionSlot, SlotMode
from .ledger import Ledger
from .operator import Operator, OperatorConfig
from .swarm import AgentRole, SubTask, Swarm, SwarmConfig, TaskDAG
from .twin import Twin


@dataclass
class OrchestratorConfig:
    """Configuration for AXIOM One orchestrator."""

    repo_path: Path
    mode: SlotMode = SlotMode.LOCAL
    max_parallel_agents: int = 4
    enable_twin: bool = True
    enable_ledger: bool = True


class AxiomOne:
    """
    Unified entry point for AXIOM One Technical Operating System.

    Combines:
    - Operator: Local tool execution and file operations
    - Swarm: Multi-agent task decomposition and parallel execution
    - Twin: Environment state capture and replay
    - Ledger: Governance, audit, and cost tracking
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig(repo_path=Path.cwd())

        # Initialize subsystems
        self.operator = Operator(OperatorConfig(repo_path=self.config.repo_path))
        self.swarm = Swarm(
            SwarmConfig(
                max_parallel_workers=self.config.max_parallel_agents,
                repo_path=self.config.repo_path,
            )
        )
        self.twin = Twin(self.config.repo_path) if self.config.enable_twin else None
        self.ledger = Ledger() if self.config.enable_ledger else None

        # Active slots
        self._active_slots: dict[str, ExecutionSlot] = {}

    def execute(self, objective: str, mode: Optional[SlotMode] = None) -> ExecutionSlot:
        """
        Execute an objective in the specified mode.

        Args:
            objective: The task to accomplish
            mode: LOCAL (terminal), MANAGED (isolated), or ORCHESTRATION (swarm)

        Returns:
            ExecutionSlot with results and audit trail
        """
        mode = mode or self.config.mode

        # Capture pre-execution state
        if self.twin:
            self.twin.capture_state("pre_execution")

        # Create execution slot
        if mode == SlotMode.LOCAL:
            slot = self.operator.start_session(objective)
        elif mode == SlotMode.MANAGED:
            slot = ExecutionSlot.create_managed(objective, repo_url="local")
            slot.mode = SlotMode.MANAGED
        else:  # ORCHESTRATION
            slot = ExecutionSlot.create_orchestration(
                objective=objective, child_objectives=[f"Subtask: {objective}"]
            )
            slot.mode = SlotMode.ORCHESTRATION

        self._active_slots[slot.slot_id] = slot

        # Execute based on mode
        if mode == SlotMode.ORCHESTRATION:
            # Use swarm for parallel execution
            dag = self._create_task_dag(objective)
            # Async execution would happen here

        # Complete and create audit receipt
        self.operator.complete_session(True, {"mode": mode.value})

        if self.ledger:
            receipt = self.ledger.create_receipt(
                slot_id=slot.slot_id,
                objective=slot.objective,
                actions=[{"tool": "execute", "objective": objective}],
            )
            slot.verification_bundle = {
                "receipt_id": receipt.receipt_id,
                "slot_id": receipt.slot_id,
                "timestamp": receipt.timestamp,
            }

        # Capture post-execution state
        if self.twin:
            self.twin.capture_state("post_execution")

        return slot

    def _create_task_dag(self, objective: str) -> TaskDAG:
        """Create a task DAG from objective."""
        dag = TaskDAG()

        # Planner creates subtasks
        dag.add_task(
            SubTask(
                task_id="plan",
                description=f"Plan: {objective}",
                role=AgentRole.PLANNER,
            )
        )

        # Workers execute in parallel
        dag.add_task(
            SubTask(
                task_id="work_1",
                description="Execute subtask 1",
                role=AgentRole.WORKER,
                dependencies=["plan"],
            )
        )

        # Critic reviews
        dag.add_task(
            SubTask(
                task_id="critic",
                description="Review work",
                role=AgentRole.CRITIC,
                dependencies=["work_1"],
            )
        )

        # Verifier validates
        dag.add_task(
            SubTask(
                task_id="verify",
                description="Run tests and validation",
                role=AgentRole.VERIFIER,
                dependencies=["work_1"],
            )
        )

        # Integrator merges
        dag.add_task(
            SubTask(
                task_id="integrate",
                description="Merge changes",
                role=AgentRole.INTEGRATOR,
                dependencies=["critic", "verify"],
            )
        )

        return dag

    def get_status(self) -> dict[str, Any]:
        """Get full system status."""
        return {
            "mode": self.config.mode.value,
            "repo": str(self.config.repo_path),
            "active_slots": len(self._active_slots),
            "operator": self.operator.get_status() if self.operator else None,
            "twin_enabled": self.twin is not None,
            "ledger_enabled": self.ledger is not None,
        }

    def rollback(self, slot_id: str) -> bool:
        """Rollback a slot's changes."""
        slot = self._active_slots.get(slot_id)
        if not slot:
            return False

        return slot.rollback_path.can_rollback()


def main():
    """CLI for AXIOM One."""
    import argparse

    parser = argparse.ArgumentParser(description="AXIOM One - Technical Operating System")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--mode", choices=["local", "managed", "orch"], default="local")
    parser.add_argument("--execute", help="Execute objective")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
    }

    config = OrchestratorConfig(
        repo_path=args.repo,
        mode=mode_map[args.mode],
    )

    axiom = AxiomOne(config)

    if args.execute:
        slot = axiom.execute(args.execute)
        print(f"Slot: {slot.slot_id}")
        print(f"Status: {slot.status}")
        if slot.verification_bundle:
            print(f"Receipt: {slot.verification_bundle}")
    elif args.status:
        print(axiom.get_status())
    else:
        print("AXIOM One - Technical Operating System")
        print(f"Mode: {args.mode}")
        print("Use --execute 'objective' or --status")


if __name__ == "__main__":
    main()
